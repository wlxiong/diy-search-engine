import sys
import tornado.gen
import tornado.web
import tornado.ioloop
import tornado.httpclient

class MainHandler(tornado.web.RequestHandler):

    backend = 0

    def initialize(self, port):
        self.port = port

    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        MainHandler.backend += 1
        MainHandler.backend %= 3
        port = MainHandler.backend + self.port + 1
        resp = yield client.fetch("http://127.0.0.1:%d" % port)
        self.write(resp.body)

def start(port):
    app = tornado.web.Application([tornado.web.url(r"/", MainHandler, dict(port=port))])
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
    print >> "listen %d" % port

if __name__ == '__main__':
    port = int(sys.argv[1])
    start(port)
