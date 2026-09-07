from curses.ascii import isdigit
import threading

import discord
from discord.ext import commands
from discord.ext import tasks
from python_on_whales import docker

#Alan Kuang 2026
#still less lines of code then when we were under spring even thought this is a monolithic single python file


"""
most of the documentation I used can be found on 
https://discordpy.readthedocs.io/en/stable/index.html, 
https://gabrieldemarmiesse.github.io/python-on-whales/
https://docs.docker.com/
"""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
#num of active instances
activeInstances = 0

PORT = 0
globalStatus = [False,False,False,False]

"""Helpers and other things"""

#TODO: make it so that it does not have to force create every time
def server_launch(number):
    docker.compose.up([f'server_{number}'],build=True,force_recreate=True)

def update_status(number):
    s = len(docker.ps(filters={('name',f'server_{number}')}))
    if s > 0:
        globalStatus[number] = True
    else:
        globalStatus[number] = False

def thread_launcher(number):
    #raise Exception("This is a test Error!")

    t = threading.Thread(target=server_launch, args=(number,))

    t.start()

#TODO: buttons
class LaunchButtonPanel(discord.ui.View):

    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Launch Server 0", style=discord.ButtonStyle.green)
    async def button_0(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.disabled = True
        link = f'{url}:{PORT}'
        await interaction.response.edit_message(content=f"Launching Server 0 with the link {link}. Please wait...")
        thread_launcher(0)


    @discord.ui.button(label="Launch Server 1", style=discord.ButtonStyle.green)
    async def button_1(self, button: discord.ui.Button, interaction: discord.Interaction):
        #t_launcher(1)
        button.disabled = True
        await interaction.response.edit_message(content=f"This is an edited button response!")

    @discord.ui.button(label="Launch Server 2", style=discord.ButtonStyle.green)
    async def button_2(self, button: discord.ui.Button, interaction: discord.Interaction):
        #t_launcher(2)
        await interaction.response.edit_message(content=f"This is an edited button response!")

    @discord.ui.button(label="Launch Server 3", style=discord.ButtonStyle.green)
    async def button_3(self, button: discord.ui.Button, interaction: discord.Interaction):
        #t_launcher(3)
        await interaction.response.edit_message(content=f"This is an edited button response!")


bot = commands.Bot(command_prefix='!', intents=intents)

#reads token.txt
tok = open("token.txt", "r")

#channel id that messages will be sent
channelID = open("channelID.txt", "r")
usableCID = int(channelID.read())

urlFile = open("url.txt", "r")
url = urlFile.read()

portFile = open("port.txt", "r")
PORT = int(portFile.read())

"""Bot stuff starts here"""

@bot.event
async def on_ready():
    # Tell the type checker that User is filled up at this point
    assert bot.user is not None

    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

#tapping into the setup hook
@bot.event
async def setup_hook() -> None:
    instance_monitor.start()

#monitors docker instances

@tasks.loop(seconds=30)
async def instance_monitor():
    global activeInstances
    #checks all server instances
    instanceList = docker.ps(filters={('name', 'server_')})
    currentInstances = len(instanceList)
    for i in range(0, 4):
        update_status(i)

    print(f"Active Docker instances: {activeInstances}\n Status: {globalStatus}")

    if currentInstances > activeInstances:
        channel = bot.get_channel(usableCID)
        await channel.send('Server Launched Successfully!')




    activeInstances = currentInstances

@instance_monitor.before_loop
async def wait_login():
    await bot.wait_until_ready()


#TODO: switch to hybrid_command once fully done
@bot.command()
async def launch(ctx, *args):


    if len(args) < 1:
        #for i in range(0, 4):
            #update_status(i)

        await ctx.send(f'buttons are not supported yet')


    elif len(args) == 1:

        if isdigit(args[0]):
            a = int(args[0])


            # launches servelet using compose API instead of raw command like v3
            # thread is captured on launch
            if -1 < a < 4:
                isLaunched = len(docker.ps(filters={('name',f'server_{a}')}))


                #t.start()
                if isLaunched == 0:
                    link = f'{url}:{PORT + a}'
                    await ctx.send(f'Launching Server {a} with the link {link}. Please wait...')
                    try:
                        thread_launcher(args[0])
                    except Exception as e:
                        #channel = bot.get_channel(usableCID)
                        await ctx.send(f'Error launching Server {a}!\nDetails: ||{e}||')

                else:
                    await ctx.send(f'Server {a} has already been launched')




            else:
                await ctx.send(f'Invalid Server number {a}. Valid range: 0-3')

        else:
            await ctx.send('Invalid Server number. please only input numbers.')

    else:
        await ctx.send('Invalid Launch command. too many arguments')


@bot.command()
async def exit(ctx, *args):
    if len(args) < 1:
        await ctx.send(f'buttons are not supported yet')



    elif len(args) == 1:
        # TODO: needs to verify if valid number
        if isdigit(args[0]):
            a = int(args[0])


            # launches servelet using compose API instead of raw command like v3
            # docker.compose.up([f'server_{args[0]}'])

            if -1 < a < 4:
                #checks if server is still alive
                isLaunched = len(docker.ps(filters={('name', f'server_{a}')}))

                if isLaunched > 0:
                    await ctx.send(f'Shutting down Server {a} ')
                    # THE ORDER IS IMPORTANT
                    # docker compose down stops the container, which frees up the thread running foundry
                    try:
                        docker.compose.down(f'server_{a}')


                        docker.compose.up([f'cleanup_{a}'],build=True,force_recreate=True)
                        docker.compose.down([f'cleanup_{a}'])

                        isShutDown = len(docker.ps(filters={('name', f'server_{a}')}))
                        isCleanedUp = len(docker.ps(filters={('name', f'cleanup_{a}')}))
                        if isCleanedUp == 0 and isShutDown == 0:
                            await ctx.send(f'Server {a} has successfully shutdown')
                        elif isCleanedUp > 0 and isShutDown == 0:
                            await ctx.send(f'WARNING! The cleanup service for Server {a} is still running! Manual intervention/Emergency shutdown is required.')
                        else:
                            await ctx.send(f'WARNING! Server {a} has not shutdown successfully. Manual intervention/Emergency shutdown is required.')
                    except Exception as e:
                        await ctx.send(f'Error shutting down Server {a}!\nDetails: ||{e}||')
                else:
                    await ctx.send(f'Server {a} is not running')

            else:
                await ctx.send(f'Invalid Server number {a}. Valid range: 0-3')

        else:
            await ctx.send('Invalid Server number. please only input numbers.')

    else:
        await ctx.send('Invalid Exit command. too many arguments')

@bot.command()
async def status(ctx):
    for i in range(0, 4):
        update_status(i)
    s = ""
    ctr = 0
    for b in globalStatus:
        if b:
            s = s + f'Server {ctr}: Online\n'
        else:
            s = s + f'Server {ctr}: Offline\n'
        ctr += 1

    await ctx.send(f'{s}Details: ||{docker.ps()}||')

    #await ctx.send(f"{len(docker.ps())} {docker.ps()}")

@bot.command()
async def emergency_shutdown(ctx):
    #channel = bot.get_channel(usableCID)
    await ctx.send(f'Emergency Shutdown activated by user {ctx.message.author.mention}. Killing all Docker containers. Misuse will be punished.')
    try:
        for i in range(0,4):
            docker.compose.kill([f'cleanup_{i}'])
        for i in range(0,4):
            docker.compose.kill([f'server_{i}'])



        await ctx.send(f'Emergency shutdown completed!')

    except Exception as e:
        await ctx.send(f'Error shutting down!\n Details: ||{e}||')


#botThread.start()
#botThread.join()
bot.run(tok.read())
