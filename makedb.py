import sqlite3

DB = 'data.db'

def createTable(table_name, cols):
	sql = 'create table if not exists {} (id INTEGER PRIMARY KEY AUTOINCREMENT, {})'.format(table_name, cols,)
	runSQL(DB, sql)

def getColumns(table_name):
	connection = sqlite3.connect(DB)
	cursor = connection.execute('select * from {}'.format(table_name,))
	names = list(map(lambda x: x[0], cursor.description))
	return names

def insertIntoTable(table_name, vals, cols = None):
	if cols == None:
		cols = tuple(getColumns(table_name)[1:])
	numberCols = len(cols) 
	qmarks = "?," * numberCols
	sql = "insert into {} {} values ({})".format(table_name, tuple(cols), qmarks[:-1])
	runSQL(DB, sql, vals)


def runSQL(dbname, sql, vals = None):
	conn = sqlite3.connect(dbname)
	c = conn.cursor()
	if vals:
		c.execute(sql, vals)
	else:
		c.execute(sql)
	conn.commit()
	result = c.fetchall()
	c.close()
	conn.close()
	return result

def openDB(dbname):
	conn = sqlite3.connect(dbname)
	c = conn.cursor()
	return conn, c

def runSQLNoClose(connection, cursor, sql, vals = None):
	conn = connection
	c = cursor
	if vals:
		c.execute(sql, vals)
	else:
		c.execute(sql)
	conn.commit()
	result = c.fetchall()
	return result

def runSQLNoCloseAsDict(connection, sql, vals = None):
	conn = connection
	conn.row_factory = dict_factory
	c = conn.cursor()
	if vals:
		c.execute(sql, vals)
	else:
		c.execute(sql)
	conn.commit()
	result = c.fetchall()
	return result

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def closeSql(connection, cursor):
	conn = connection
	c = cursor
	c.close()
	conn.close()


#sample create code


#sample if exists code
#sql = "Select 1 from summonerTable where summonerName = ?"
#print(len(runSQL(DB, sql, vals = ("bluebottle",))))
def createTables():
	import os
	if not os.path.exists(DB):
	    open(DB, 'w').close()
	createTable("summonerTable", "summonerName text, region text, summonerID integer, acctID integer, autoUpdate integer")
	createTable("gameStat", """date integer, gameID integer, gameType text, gameMode text, gameSubType text, duration integer, winner integer""")
	createTable("simpleGameTable", """date integer, accountID integer, summonerID integer, gameID integer, championId integer, skinIndex integer, gameType text, gameMode text, gameSubType text, spell1 integer, spell2 integer, win integer, duration integer, k integer, d integer, a integer, team integer""")
	createTable("scoreBoardGameTable", """accountID integer, summonerID integer, gameID integer, spell1 integer, spell2 integer, win integer, level integer, gold integer, cs integer, neutral_cs integer, champ_damage integer, healing integer, greenWards integer, pinkWards integer, item1 integer, item2 integer, item3 integer, item4 integer, item5 integer, item6 integer, premadeSize integer""")
	createTable("detailedGameTable", """accountID integer, summonerID integer, gameID integer, physicalDamageChamp integer, trueDamageTaken integer, physicalDamageTaken integer, magicDamageChamp integer, wardPlaced integer, totalDamageTaken integer, magicDamageDealt integer, crit integer, wardKilled integer, trueDamageDealt integer, magicDamageTaken integer, turretsKilled Integer, largestMultiKill integer, timeDead integer, totalDamageDealt integer, barracksKilled integer, trueDamageDealtChamp integer, totalCC integer, physicalDamageDealt integer""")



def insertSummoners():
	#sample insert code
	insertIntoTable("summonerTable", ("bluebottle", "NA", 20097, 46941, 1))
	insertIntoTable("summonerTable", ("portalmighty", "NA", 20097, 46941, 1))

if __name__=="__main__":
	createTables()
	#insertSummoners()