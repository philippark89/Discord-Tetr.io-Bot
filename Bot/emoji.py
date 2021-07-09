def rank(rank):
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


def badges(json):
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
