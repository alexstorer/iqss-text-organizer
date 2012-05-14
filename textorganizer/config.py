import codecs
import os
import subprocess
import sqlite3



def get_and_check_config(config_file_location,programdir):
    config=read_config_file(config_file_location,programdir)
    while not check_db(config['dblocation']):
        print "Generating new configuration file."
        make_config_file(config_file_location,programdir)
    return config
            
def read_config_file(config_file_location,programdir):
    dblocation = None
    configuration = {}

    try:
        cnffile = open(config_file_location,'r')
        print "Reading configuration file"
        for line in cnffile:
            if line.startswith("dblocation:"): 
                dblocation = line[len("dblocation:")+1:].strip()
                configuration['dblocation']=dblocation
        return configuration
    except IOError:
        print "No configuration file found; creating a new one."
        make_config_file(config_file_location,programdir)
        return read_config_file(config_file_location,programdir)


def make_config_file(config_file_location,programdir):

    dblocation = os.path.join(programdir,"textdb.sqlite")

    while True:
        newloc = raw_input("Please choose a location for the main database. Press ENTER to accept the default value (" + dblocation+") or type a new file path.\n> ")
        if newloc == '': newloc=dblocation
        try:
            # expand '~' to /home/[user] and then convert to absolute path
            expanded_path = os.path.realpath(os.path.expanduser(newloc))

            # spawn a sqlite process using the expanded_path as the database. this checks if a) expanded_path is a valid path to a database, and b) if the database exists there.
            # NOTE: this is vulnerable to shell injection. we should fix that. 
            output=subprocess.check_output('sqlite3 \''+expanded_path+'\' .tables',stderr=subprocess.STDOUT,shell=True)
            dblocation = expanded_path
            break
        except:
            print "Could not create a database file at this location. Please try again."

    cnffile = open(config_file_location,'w')
    cnffile.write("dblocation: "+dblocation)

def check_db(dblocation):
    '''First, try to connect to the database'''
    try:
        conn=sqlite3.connect(dblocation)
        c=conn.cursor()
    except:
        print "Could not connect to database in config file."
        return False

    '''Now try to get the number of entries in the FILES table'''
    try:
        c.execute('SELECT count(filepath) FROM files')
        num_files = c.fetchone()[0]
        print "FILES table contains "+str(num_files)+" entries."
    except sqlite3.OperationalError:
        print "No FILES table found; creating one."
        c.execute('CREATE TABLE FILES (pkid INTEGER PRIMARY KEY AUTOINCREMENT, filepath TEXT)')
        conn.commit()

    '''Next, try to get the number of entries in the TAGS table'''
    try:        
        c.execute('SELECT count(tag) FROM tags')
        num_tags=c.fetchone()[0]
        print "TAGS table contains "+str(num_tags)+" entries."
    except sqlite3.OperationalError:
        print "No TAGS table found; creating one."

        c.execute('CREATE TABLE TAGS (file_id INTEGER, tag TEXT)')
        conn.commit()

    '''Finally, try to get the number of entries in the NGRAMS table'''
    try:        
        c.execute('SELECT count(file_id) FROM NGRAMS')
        num_ngrams=c.fetchone()[0]
        print "NGRAMS table contains "+str(num_ngrams)+" entries."
    except sqlite3.OperationalError:
        print "No NGRAMS table found; creating one."

        c.execute('CREATE TABLE NGRAMS (file_id INTEGER, ngram TEXT, count INTEGER)')
        conn.commit()

    conn.close()
    return True
