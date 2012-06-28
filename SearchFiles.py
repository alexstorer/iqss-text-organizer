#!/usr/bin/env python
from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, SimpleFSDirectory, File, \
    VERSION, initVM, Version, IndexReader
import threading, sys, time, os, csv

"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


def run(searcher, analyzer, reader):
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query:")
        if command == '':
            return

        print "Searching for:", command
        query = QueryParser(Version.LUCENE_CURRENT, "contents",
                            analyzer).parse(command)
        scoreDocs = searcher.search(query, reader.maxDoc()).scoreDocs
        print "%s total matching documents." % len(scoreDocs)

        allDicts = []
        allTerms = set()
        
        print "building unique terms"
        ticker = Ticker()
        threading.Thread(target=ticker.run).start()
        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            vector = reader.getTermFreqVector(scoreDoc.doc,"contents")
            #print 'path:', doc.get("path"), 'name:', doc.get("name")
            d = dict()
            allTerms = allTerms.union(map(lambda x: x.encode('utf-8'),vector.getTerms()))
            for (t,num) in zip(vector.getTerms(),vector.getTermFrequencies()):
                d[t.encode('utf-8')] = num
            d["___path___"] = doc.get("path").encode('utf-8')
            d["___name___"] = doc.get("name").encode('utf-8')
            allDicts.append(d)
        names = set(allTerms)
        ticker.tick = False
        print "\nTerms: ", len(allTerms)
        print "Ready to write TDM."
        l = list(allTerms)
        l.sort()
        writeTDM(allDicts,['___name___','___path___']+l,'tdm.csv')

def writeTDM(allDicts,allTerms,fname):
    f = open(fname,'w')
    c = csv.DictWriter(f,allTerms)
    print "writing header"
    dhead = dict()
    for k in allTerms:
        dhead[k] = k
    c.writerow(dhead)
    print "iterating across dictionaries..."
    for d in allDicts:
        c.writerow(d)
    f.close()
    

if __name__ == '__main__':
    STORE_DIR = "index"
    initVM()
    print 'lucene', VERSION
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    reader = IndexReader.open(directory, True)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    run(searcher, analyzer, reader)
    searcher.close()
