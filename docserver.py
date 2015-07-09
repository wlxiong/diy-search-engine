import sys
import socket
import tornado.ioloop
import tornado.web
from config import gconf
try:
    import cPickle as pickle
except ImportError:
    import pickle

class MainHandler(tornado.web.RequestHandler):

    def initialize(self, port):
        self.max_results = gconf["max_results"]
        self.port = port
        partition_id = port % 1000
        with open("doc-%03d.dump" % partition_id, 'rb') as fin:
            self.doc = pickle.load(fin)

    def get(self, *args, **kwargs):
        q = self.get_query_argument("q", None)
        docid = self.get_query_argument("id", None)
        if q is None or docid is None:
            self.write({"results": []})
            return
        docid = int(docid)
        if docid not in self.doc:
            self.write({"results": []})
            return
        qset = set(q.split())
        title = self.doc[docid]["title"]
        text = self.doc[docid]["text"]
        results = self.doc[docid]
        self.write(results)

def start(port):
    app = tornado.web.Application([tornado.web.url(r"/doc", MainHandler, dict(port=port))])
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
    print >> "listen %d" % port

if __name__ == '__main__':
    port = int(sys.argv[1])
    start(port)
