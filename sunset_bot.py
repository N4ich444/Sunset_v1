from curses.ascii import isdigit
import threading

import discord
from discord.ext import commands
from discord.ext import tasks
from python_on_whales import docker

#still less lines of code then when we were under spring even thought this is a monolithic single python file


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
#num of active instances
activeInstances = 0
launchFlag = False
PORT = 0

def server_launch(number):
    docker.compose.up([f'server_{number}'],build=True,force_recreate=True)

#remember to join launch threads as it is captured
def server_exit(number):
    docker.compose.down([f'server_{number}'])
    docker.compose.up([f'cleanup_{number}'])
    docker.compose.down([f'cleanup_{number}'])
#runs discord bot
#botThread = threading.Thread(target=bot_launch)

def t_launcher(number):
    t = threading.Thread(target=server_launch, args=(number,))

    t.start()


class LaunchButtonPanel(discord.ui.View):

    def __init__(self, *, timeout=180):
        self.launchDisable = False
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Launch Server 0", style=discord.ButtonStyle.green)
    async def button_0(self, button: discord.ui.Button, interaction: discord.Interaction):
        #t_launcher(0)
        await interaction.response.edit_message(content=f"This is an edited button response!")

    @discord.ui.button(label="Launch Server 1", style=discord.ButtonStyle.green)
    async def button_1(self, button: discord.ui.Button, interaction: discord.Interaction):
        #t_launcher(1)
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

    print(f"Active Docker instances: {activeInstances}")

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
        await ctx.send(f'Launch a Server', view=LaunchButtonPanel())


    elif len(args) == 1:

        if isdigit(args[0]):
            a = int(args[0])


            #launches servelet using compose API instead of raw command like v3
            #docker.compose.up([f'server_{args[0]}'])
            # thread is captured on launch
            if -1 < a < 4:
                isLaunched = len(docker.ps(filters={('name',f'server_{a}')}))
                #t = threading.Thread(target=server_launch, args=(args[0],))

                #t.start()
                if isLaunched == 0:
                    link = f'{url}:{PORT + a}'
                    await ctx.send(f'Launching Server {a} with the link {link}. Please wait...')
                    t_launcher(args[0])
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
        await ctx.send(f'placeholder exit panel ')


    elif len(args) == 1:
        # TODO: needs to verify if valid number
        if isdigit(args[0]):
            a = int(args[0])

            await ctx.send(f'placeholder exit screen: server {a} ')
            # launches servelet using compose API instead of raw command like v3
            # docker.compose.up([f'server_{args[0]}'])

            if -1 < a < 4:
                isLaunched = len(docker.ps(filters={('name', f'server_{a}')}))

                if isLaunched > 0:
                    # THE ORDER IS IMPORTANT
                    # docker compose down stops the container, which frees up the thread running foundry
                    docker.compose.down(f'server_{a}')


                    docker.compose.up([f'cleanup_{a}'])
                    docker.compose.down([f'cleanup_{a}'])
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
    await ctx.send(f"{len(docker.ps())} {docker.ps()}")


#botThread.start()
#botThread.join()
bot.run(tok.read())
