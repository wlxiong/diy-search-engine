import sys
import math
import socket
import heapq
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
        with open("tf-%03d.dump" % partition_id, 'rb') as fin:
            self.tf = pickle.load(fin)
        with open("df.dump", 'rb') as fin:
            self.df = pickle.load(fin)
            self.doc_count = self.df["_doc_count_"]

    def get(self, *args, **kwargs):
        q = self.get_query_argument("q", None)
        if q is None:
            self.write({"postings": []})
            return
        qset = set(q.split())
        score = []
        for docid, tf in self.tf.items():
            accum = 0.0
            for t, f in tf.items():
                if t in qset:
                    accum += f * math.log(self.doc_count / self.df[t]) * self.df[t]
            if accum > 0.0:
                score.append((docid, accum))
        postings = heapq.nlargest(self.max_results, score, lambda t: t[1])
        self.write({"postings": postings})

def start(port):
    app = tornado.web.Application([tornado.web.url(r"/index", MainHandler, dict(port=port))])
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
    print >> "listen %d" % port

if __name__ == '__main__':
    port = int(sys.argv[1])
    start(port)
