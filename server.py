import tornado.ioloop
import tornado.web
import os

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        from makedb import runSQLNoClose, DB, openDB, closeSql, runSQLNoCloseAsDict
        connection,cursor = openDB(DB)
        sql = "Select acctID as id, summonerName as name from summonerTable where autoUpdate = 1"
        test = runSQLNoCloseAsDict(connection, sql)
        self.render("players.html", players=test)

class PlayerHandler(tornado.web.RequestHandler):
    def get(self, id):
        self.write(id)

application = tornado.web.Application(
    [
        (r'/', MainHandler),
        (r'/player/(.*)', PlayerHandler),
    ], 
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    )

def startServer():
    port = 8888
    print("server started on %s" %(str(port)))
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    startServer()