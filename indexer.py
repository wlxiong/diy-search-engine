from config import gconf
import sys
import string
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
try:
    import cPickle as pickle
except ImportError:
    import pickle


xml_escape = {
    '"': "&quot;",
    "'":  "&apos;",
    "<":  "&lt;",
    ">":  "&gt;",
    "&":  "&amp;"
}

def tokenize_doc(text):
    for old, esc in xml_escape.items():
        text = string.replace(text, esc, old)
    text = [c if c not in set(string.punctuation + string.whitespace) else " " for c in text]
    return string.split("".join(text))

def compute_tf(terms):
    tf = {}
    for t in terms:
        tf[t] = 1 if t not in tf else tf[t] + 1
    return tf

def compute_df(tf_partitions):
    df = {}
    for partition in tf_partitions:
        for docid, tf in partition.items():
            for t in tf:
                df[t] = 1 if t not in df else df[t] + 1
    return df

def main():
    source = sys.argv[1]
    tree = ET.parse(source)
    root = tree.getroot()
    ns = {"wiki": "http://www.mediawiki.org/xml/export-0.10/"}
    index_server = gconf["index_server"]
    doc_server = gconf["doc_server"]
    tf_partitions = [dict() for _ in range(len(index_server))]
    doc_partitions = [dict() for _ in range(len(doc_server))]
    pages = root.findall("wiki:page", ns)
    for child in pages:
        title = child.find("wiki:title", ns).text.encode('utf-8', 'replace')
        docid = int(child.find("wiki:id", ns).text)
        text = child.find("./wiki:revision/wiki:text", ns)
        bytes = text.attrib["bytes"]
        leng = len(text.text)
        ip = docid % len(index_server)
        dp = docid % len(doc_server)
        print ip, dp, docid, title, bytes
        tf_partitions[ip][docid] = compute_tf(tokenize_doc(text.text))
        doc_partitions[dp][docid] = {"title": title, "text": text.text}

    print "docs", len(pages)
    print "tf partitions"
    for i, partition in enumerate(tf_partitions):
        print len(partition)
        dump = open("tf-%03d.dump" % (i + 1,), 'wb')
        pickle.dump(partition, dump, 2)
    print "doc partitions"
    for i, partition in enumerate(doc_partitions):
        print len(partition)
        dump = open("doc-%03d.dump" % (i + 1,), 'wb')
        pickle.dump(partition, dump, 2)
    print "global df"
    df = compute_df(tf_partitions)
    df["_doc_count_"] = len(pages) * 1.0
    sorted_df = sorted(df.items(), key=lambda t: t[1])
    print sorted_df[:10]
    print sorted_df[-10:]
    dump = open("df.dump", 'wb')
    pickle.dump(df, dump, 2)

if __name__ == "__main__":
    main()
