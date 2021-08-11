# bot.py
import discord
import aiohttp
import time


# local imports
import secret
import emoji
from apiClient import userData, userRecord, userStream, leaderBoard

import pymysql
from discord.ext import commands, tasks
from itertools import cycle
from io import BytesIO
from datetime import datetime, timedelta

client = commands.Bot(command_prefix="!")
client.remove_command('help')
playing_list = cycle(['!info userID', 'made by Phily', '!match userID'])

@tasks.loop(seconds=3)
async def change_status():
    await client.change_presence(activity=discord.Game(next(playing_list)))


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    change_status.start()

def save_user(discord_id, userName):
    conn = pymysql.connect(host="localhost", user="root", db="tetrio_bot", password=secret.dbPassword, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    try:
        sql = f"INSERT INTO users(discord_id, user_name) VALUES({discord_id}, '{userName}')"
        cur.execute(sql)
        conn.commit()

    except:
        sql = f"UPDATE users SET user_name='{userName}' WHERE discord_id={discord_id}"
        cur.execute(sql)
        conn.commit()

    conn.close()

    return

#returns None if not found
def load_user(discord_id):
    conn = pymysql.connect(host="localhost", user="root", db="tetrio_bot", password=secret.dbPassword, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = f"SELECT user_name FROM users WHERE discord_id={discord_id}"
    cur.execute(sql)
    result = cur.fetchall()

    if len(result) == 0:
        return

    userName = result[0]['user_name'].lower()

    return userName

def get_my_color(client, channel):
    for member in channel.members:
        if client.user == member:
            color = member.color
            return color

#returns url
def get_avatar(user):
    avatarURL = "https://tetr.io/res/avatar.png"
    if ("avatar_revision" in user):
        avatarURL = f"https://tetr.io/user-content/avatars/{user['_id']}.jpg?rv={user['avatar_revision']}"

    return avatarURL

def longest_name(records):
    names = []
    for game in records:
        names.append(
            game["endcontext"][0]['user']['username']
        )
        names.append(
            game["endcontext"][1]["user"]["username"]
        )
    return len(max(names, key=len))


def is_owner():
    def is_owner_check(ctx):
        return ctx.message.author.id == 243590632180809728

    return commands.check(is_owner_check)


@client.command()
async def help(ctx):
    commands = f"**!help**					`봇 명령어 확인 (Prints this message)`\n"
    commands += f"**!info id**				`해당 플레이어 정보 출력 (Check user info)`\n"
    commands += f"**!match id**			`해당 플레이어 최근 10개 랭크게임 기록 출력 (Prints last 10 ranked game results)`\n"
    commands += f"**!top10**				`상위 랭킹 1위~10위 정보 출력 (기록업뎃 대략 10~15분) (prints top10 players)`\n\n"
    # commands += f"**!ratio id1 id2**	`플레이어1과 플레이어2사이 Glicko 를 비교하여 승률을 나타냅니다. (prints elo ratio between p1 and p2)`\n\n"
    commands += f"버그나 각종 명령어 추천받습니다. `phily#6360`를 찾아주세요.    `Special Thanks: cn#4157`"

    await ctx.send(commands)


@client.command()
@is_owner()
async def servers(ctx):
    servers = list(client.guilds)
    await ctx.send(f"Connected on {str(len(servers))} servers:")
    await ctx.send("\n".join(guild.name for guild in client.guilds))


@client.command()
@is_owner()
async def ratio(ctx, p1, p2=None):
    if p2 is None:
        p2 = p1
        p1 = load_user(ctx.author.id)

        if p1 is None:
            ctx.send("You are not registered yet. Please set with !set username. ")
            return

    player1 = await userData(p1)
    player2 = await userData(p2)

    diff = round(player1['data']['user']['league']['glicko'] -
                 player2['data']['user']['league']['glicko'])
    elo = round((1 / (1 + pow(10, (-diff / 400))) * 100), 2)

    results = f"**{p1.upper()}** has **{elo}%** winning chance against **{p2.upper()}** by Elo-Rating System."

    await ctx.send(results)


@client.command()
async def top10(ctx):
    json = await leaderBoard()
    data = json['data']['users']

    longest_name = 0
    for i in range(10):
        user = data[i]
        length = len(user['username'])
        if length > longest_name:
            longest_name = length

    result = f"**Tetr.io Top10 Leader Board**\n"
    result += f"`{'pos.': <6}{'name': <{longest_name}}TR        `<:transparent:856070148657119273><:transparent:856070148657119273><:transparent:856070148657119273>     `    Wins       APM       PPS       VS  `\n"
    for i in range(10):
        user = data[i]
        league = user['league']
        position = i + 1
        result += f"`#{position: <5}{user['username']: <{longest_name}}({str(round(league['rating'], 2))})` "
        result += f":flag_{data[i]['country'].lower()}:" if user['country'] != None else ":pirate_flag:"
        result += f"<:verified:852645231965896734>" if user['verified'] else "<:transparent:856070148657119273>"
        result += f"<:support:852644663457742848>" if 'supporter' in user else "<:transparent:856070148657119273>"
        result += f"    `{data[i]['league']['gameswon']}"
        result += f"({str(round((data[i]['league']['gameswon'] / data[i]['league']['gamesplayed']) * 100, 2))}%)"
        result += f"   {round(data[i]['league']['apm'], 1)}      {round(data[i]['league']['pps'], 1)}      {round(data[i]['league']['vs'], 1)}`"
        result += f"\n"

    await ctx.send(result)


@client.command()
async def set(ctx, userName=None):
    if userName is None:
        await ctx.send("Please enter the Tetr.io username. ")
        return

    userName = userName.lower()

    user_data = await userData(userName)

    if user_data['success'] == False:
        await ctx.send("User not found! ")
        return

    save_user(ctx.author.id, userName)

    user = user_data['data']['user']

    title = f"{ctx.author} successfully set!"

    avatarURL = get_avatar(user)

    description= f"**Tetrio name**: {userName}\n"

    color = get_my_color(client, ctx.message.channel)
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_thumbnail(url=avatarURL)
    
    await ctx.send(embed=embed)
    return


@client.command()
async def match(ctx, user=None):
    if user is None:
        user = load_user(ctx.author.id)

        if user is None:
            ctx.send("You are not registered yet. Please set with !set username. ")
            return

    json = await userStream(user)
    data = json['data']['records']
    result = "```diff\n"

    if (len(data) == 0):
        result += "- No match records"
    else:
        length = longest_name(data)
        result = "**" + user.upper() + "'s last " + str(len(data)) + " match results**\n"
        result += "```diff\n"

        for game in data:
            end = game['endcontext']
            # prefix = "- L "
            formatted_time = datetime.strptime(
                game['ts'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d / %H:%M:%S")
            if (end[0]['user']['username'] == user.lower()):
                # prefix = "+ W "
                result += f"+ W {end[0]['user']['username']}   {end[0]['wins']} - {end[1]['wins']}   {end[1]['user']['username']: <{length}} {formatted_time}\n"
            else:
                result += f"- L {end[1]['user']['username']}   {end[1]['wins']} - {end[0]['wins']}   {end[0]['user']['username']: <{length}} {formatted_time}\n"

            # result += f"{prefix}{end[0]['user']['username']: <{length}} {end[0]['wins']} - {end[1]['wins']} {end[1]['user']['username']: <{length}} {formatted_time}\n"

    result += "```"

    await ctx.send(result)


@client.command()
async def info(msg, userName=None):
    if userName is None:
        userName = load_user(msg.author.id)

        if userName is None:
            ctx.send("You are not registered yet. Please set with !set username. ")
            return

    user_data = await userData(userName)
    user_record = await userRecord(userName)

    userURL = "https://ch.tetr.io/u/" + userName

    user = user_data['data']['user']
    sprint = user_record['data']['records']['40l']['record']
    blitz = user_record['data']['records']['blitz']['record']
    emojiFlags = user['country']

    joinDate = datetime.strptime(
        user['ts'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")

    # check if user is exist
    if ("error" in user_data):
        embed_error = discord.Embed(
            title='No such user!', color=discord.Color.green())
        await msg.send(embed=embed_error)
        return

    # if the user has avatar on it or not
    avatarURL = get_avatar(user)

    if (user['league']['gamesplayed'] > 10):
        currRank = emoji.rank(user['league']['rank'])
        # raiting has been rounded up
        currRating = user['league']['rating']
        standing = user['league']['standing']
        standingLocal = user['league']['standing_local']
        pps = user['league']['pps']
        apm = user['league']['apm']
        vs = user['league']['vs']
        gpm = user['league']['vs'] * 0.6 - user['league']['apm']
    else:
        currRank = user['league']['rank'].upper()
        currRating = '-'
        standing = '-'
        standingLocal = '-'
        pps = '-'
        apm = '-'
        vs = '-'
        gpm = '-'

    if (blitz != None):
        blitz = f"{blitz['endcontext']['score']:,}"

    if (sprint == None):
        sprint = "None"
    else:
        sprint = sprint['endcontext']['finalTime']
        sprint = sprint / 1000
        m, s = divmod(sprint, 60)
        if (m > 0):
            sprint = f"{int(m)}:{s:.3f}"
        else:
            sprint = f"{s:.3f}"

    if (emojiFlags != None):
        emojiFlags = f":flag_{user['country'].lower()}:"
    else:
        emojiFlags = ":pirate_flag:"

    globeEmoji = ":globe_with_meridians:"
    userEmoji = emojiFlags + " " + userName.upper()
    badges = ""

    # check support, verified, and badges
    if ('verified' in user):
        if (user['verified'] == True):
            userEmoji += " <:verified:845092546979299328>"
    if ('supporter' in user):
        if (user['supporter'] == True):
            for i in range(user['supporter_tier']):
                userEmoji += " <:support:845092535206674501>"
    if (len(user['badges']) != 0):
        badges = emoji.badges(user['badges'])

    color = get_my_color(client, msg.message.channel)

    embed = discord.Embed(title=userEmoji,
                          color=color,
                          url=userURL)

    embed.set_author(name="Tetr.io",
                     icon_url="https://cdn.discordapp.com/emojis/676945644014927893.png?v=1")
    embed.set_thumbnail(url=avatarURL)
    embed.add_field(name="Tetra League",
                    value=f"{currRank} ({int(currRating)} TR) with {globeEmoji} {standing} / {emojiFlags} {standingLocal}",
                    inline=False)
    embed.add_field(name="Stats",
                    value=f"_**PPS**_ {pps:.2f}\n_**APM**_ {apm:.2f}\n_**VS**_ {vs:.2f}\n_**GPM**_ {gpm:.2f}",
                    inline=True)
    embed.add_field(name="Solo Records",
                    value=f"_**Sprint(40L)**_ {sprint}\n_**Blitz**_ {blitz}\n{badges}",
                    inline=True)
    embed.add_field(name="Played Since",
                    value=joinDate,
                    inline=False)

    await msg.send(embed=embed)

client.run(secret.TOKEN)
