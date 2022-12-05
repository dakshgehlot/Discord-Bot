import os
import datetime
import json
import random
import urllib
import base64
import discord
import requests
from discord.ext import tasks, commands
from discord.ext.commands import has_permissions, MissingPermissions, has_any_role, MissingRequiredArgument, MissingRole
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.guilds = True
load_dotenv()
client = commands.Bot(command_prefix="$", intents=intents)

# Variables
games = ["Lost in Space", "How's the Josh!?"]
help_info = [
    "**COMMANDS**\n\n'$hey' TO GET A 'Hello'\n\n$inspire' TO GET RANDOM QUOTE\n\n'$date' TO GET CURRENT DATE\n\n'$meme' TO GET A MEME\n\n\
'$github' TO SEARCH ACCOUNT ON GITHUB\n\n'joke' TO GET RANDOM JOKE\n\n'$clear <amount>' TO CLEAR MESSAGE \n\n'$bday <name>' TO GET A BIRTHDAY MESSAGE\n\n\
'$members <role>' TO GET A LIST OF MEMBERS HAVING THE SPECIFIED ROLE\n\n'$projects' TO GET CURRENT ACTIVE PROJECTS\n\n\
'$dot_data' TO GET SERVER STATUS"
]


# Function to get random quote
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")  # random api to get a random quote
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " \n-" + json_data[0]['a']
    return quote


# Function to return GitHub account
def github_search_user(user_name):
    response = urllib.request.urlopen("https://api.github.com/users/" + user_name)
    data = json.loads(response.read())

    github_url = data["html_url"]
    repo = str(data["public_repos"])
    num_follower = str(data["followers"])
    num_following = str(data["following"])

    github_resource = [github_url, num_follower, num_following, repo]
    return github_resource


# Function to return random joke
def random_joke():
    url = "https://some-random-api.ml/joke"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    joke = data["joke"]
    return joke


# Function to return random joke
def random_meme():
    url = "https://some-random-api.ml/meme"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    meme = data["image"]
    return meme


# Function to return active projects
def active_projects():
    url = "https://api.github.com/repos/dot-space/dot-bot/contents/active_projects.txt"
    url_handle = urllib.request.urlopen(url)
    data = url_handle.read().decode()
    js = json.loads(data)
    content = js['content']
    content = base64.b64decode(content)
    decoded_content = content.decode('ascii')
    return decoded_content


# Created login message
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online)
    await client.wait_until_ready()
    bot_status.start()
    print("Bot is ready!!")


# Task is looped which change the status of bot frequently
@tasks.loop(seconds=60)
async def bot_status():
    await client.change_presence(activity=discord.Game(random.choice(games)))


# Gives welcome message when someone joins the server
@client.event
async def on_member_join(member):
    channel = client.get_channel(979107875408470016)
    embed = discord.Embed(title=f"Welcome {member.name}", description=f"Thanks for joining {member.guild.name}!")
    embed.set_thumbnail(url=member.avatar_url)
    await channel.send(embed=embed)


# Gives goodbye message when someone leaves the server
@client.event
async def on_member_remove(member):
    channel = client.get_channel(979107875408470016)
    embed = discord.Embed(title=f"Good bye {member.name}!!", description=f"I was such a pleasure to meet you :pray: ")
    await channel.send(embed=embed)


# Error handler
@client.event
async def on_command_error(ctx, error):
    # Trigger when Argument is missing in any command
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Please pass all required arguments")
    # Trigger when Permission is missing
    elif isinstance(error, MissingPermissions):
        await ctx.send("You don't have Required Permission...")
    # Trigger when Role is missing
    elif isinstance(error, MissingRole):
        await ctx.send("Please Contact Admin to give Access to perform this task")


# Command to return "hello"
@client.command()
async def hey(ctx):
    hello = 'Hello '
    user = hello + ctx.message.author.mention + '!!! 😄'
    await ctx.send(user)


#command to return random quotes
@client.command()
async def inspire(ctx):
    quote = get_quote()
    await ctx.send(quote)


# Command to return "Happy Birthday!"
@client.command()
async def bday(ctx, message):
    await ctx.send(f"Happy Birthday {message}! 🎈🎉")


# Command to get the current date
@client.command()
async def date(ctx):
    emd_msg = discord.Embed(title="Date & Time", color=0x00ff00)
    time = datetime.datetime.now().strftime("%H:%M:%S")
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    emd_msg.add_field(name="Date", value=f"{date}", inline=True)
    emd_msg.add_field(name="Time", value=f"{time}")
    await ctx.send(embed=emd_msg)


# Command to return random jokes
@client.command()
async def joke(ctx):
    joke = random_joke()
    await ctx.send(joke)


# Command to return random meme
@client.command()
async def meme(ctx):
    meme = random_meme()
    await ctx.send(meme)


# Command to send command info
@client.command()
async def commands(ctx):
    await ctx.send(''.join(help_info))


# Command to send
@client.command()
async def github(ctx, member):
    github_result = github_search_user(member)
    await ctx.send(
        github_result[0] + "\nFollowers: " + github_result[1] + ",  Following: " + github_result[2] + ",  Public Repo: " +
        github_result[3])


# Command to clear messages
@client.command()
async def clear(ctx, amount):
    amt = int(amount) + 1
    await ctx.channel.purge(limit=amt)


# Command to kick member
@client.command()
@has_permissions(kick_members=True)
@has_any_role('Lead', 'Mod', 'Head')
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member.mention} \n\nReason: {reason}")


# Command to ban member
@client.command()
@has_permissions(ban_members=True)
@has_any_role('Lead', 'Mod', 'Head')
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member.mention}")


# Command to send invite link
@client.command(pass_context=True)
async def invite(ctx):
    link = await ctx.channel.create_invite(max_use=2)
    await ctx.send(link)


# Command to unban member
@client.command()
async def unban(ctx, *, member):
    banned_user = await ctx.guild.bans()
    member_name, member_disc = member.split("#")

    for ban_entry in banned_user:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_disc):
            await ctx.guild.unban(user)
            await ctx.send(f"unban {user.mention}#{user.discriminator}")

        return


# Command that returns active projects
@client.command()
async def projects(ctx):
    all_projects = active_projects()
    await ctx.send(f"{all_projects}")
    

# Command that returns current members of the provided role
@client.command()
async def members(ctx, role: discord.Role):
    member_list = role.members
    final_list = list()
    for member in member_list:
        final_list.append("{0.name}#{0.discriminator}".format(member))
    await ctx.send("\n".join(final_list))
    

# Command that returns server status
@client.command()
async def dot_data(ctx):
    offline = 0
    online = 0
    idle = 0
    for member in ctx.guild.members:  # .members was added

        if member.status == discord.Status.offline:
            offline += 1
        elif member.status == discord.Status.online:
            online += 1
        else:
            idle += 1
    embed = discord.Embed(title=ctx.guild.name + " Stats", color=0x000)
    embed.add_field(name="Member Count", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Online", value=f"{online} :green_circle:", inline=True)
    embed.add_field(name="Offline", value=f"{offline} :red_circle:", inline=True)
    embed.add_field(name="Idle", value=f"{idle} :yellow_circle:", inline=True)
    await ctx.send(embed=embed)
    await ctx.message.delete()


# @client.command()
# @has_permissions(manage_channels=True)
# async def lock(ctx, channel: discord.TextChannel = None):
#     overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
#     overwrite.send_messages = False
#     await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
#     await ctx.send('Channel locked.')


# @client.command()
# @has_permissions(manage_channels = True)
# async def lock(ctx, channel: discord.TextChannel = None):
#     channel = channel or ctx.channel

#     if ctx.guild.default_role not in channel.overwrites:
#         overwrites = {
#             ctx.guild.default_role: discord.PermissionOverwrite(send_messages = False)
#         }
#         await channel.edit(overwrites = overwrites)
#         await ctx.send(f"Channel lockdown initiated.") 


# @client.command()
# @has_permissions(manage_channels=True)
# async def unlock(ctx, channel: discord.TextChannel = None):
#     overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
#     overwrite.send_messages = True
#     await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
#     await ctx.send('Channel unlocked.')

###################################################################

# keep_alive()
bot = os.getenv("Token")
client.run(bot)
