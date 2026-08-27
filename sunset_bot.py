from curses.ascii import isdigit
import threading

import discord
from discord.ext import commands
from python_on_whales import docker


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

def bot_launch():
    bot.run(tok.read())

def server_launch(number):
    docker.compose.up([f'server_{number}'],build=True,force_recreate=True)

#remember to join launch threads as it is captured
def server_exit(number):
    docker.compose.down([f'server_{number}'])
    docker.compose.up([f'cleanup_{number}'])
    docker.compose.down([f'cleanup_{number}'])
#runs discord bot
#botThread = threading.Thread(target=bot_launch)

#could be more compact w a for loop
#thread is captured on launch
tl0 = threading.Thread(target=server_launch,args=('0',))
tl1 = threading.Thread(target=server_launch,args=('1',))
tl2 = threading.Thread(target=server_launch,args=('2',))
tl3 = threading.Thread(target=server_launch,args=('3',))

#te1 = threading.Thread(target=server_exit,args=('0',))
#te2 = threading.Thread(target=server_exit,args=('1',))
#te3 = threading.Thread(target=server_exit,args=('2',))
#te4 = threading.Thread(target=server_exit,args=('3',))

#captured thread list
capturedList = [tl0, tl1, tl2, tl3]

bot = commands.Bot(command_prefix='!', intents=intents)

#reads token.txt
tok = open("token.txt", "r")






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
            a = int(args[0])

            await ctx.send(f'placeholder launching screen: server {a} ')
            #launches servelet using compose API instead of raw command like v3
            #docker.compose.up([f'server_{args[0]}'])
            if -1 < a < 4:
                t = capturedList[a]

                t.start()
            else:
                await ctx.send('invalid server number. 0-3')

        else:
            await ctx.send('invalid server number, please only input numbers.')

    else:
        await ctx.send('invalid launch command, too many arguments')


@bot.command()
async def exit(ctx, *args):
    if len(args) < 1:
        await ctx.send(f'placeholder exit panel ')


    elif len(args) == 1:
        # TODO: needs to verify if valid number
        if isdigit(args[0]):
            a = int(args[0])

            await ctx.send(f'placeholder exit screen: server {a} ')
            # launches servelet using compose API instead of raw command like v3
            # docker.compose.up([f'server_{args[0]}'])

            if -1 < a < 4:
                t = capturedList[a]

                # THE ORDER IS IMPORTANT
                # docker compose down stops the container, which frees up the thread running foundry
                docker.compose.down(f'server_{a}')
                t.join()

                docker.compose.up([f'cleanup_{a}'])
                docker.compose.down([f'cleanup_{a}'])

            else:
                await ctx.send('invalid server number. 0-3')

        else:
            await ctx.send('invalid server number, please only input numbers.')

    else:
        await ctx.send('invalid exit command, too many arguments')



#botThread.start()
#botThread.join()
bot.run(tok.read())
