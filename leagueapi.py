from makedb import createTable, insertIntoTable, runSQLNoClose, DB, openDB, closeSql
import requests

#sql = "Select 1 from summonerTable where summonerName = ?"
#print(len(runSQLNoClose(connection, cursor, sql, vals = ("bluebottle",))))

authorization = "tgYUY4ydFTRWexZkRdxV9uGUn323dzq5"
officialauth = "ab962bdc-fc8e-4b4b-a273-281d75bd81c6"

def getSummonerByName(name, region, auth = None):
	if auth == None:
		auth = authorization
	url = "https://community-league-of-legends.p.mashape.com/api/v1.0/%s/summoner/getSummonerByName/%s" %(region, name)
	response = requests.get(url,
	  
	  headers={
	    "X-Mashape-Authorization": auth
	  }
	);

	result = response.json()
	return result

def getSummonerByID(sumID, region, auth = None):
	if auth == None:
		auth = authorization
	url = "https://community-league-of-legends.p.mashape.com/api/v1.0/%s/summoner/getSummonerBySummonerId/%s" %(region, sumID)
	response = requests.get(url,
	  
	  headers={
	    "X-Mashape-Authorization": auth
	  }
	);

	result = response.json()
	return getSummonerByName(result['array'][0], region)

def getSummonersByID(sumID, region, auth = None):
	if auth == None:
		auth = authorization
	url = "https://community-league-of-legends.p.mashape.com/api/v1.0/%s/summoner/getSummonerBySummonerId/%s" %(region, sumID)
	response = requests.get(url,
	  
	  headers={
	    "X-Mashape-Authorization": auth
	  }
	);
	result = response.json()
	return [getSummonerByName(summonerName, region) for summonerName in result['array']]


def insertSummonersIfNotExist(column, value, region, autoUpdate = False):
	unionargs = ''
	for (index, val) in enumerate(value):
		if index == 0:
			firstval = value[index]
		else:
			unionargs += ' union select {} '.format(str(val))
	sql = 'select * from ( select {} temp {}) where temp not in (select {} from summonerTable)'.format(firstval, unionargs, column)
	notExists = runSQLNoClose(connection, cursor, sql)
	summonersNotExisting = ','.join(str(val[0]) for val in notExists)
	if summonersNotExisting:
		jsonResult = getSummonersByID(summonersNotExisting, region)
		for summoner in jsonResult:
			summonerName = summoner['name']
			summonerID = summoner['summonerId']
			acctID = summoner['acctId']
			insertIntoTable("summonerTable", (summonerName, region, summonerID, acctID, int(autoUpdate)))
			print("%s added to db. " %(summonerName))

def insertSummonerIfNotExist(column, value, region, autoUpdate = False):
	sql = "Select 1 from summonerTable where {} = ?".format(column)
	if len(runSQLNoClose(connection, cursor, sql, vals = (value,))) == 0:
		if column == "summonerName":
			jsonResult = getSummonerByName(value, region)
		else:
			jsonResult = getSummonerByID(value, region)
		summonerName = jsonResult['name']
		summonerID = jsonResult['summonerId']
		acctID = jsonResult['acctId']

		insertIntoTable("summonerTable", (summonerName, region, summonerID, acctID, int(autoUpdate)))
		print("%s added to db. " %(summonerName))
	else:
		print("%s already exists in db. " %(value))

def getSummonersToUpdate():
	sql = "Select acctID from summonerTable where autoUpdate = 1"
	return(runSQLNoClose(connection, cursor, sql))

def getOfficialGameHistory(summonerID, region, auth = None):
	if auth == None:
		auth = officialauth
	url = "https://prod.api.pvp.net/api/lol/%s/v1.3/game/by-summoner/%s/recent?api_key=%s" %(region.lower(), summonerID, auth)
	response = requests.get(url);
	return response.json()

def getMashApeGameHistory(summonerID, region, auth = None):
	if auth == None:
		auth = authorization
	url = "https://community-league-of-legends.p.mashape.com/api/v1.0/%s/summoner/getRecentGames/%s" %(region, summonerID)
	response = requests.get(url,
	  
	  headers={
	    "X-Mashape-Authorization": auth
	  }
	);

	result = response.json()
	return result

def updateGameHistory():
	sql = "Select acctID, summonerID, region from summonerTable where autoUpdate = ?"
	result = runSQLNoClose(connection, cursor, sql, vals = (1,))
	if len(result) != 0:
		for summonerID in result:
			acctID, sumID, region = summonerID
			mashApeHistory = getMashApeGameHistory(acctID, region)
			gameIDs = [game['gameId'] for game in mashApeHistory['gameStatistics']['array']]
			qmarks = "?," * len(gameIDs)
			gameIDString = ""
			for g in gameIDs:
				gameIDString += str(g) + ","
			sql = "Select 1 from gameStat where gameID in ({})".format(qmarks[:-1])
			if len(runSQLNoClose(connection, cursor, sql, vals = tuple(gameIDs)))==0:
				print("adding games from official API")
				officialHistory = getOfficialGameHistory(sumID, region)
				insertIntoGameHistory(officialHistory)
			else:
				print('no call to official API needed')
			handleGameDetails(mashApeHistory, region)

	else:
		print("No one to update")

def gameNotInGameDB(gameID):
	sql = "Select 1 from gameStat where gameID = ?"
	return len(runSQLNoClose(connection, cursor, sql, vals = (gameID,))) == 0

def gameNotInStatsDB(gameID, accountID):
	sql = "Select 1 from simpleGameTable where gameID = ? and accountID = ?"
	return len(runSQLNoClose(connection, cursor, sql, vals = (gameID,accountID))) == 0

def oppositeTeam(team):
	if team == 200:
		return 100
	return 200

def insertIntoGameHistory(officialHistory):
	for game in officialHistory['games']:
		gameID = game['gameId']
		if gameNotInGameDB(gameID):
			gameDate = game['createDate']
			gameType = game['gameType']
			gameMode = game['gameMode']
			gameSubType = game['subType']
			duration = game['stats']['timePlayed']
			winner = game['stats']['team'] if game['stats']['win'] else oppositeTeam(game['stats']['team'])
			insertIntoTable("gameStat", (gameDate, gameID, gameType, gameMode, gameSubType, duration, winner))
			print('added game %s' %(gameID))
		else:
			print('game %s already in db' %(gameID))
		#print(duration)

def handleGameDetails(mashApeHistory, region):
	#game = mashApeHistory['gameStatistics']['array'][0]
	#if 1 == 1:
	for game in mashApeHistory['gameStatistics']['array']:
		accountID = game['userId']
		gameID = game['gameId']
		insertGameIfNotInStatsDB(game, accountID)
		fellowPlayers = game['fellowPlayers']['array']
		playerArray = [player['summonerId'] for player in fellowPlayers]
		insertSummonersIfNotExist("summonerID", playerArray, region)
		for player in fellowPlayers:
			summonerID = player['summonerId']
			#insertSummonerIfNotExist("summonerID", summonerID, region)
			acctID = getAccountID(summonerID)
			mashApeHistory = getMashApeGameHistory(acctID, region)
			for g in mashApeHistory['gameStatistics']['array']:
				if g['gameId'] == gameID:
					insertGameIfNotInStatsDB(g, acctID)


def getAccountID(summonerID):
	sql = "Select acctID from summonerTable where summonerID = ?"
	return(runSQLNoClose(connection, cursor, sql, vals = (summonerID,))[0][0])

#createTable("simpleGameTable", "date integer, summonerID integer, gameID integer, championId integer, skinIndex integer, gameType text, gameMode text, gameSubType text, spell1 integer, spell2 integer, win integer, duration integer, k integer, d integer, a integer, team integer")
#createTable("scoreBoardGameTable", "summonerID integer, gameID integer, spell1 integer, spell2 integer, win integer, level integer, gold integer, cs integer, neutral_cs integer, champ_damage integer, healing integer, greenWards integer, pinkWards integer, item1 integer, item2 integer, item3 integer, item4 integer, item5 integer, item6 integer, premadeSize integer")
#createTable("detailedGameTable", "accountID integer, summonerID integer, gameID integer, physicalDamageChamp integer, trueDamageTaken integer, physicalDamageTaken integer, magicDamageChamp integer, wardPlaced integer, totalDamageTaken integer, magicDamageDealt integer, crit integer, wardKilled integer, trueDamageDealt integer, magicDamageTaken integer, turretsKilled Integer, largestMultiKill integer, timeDead integer, totalDamageDealt integer, barracksKilled integer, trueDamageDealtChamp integer, totalCC integer, physicalDamageDealt integer")
def insertGameIfNotInStatsDB(game, accountID):
	gameID = game['gameId']
	if gameNotInStatsDB(gameID, accountID):
		insertGameDetails(game)
	else:
		print("game %s in db already for account id %s" %(gameID, accountID))


def makeDict(arr):
	result = {}
	for n in arr:
		result[n['statType']] = n['value']
	return result

def insertGameDetails(game):
	accountID = game['userId']
	summonerID = game['summonerId']
	if summonerID == 0:
		sql = "Select summonerID from summonerTable where acctID = ?"
		summonerID = runSQLNoClose(connection, cursor, sql, vals = (accountID,))[0][0]
	gameID = game['gameId']
	championID = game['championId']
	skinIndex = game['skinIndex']
	spell1 = game['spell1']
	spell2 = game['spell2']
	gamestats = makeDict(game['statistics']['array'])
	win = zeroIfError(gamestats,'WIN')
	kills = zeroIfError(gamestats,'CHAMPIONS_KILLED')
	deaths = zeroIfError(gamestats,'NUM_DEATHS')
	assists = zeroIfError(gamestats,'ASSISTS')
	team = game['teamId']
	insertIntoTable("simpleGameTable", (None, accountID, summonerID, gameID, championID, skinIndex, None, None,None,spell1, spell2, win, 
		None, kills , deaths, assists, team))

	level = game['level']
	gold = zeroIfError(gamestats,'GOLD_EARNED')
	cs = zeroIfError(gamestats,'MINIONS_KILLED')
	neutral_cs = zeroIfError(gamestats,'NEUTRAL_MINIONS_KILLED')
	champ_damage = zeroIfError(gamestats,'TOTAL_DAMAGE_DEALT_TO_CHAMPIONS')
	healing = zeroIfError(gamestats,'TOTAL_HEAL')
	greenWards = zeroIfError(gamestats,'SIGHT_WARDS_BOUGHT_IN_GAME')
	pinkWards = zeroIfError(gamestats,'VISION_WARDS_BOUGHT_IN_GAME')
	item1 = zeroIfError(gamestats,'ITEM1')
	item2 = zeroIfError(gamestats,'ITEM2')
	item3 = zeroIfError(gamestats,'ITEM3')
	item4 = zeroIfError(gamestats,'ITEM4')
	item5 = zeroIfError(gamestats,'ITEM5')
	item6 = zeroIfError(gamestats,'ITEM6')
	premadeSize = game['premadeSize']
	insertIntoTable("scoreBoardGameTable", (accountID, summonerID, gameID, spell1, spell2, win, level, gold, cs, neutral_cs, champ_damage, healing, 
		greenWards, pinkWards, item1, item2, item3, item4, item5, item6, premadeSize))

	physicalDamageChamp = zeroIfError(gamestats,'PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS')
	trueDamageTaken = zeroIfError(gamestats,'TRUE_DAMAGE_TAKEN')
	physicalDamageTaken = zeroIfError(gamestats,'PHYSICAL_DAMAGE_TAKEN')
	magicDamageChamp = zeroIfError(gamestats,'MAGIC_DAMAGE_DEALT_TO_CHAMPIONS')
	wardPlaced = zeroIfError(gamestats,'WARD_PLACED')
	totalDamageTaken = zeroIfError(gamestats,'TOTAL_DAMAGE_TAKEN')
	magicDamageDealt = zeroIfError(gamestats,'MAGIC_DAMAGE_DEALT_PLAYER')
	crit = zeroIfError(gamestats,'LARGEST_CRITICAL_STRIKE')
	wardKilled = zeroIfError(gamestats,'WARD_KILLED')
	trueDamageDealt = zeroIfError(gamestats,'TRUE_DAMAGE_DEALT_PLAYER')
	magicDamageTaken = zeroIfError(gamestats,'MAGIC_DAMAGE_TAKEN')
	turretsKilled = zeroIfError(gamestats,'TURRETS_KILLED')
	largestMultiKill = zeroIfError(gamestats,'LARGEST_MULTI_KILL')
	timeDead = zeroIfError(gamestats,'TOTAL_TIME_SPENT_DEAD')
	totalDamageDealt = zeroIfError(gamestats,'TOTAL_DAMAGE_DEALT')
	barracksKilled = zeroIfError(gamestats,'BARRACKS_KILLED')
	trueDamageDealtChamp = zeroIfError(gamestats,'TRUE_DAMAGE_DEALT_TO_CHAMPIONS')
	totalCC = zeroIfError(gamestats,'TOTAL_TIME_CROWD_CONTROL_DEALT')
	physicalDamageDealt = zeroIfError(gamestats,'PHYSICAL_DAMAGE_DEALT_PLAYER')

	insertIntoTable("detailedGameTable", (accountID, summonerID, gameID, physicalDamageChamp, trueDamageTaken, physicalDamageTaken, 
		magicDamageChamp, wardPlaced, totalDamageTaken, magicDamageDealt, crit, wardKilled, trueDamageDealt, magicDamageTaken, 
		turretsKilled, largestMultiKill, timeDead, totalDamageDealt, barracksKilled, trueDamageDealtChamp, totalCC, physicalDamageDealt))
	print("added game %s for %s" %(str(gameID), str(accountID)))

def zeroIfError(gameStats, key, default = 0):
	try:
		return gameStats[key]
	except KeyError:
		return default

connection,cursor = openDB(DB)
insertSummonerIfNotExist("summonerName", "bluebottle", "NA", True)
insertSummonerIfNotExist("summonerName", "portalmighty", "NA", True)
updateGameHistory()
closeSql(connection, cursor)