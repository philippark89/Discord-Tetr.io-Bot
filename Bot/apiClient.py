import aiohttp


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
