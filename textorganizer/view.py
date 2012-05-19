import sqlite3

class viewdb():
    def __init__(self,argstring,dblocation):
        self.dblocation = dblocation
        self.parseargs_view(argstring)

    def parseargs_view(self,viewstring):
        if viewstring.startswith('tags'):
            return self.get_all_tags()
        elif viewstring.startswith('fields'):
            return self.get_all_fields()

    def get_all_tags(self):
        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()

        c.execute("SELECT DISTINCT tag FROM TAGS")
        alltags=[row[0] for row in c]

        conn.close()
        
        for t in alltags:
            print t

    def get_all_fields(self):
        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()

        c.execute("PRAGMA table_info(FILES)")
        alltags=[row[1] for row in c]

        conn.close()
        
        #first two entries in alltags are 'pkid' and 'filepath', so skip these
        for t in alltags[2:]:
            print t
