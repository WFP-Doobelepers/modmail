import datetime
from discord.ext import commands
import os
import discord
from dotenv import load_dotenv
import pymongo


from core import checks
from core.thread import Thread
from core.models import DMDisabled, PermissionLevel, SimilarCategoryConverter, getLogger


load_dotenv()

url = os.getenv("CONNECTION_URI")
myclient = pymongo.MongoClient(url)
mydb = myclient["modmail_bot"]
mycol = mydb["drafts"]


class Draft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    @commands.command()
    @checks.thread_only()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def draft(self, ctx : commands.Context, *, draft : str = None):
        global mycol
        thread = {'_id': f'{ctx.channel.id}'}
        count = mycol.count_documents(thread)
        
        newdraft = {
            '_id' : f'{ctx.channel.id}',
            'draft' : f'{draft}',
            'approvals' : 0,
            'approve_users' : [],
            'sent' : False
        }

        if count == 1 :
            x = mycol.find_one({'_id' : f'{ctx.channel.id}'})
            if draft is None :
                if x['draft'] == 'None' :
                    embed = discord.Embed(title='Draft', description=f"There's no draft for this thread. set one by typing `+draft <The draft>`")
                    embed.timestamp = datetime.datetime.now()
                    embed.set_author(name =f"{ctx.author} ({ctx.author.id})", icon_url=f"{ctx.author.display_avatar}")         
                    embed.color = 0x7BB6F3
                    await ctx.send(embed=embed)
                    
                else:
                    appr = f'Current approvals : **{x["approvals"]}**'

                    embed = discord.Embed(title='Draft', description=f"The draft for this thread\n**{x['draft']}**")
                    embed.timestamp = datetime.datetime.now()
                    embed.set_author(name =f"{ctx.author} ({ctx.author.id})", icon_url=f"{ctx.author.display_avatar}")         
                    embed.color = 0x7BB6F3
                    await ctx.send(appr, embed=embed)
            else :
                
                newdraft = { "$set": {"draft" : f'{draft}'}}
                mycol.update_one(thread, newdraft)
                embed = discord.Embed(title='Draft', description=f"You have set a draft for this thread\n**{draft}**")
                embed.set_author(name =f"{ctx.author} ({ctx.author.id})", icon_url=f"{ctx.author.display_avatar}")         
                embed.timestamp = datetime.datetime.now()
                embed.color = 0x7BB6F3
                await ctx.send(embed=embed)
        else :
            if draft is None :
                mycol.insert_one(newdraft)
                embed = discord.Embed(title='Draft', description=f"There's no draft for this thread. set one by typing `+draft <The draft>`")
                embed.timestamp = datetime.datetime.now()
                embed.set_author(name =f"{ctx.author} ({ctx.author.id})", icon_url=f"{ctx.author.display_avatar}")         
                embed.color = 0x7BB6F3
                await ctx.send(embed=embed)
            
            else :
                mycol.insert_one(newdraft)
                
                appr = f'Current approvals : **{x["approvals"]}**'
                
                embed = discord.Embed(title='Draft', description=f"You have set a draft for this thread\n**f'{draft}**")
                embed.timestamp = datetime.datetime.now()
                embed.color = 0x7BB6F3
                embed.set_author(name =f"{ctx.author} ({ctx.author.id})", icon_url=f"{ctx.author.display_avatar}")         
                await ctx.send(appr, embed=embed)

    @commands.command()
    @checks.thread_only()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def draftapprove(self, ctx : commands.Context):
        global mycol

        thread = {'_id': f'{ctx.channel.id}'}
        count = mycol.count_documents(thread)

        if count == 1 :
            x = mycol.find_one(thread)
            if ctx.author.id not in x['approve_users']:
            
                full_approvals = x['approvals'] + 1
                newapprove = { "$set": {"approvals" : full_approvals}}
                newapproval = { "$push" : {'approve_users' : ctx.author.id}}
                mycol.update_one(thread, newapprove)
                mycol.update_one(thread, newapproval)
                await ctx.send(f'You have successfully approve this draft.\nCurrent approvals : {x["full_approvals"]}')
            else :
                await ctx.send('You have already approve this draft!')
        else :
            await ctx.send('This thread does not contain draft')

    @commands.command()
    @checks.thread_only()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def senddraft(self, ctx : commands.Context):
        global mycol
        thread = {'_id': f'{ctx.channel.id}'}
        x = mycol.find_one(thread)
        if x['approvals'] >= 2 :
            ctx.message.content = x['draft']
            async with ctx.typing():
                await ctx.thread.reply(ctx.message)
               
                sent = { "$set": { "sent": True } }
                mycol.update_one(thread, sent)
                await ctx.send('Draft was sent successfully')

        else :
            await ctx.send('This draft does not have enough approvals!')
            

def setup(bot): 
    bot.add_cog(Draft(bot)) 
              