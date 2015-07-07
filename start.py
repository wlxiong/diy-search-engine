import tornado.web
import tornado.ioloop
import backend
import frontend

def main():
    for port in [20001, 20002, 20003]:
        app = tornado.web.Application([tornado.web.url(r"/", backend.MainHandler, dict(port=port))])
        app.listen(port)
    app = tornado.web.Application([tornado.web.url(r"/", frontend.MainHandler, dict(port=20000))])
    app.listen(20000)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
