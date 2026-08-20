from curses.ascii import isdigit
from unicodedata import numeric

import discord
from discord.ext import commands
from python_on_whales import docker


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

#reads token.txt
tok = open("token.txt", "r")

class ControlPanel(discord.ui.ActionRow):

    @discord.ui.button(label='Click Me!')
    async def click_me(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('You clicked me!')




@bot.event
async def on_ready():
    # Tell the type checker that User is filled up at this point
    assert bot.user is not None

    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

#TODO: switch to hybrid_command once fully done
@bot.command()
async def launch(ctx, *args):


    if len(args) < 1:
        await ctx.send(f'placeholder launch panel ')


    elif len(args) == 1:
        #TODO: needs to verify if valid number
        if isdigit(args[0]):
            await ctx.send(f'placeholder launching screen: server {args[0]} ')
            #launches serverlet using compose API instead of raw command like v3
            docker.compose.up([f'server_{args[0]}'])
        else:
            await ctx.send('invalid server number. 1-4')

    else:
        await ctx.send('invalid launch command, too many arguments')


@bot.command()
async def exit(ctx, *args):


    if len(args) < 1:
        await ctx.send(f'placeholder launch panel ')


    elif len(args) == 1:
        # TODO: needs to verify if valid number
        if isdigit(args[0]):
            await ctx.send(f'placeholder launching screen: server {args[0]} ')
            # launches serverlet using compose API instead of raw command like v3
            docker.compose.down([f'server_{args[0]}'])
            docker.compose.up([f'cleanup_{args[0]}'])
            docker.compose.down([f'cleanup_{args[0]}'])
        else:
            await ctx.send('invalid server number. 1-4')

    else:
        await ctx.send('invalid launch command, too many arguments')


bot.run(tok.read())


