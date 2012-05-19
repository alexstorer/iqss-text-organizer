import subprocess
import codecs
import os
import sqlite3

class selection():
    def __init__(self,selectstring,dblocation):
        self.dblocation = dblocation
        self.selecteditems = self.parseargs_select(selectstring)


    def parseargs_select(self,selectstring):
        if selectstring.startswith('tag '):
            return self.select_tags(selectstring[4:])
        elif selectstring.startswith('where '):
            return self.select_complex(selectstring[6:])
        elif selectstring.startswith('containing '):
            return self.select_containing(selectstring[11:])
        else:
            print 'Invalid selection.'
            return []

    def select_tags(self,tagstring):
        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()
        try:
            c.execute("SELECT pkid FROM FILES INNER JOIN TAGS on FILES.pkid=TAGS.file_id where TAGS.tag=:tag",{'tag':tagstring})
            allpkids=[row[0] for row in c]
        except:
            print "Invalid Selection."
            allpkids = []
        conn.close()
        return allpkids

    def select_all(self):
        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()

        try:
            c.execute("SELECT pkid FROM FILES")
            allpkids=[row[0] for row in c]
        except:
            print "Invalid Selection."
            allpkids = []
        conn.close()
        return allpkids

    def select_containing(self,selectstring):
        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()

        try:
            c.execute("select distinct pkid from FILES INNER JOIN NGRAMS on pkid = file_id where ngram=:searchstr",{'searchstr':selectstring})
            allpkids=[row[0] for row in c]
        except:
            print "Invalid Selection."
            allpkids = []
        conn.close()
        return allpkids
    
    def select_complex(self,sqlstring):
        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()

        #again, this is super vulnerable to SQL injection, but it allows the user to use custom SQL
        try:
            c.execute("SELECT pkid FROM FILES where "+sqlstring)
            allpkids=[row[0] for row in c]
        except:
            print "Invalid Selection."
            allpkids = []
        conn.close()
        return allpkids

    def parseargs_view(self,viewstring):
        if viewstring.startswith('tags'):
            return self.get_all_tags()
        elif viewstring.startswith('fields'):
            return self.get_all_fields()

    def get_all_tags(self):
        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()

        c.execute("SELECT DISTINCT tag FROM FILES")
        alltags=[row[0] for row in c]

        conn.close()
        return alltags

    def parseargs_export(self,exportstring):
        if exportstring.startswith('files'):
            self.export_files()
        elif exportstring.startswith('tdm'):
            self.export_tdm()
        else:
            print "Invalid arguments; please type \'export files\' or \'export tdm\'"
                                      
    
    def export_files(self):
        if len(self.selecteditems) == 0:
            print "No files selected; use 'select tag [tag]' or 'select where [field]=[value]' to select files, then try again."
            return

        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()

        filepaths = []
        for pkid in self.selecteditems:
            c.execute("SELECT filepath FROM FILES WHERE pkid=:id",{'id': pkid})
            filepaths.append(c.fetchone()[0])
        
        conn.close()

        print str(len(filepaths))+" files to be exported. Type the name of the directory to export to. (or press enter for default directory ./export"
        outdirraw = raw_input('> ')
        if outdirraw == '': outdirraw = './export'
        expanded_outdir = os.path.realpath(os.path.expanduser(outdirraw))
        try:
            subprocess.call(['mkdir',expanded_outdir])
        except:
            print 'could not create directory. Proceeding anyway'
        print "Exporting files to path "+expanded_outdir+"..."
        for path in filepaths:
            subprocess.call(['cp',path,os.path.join(expanded_outdir,os.path.split(path)[1])])
        print "Done."
            
    def export_tdm(self):
        if len(self.selecteditems) == 0:
            print "No files selected; use 'select tag [tag]' or 'select where [field]=[value]' to select files, then try again."
            return

        conn=sqlite3.connect(self.dblocation)
        c=conn.cursor()

        filepaths = []
        for pkid in self.selecteditems:
            pass
#NEED TO FIND A GOOD SQL COMMAND TO CREATE A TDM
        
        conn.close()
