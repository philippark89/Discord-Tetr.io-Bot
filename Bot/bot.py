# bot.py
import discord
import aiohttp
import time
import secret
from discord.ext import commands, tasks
from itertools import cycle
from selenium import webdriver
from PIL import Image
from io import BytesIO
from datetime import datetime

client = commands.Bot(command_prefix=">")
client.remove_command('help')
playing_list = cycle(['!info userID', 'made by Seoul', '!match userID'])


def rankEmojis(rank):
    if (rank == "x"):
        return "<:rankX:845092185052413952>"
    elif (rank == "u"):
        return "<:rankU:845092171438882866>"
    elif (rank == "ss"):
        return "<:rankSS:845092157139976192>"
    elif (rank == "s+"):
        return "<:rankSplus:845092140471418900>"
    elif (rank == "s"):
        return "<:rankS:845092120662376478>"
    elif (rank == "s-"):
        return "<:rankSminus:845092009101230080>"
    elif (rank == "a+"):
        return "<:rankAplus:845091973248581672>"
    elif (rank == "a"):
        return "<:rankA:845091931994587166>"
    elif (rank == "a-"):
        return "<:rankAminus:845091885286424596>"
    elif (rank == "b+"):
        return "<:rankBplus:845091818911301634>"
    elif (rank == "b"):
        return "<:rankB:845089923089825812>"
    elif (rank == "b-"):
        return "<:rankBminus:845089882698154044>"
    elif (rank == "c+"):
        return "<:rankCplus:845088318509285416>"
    elif (rank == "c"):
        return "<:rankC:845088262611533844>"
    elif (rank == "c-"):
        return "<:rankCminus:845088252322775041>"
    elif (rank == "d+"):
        return "<:rankD:845088198966640640>"
    elif (rank == "d"):
        return "<:rankDplus:845088230588284959>"
    elif (rank == "z"):
        return "<:unranked:845092197346443284>"


def badgeEmoji(json):
    badgeEmojis = []
    badges = ""
    for i in range(len(json)):
        badgeEmojis.append(json[i]['id'])

    for x in range(len(badgeEmojis)):
        if ("leaderboard1" == badgeEmojis[x]):
            badges += "<:zRank1:847188809907961886>"
        elif ("infdev" == badgeEmojis[x]):
            badges += "<:zINF:847189521899454505>"
        elif ("allclear" == badgeEmojis[x]):
            badges += "<:zPC:847188524247285771>"
        elif ("kod_founder" == badgeEmojis[x]):
            badges += "<:zKOD:847188743680557146>"
        elif ("secretgrade" == badgeEmojis[x]):
            badges += "<:zSG:847188855865868338>"
        elif ("20tsd" == badgeEmojis[x]):
            badges += "<:z20tsd:847188471633674270>"
        elif ("superlobby" == badgeEmojis[x]):
            badges += "<:zHDSL:847190320986325034>"
        elif ("early-supporter" == badgeEmojis[x]):
            badges += "<:zES:847188570769850380>"
        elif ("100player" == badgeEmojis[x]):
            badges += "<:zSL:847188404163837953>"

    return badges


@tasks.loop(seconds=3)
async def change_status():
    await client.change_presence(activity=discord.Game(next(playing_list)))


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    change_status.start()


async def userData(user):
    async with aiohttp.ClientSession() as session:
        user = user.lower()
        URL = 'https://ch.tetr.io/api/users/' + user
        request = await session.get(URL)
        json = await request.json()

    return json


async def userRecord(user):
    async with aiohttp.ClientSession() as session:
        user = user.lower()
        URL = 'https://ch.tetr.io/api/users/' + user + "/records"
        request = await session.get(URL)
        json = await request.json()

    return json


async def leaderBoard():
    async with aiohttp.ClientSession() as session:
        URL = "https://ch.tetr.io/api/users/lists/league"
        request = await session.get(URL)
        json = await request.json()

    return json


async def userStream(user):
    async with aiohttp.ClientSession() as session:
        id = await userData(user.lower())
        URL = "https://ch.tetr.io/api/streams/league_userrecent_" + \
            id['data']['user']['_id']
        request = await session.get(URL)
        json = await request.json()

    return json


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


@client.command()
async def help(ctx):
    commands = f"**!help**					`봇 명령어 확인 (Prints this message)`\n"
    commands += f"**!info id**				`해당 플레이어 정보 출력 (Check user info)`\n"
    commands += f"**!match id**			`해당 플레이어 최근 10개 랭크게임 기록 출력 (Prints last 10 ranked game results)`\n"
    commands += f"**!top10**				`상위 랭킹 1위~10위 정보 출력 (기록업뎃 대략 10~15분) (prints top10 players)`\n"
    commands += f"**!ratio id1 id2**	`플레이어1과 플레이어2사이 Glicko 를 비교하여 승률을 나타냅니다. (prints elo ratio between p1 and p2)`\n\n"
    commands += f"버그나 각종 명령어 추천받습니다. 채널내 `@SEOUL` 또는 `phily#6360`를 찾아주세요.    `Special Thanks: cn#4157, 시아미즈#0001`"

    await ctx.send(commands)


@client.command()
async def ratio(ctx, p1, p2):
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
async def match(ctx, user):
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


# @client.command()
# async def test(ctx, user):
# 	json = await userData(user)
# 	url = "https://ch.tetr.io/s/league_userrecent_" + json['data']['user']['_id']
# 	options = webdriver.ChromeOptions()
# 	options.add_argument('--headless')
# 	driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options=options)
# 	driver.set_window_size(1120,2000)
# 	driver.get(url)

# 	rows = driver.find_elements_by_xpath("//table/tbody/tr")
# 	str = ""
# 	for i in rows:
# 		str += i.text + "\n"

# 	await ctx.send(str)

# @client.command()
# async def rank(ctx, user):
# 	url = "https://ch.tetr.io/u/" + user
# 	options = webdriver.ChromeOptions()
# 	options.add_argument('--headless')
# 	driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options=options)
# 	driver.set_window_size(1120,2000)
# 	driver.get(url)
# 	time.sleep(1)
# 	# element = driver.find_element_by_id("usercard_league")
# 	# element.screenshot('rank.png')
# 	checking = driver.find_element_by_id("error_title")
# 	if (checking.text == "No such user!"):
# 		element = driver.find_element_by_id("error")
# 		element.screenshot('rank.png')

# 		im = Image.open(r"rank.png")
# 		w, h = im.size

# 		crop = im.crop((100, 235, 780, 479)) # left, top, right, bottom ((x1, y1, x2, y2))
# 		crop.save("rank.png")
# 	else:
# 	    element = driver.find_element_by_id("usercard_league")
# 	    element.screenshot('rank.png')

# 	driver.close()

# 	await ctx.send(file=discord.File('rank.png'))

@client.command()
async def info(msg, user):
    async with aiohttp.ClientSession() as session:
        user = user.lower()
        URL = 'https://ch.tetr.io/api/users/' + user
        request = await session.get(URL)
        tetJson = await request.json()

        URLr = URL + "/records"
        request_r = await session.get(URLr)
        recordJson = await request_r.json()

        emojiTetrio = "https://cdn.discordapp.com/emojis/676945644014927893.png?v=1"
        globeEmoji = ":globe_with_meridians:"

    if ("error" in tetJson):
        embed_error = discord.Embed(
            title='No such user!', color=discord.Color.green())
        await msg.send(embed=embed_error)
    else:
        userURL = "https://ch.tetr.io/u/" + user

        # if the user has avatar on it or not
        if ("avatar_revision" in tetJson['data']['user']):
            avatarURL = "https://tetr.io/user-content/avatars/" + \
                str(tetJson['data']['user']['_id']) + ".jpg?rv=" + \
                str(tetJson['data']['user']['avatar_revision'])
        else:
            avatarURL = "https://tetr.io/res/avatar.png"

        if (tetJson['data']['user']['league']['gamesplayed'] > 10):
            currRank = rankEmojis(tetJson['data']['user']['league']['rank'])
            # raiting has been rounded up
            currRating = str(
                int(round(tetJson['data']['user']['league']['rating'])))
            standing = str(tetJson['data']['user']['league']['standing'])
            standingLocal = str(
                tetJson['data']['user']['league']['standing_local'])
            pps = str("{:.2f}".format(
                tetJson['data']['user']['league']['pps']))
            apm = str("{:.2f}".format(
                tetJson['data']['user']['league']['apm']))
            vs = str("{:.2f}".format(tetJson['data']['user']['league']['vs']))
            gpm = str("{:.2f}".format(
                (tetJson['data']['user']['league']['vs'] * 0.6) - tetJson['data']['user']['league']['apm']))
        else:
            currRank = tetJson['data']['user']['league']['rank'].upper()
            currRating = '-'
            standing = '-'
            standingLocal = '-'
            pps = '-'
            apm = '-'
            vs = '-'
            gpm = '-'

        joinDate = str(tetJson['data']['user']['ts'])[:10]
        record40 = recordJson['data']['records']['40l']['record']
        blitzScore = recordJson['data']['records']['blitz']['record']
        emojiFlags = tetJson['data']['user']['country']

        if (blitzScore != None):
            blitzScore = recordJson['data']['records']['blitz']['record']['endcontext']['score']

        if (record40 == None):
            record40 = "None"
        else:
            record40 = round(
                recordJson['data']['records']['40l']['record']['endcontext']['finalTime'])
            decimal = str(record40)[-3:]
            secs = str(record40)[:-3]
            if (int(secs) >= 60):
                mins = int(int(secs) / 60)
                sec = int(secs) % 60
                record40 = str(mins) + ":" + str(sec) + "." + str(decimal)
            else:
                record40 = secs + "." + decimal

        if (emojiFlags != None):
            emojiFlags = ":flag_" + \
                tetJson['data']['user']['country'].lower() + ":"
        else:
            emojiFlags = ":pirate_flag:"

        user = emojiFlags + " " + user.upper()
        badges = " "

        # check support, verified, and badges
        if ('verified' in tetJson['data']['user']):
            if (tetJson['data']['user']['verified'] == True):
                user += " <:verified:845092546979299328>"
        if ('supporter' in tetJson['data']['user']):
            if (tetJson['data']['user']['supporter'] == True):
                for i in range(tetJson['data']['user']['supporter_tier']):
                    user += " <:support:845092535206674501>"
        if (len(tetJson['data']['user']['badges']) != 0):
            badges = badgeEmoji(tetJson['data']['user']['badges'])

        embed = discord.Embed(
            title=user, color=discord.Color.green(), url=userURL)
        embed.set_author(name="Tetr.io", icon_url=emojiTetrio)
        embed.set_thumbnail(url=avatarURL)
        embed.add_field(name="Tetra League", value=currRank + " " + "(" + currRating + " TR)" +
                        " with " + globeEmoji + " " + standing + " / " + emojiFlags + " " + standingLocal, inline=False)
        embed.add_field(name="Stats", value="_**PPS**_ " + pps +
                        "\n_**APM**_ " + apm +
                        "\n_**VS**_ " + vs +
                        "\n_**GPM**_ " + gpm, inline=True)
        embed.add_field(name="Solo Records", value="_**Sprint(40L)**_ " + str(record40) + "\n_**Blitz**_ " + str(blitzScore) +
                        "\n" + badges, inline=True)
        embed.add_field(name="Played Since", value=joinDate, inline=False)

        await msg.send(embed=embed)


client.run(secret.TOKEN)
