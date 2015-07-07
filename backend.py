import sys
import socket
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):

    def initialize(self, port):
        self.port = port

    def get(self, *args, **kwargs):
        self.write("%s:%d" % (socket.gethostname(), self.port))

def start(port):
    app = tornado.web.Application([tornado.web.url(r"/", MainHandler, dict(port=port))])
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
    print >> "listen %d" % port

if __name__ == '__main__':
    port = int(sys.argv[1])
    start(port)
