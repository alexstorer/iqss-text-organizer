# -*- coding: utf-8 -*-

import codecs
import os
import sqlite3
import csv

def process_raw_files_interactive(filenames,configuration):
    #Define a list of unicode characters to be ignored in the term-document matrix
    global ignored_characters_dict
    global program_directory
    global dictionary
    
    ignored_characters_dict = dict.fromkeys(map(ord, './!@#$%^&*()<>“”;:"+*,'), None)
    program_directory = configuration['programdir']
    dblocation = configuration['dblocation']
    dictionary = {}

    '''first, get a list of all absolute paths to files containing text data'''
    print 'Checking files for text content'
    good_filenames = filter_filenames(filenames)

    '''Now prompt for metadata. prompt_for_metadata() returns metadata in the form of key-value pairs and tags'''
    metadata_pairs, tags = prompt_for_metadata()

    '''set the language to be English, for now. Chinese works too (just change 'en' to 'zh'), but right now there is no way to determine which language a document is in. '''
    language = 'en'

    '''finally, add to the database'''

    if add_to_db(good_filenames,dblocation,metadata_pairs,tags,language):
        print "Successfully added "+str(len(good_filenames))+" entries to database."
    else:
        print "Error adding files to database."

def process_raw_files_with_metadata_file(csv_filepath,configuration):
    global ignored_characters_dict
    global program_directory
    global dictionary
    
    ignored_characters_dict = dict.fromkeys(map(ord, './!@#$%^&*()<>“”;:"+*,'), None)
    program_directory = configuration['programdir']
    dblocation = configuration['dblocation']
    dictionary = {}

    csv_reader = csv.reader(codecs.open(csv_filepath,'r',encoding='UTF-8'), delimiter=',', quotechar='"', skipinitialspace=True)

    good_filenames = []
    md_values = []
    tags = []
    language = []

    for idx,row in enumerate(csv_reader):
        if idx == 0:
            #number of fields = number of columns in CSV file minus filepath and TAGS column
            csv_fields = row[:]
            md_fieldnames = filter(lambda z: z.lower() not in ['tags','filepath'],csv_fields)
            tag_field = [x.lower() for x in csv_fields].index('tags')
        else:
            expanded_path = check_file(row[0])
            if expanded_path:
                good_filenames.append(expanded_path)
                md_values.append([row[y] for y in range(len(csv_fields)) if y != tag_field and y != 0])
                tags.append([x.strip() for x in row[tag_field].split(',')])
                #for now, default to English for each document
                language.append('en')

    if add_to_db2(good_filenames,dblocation,md_fieldnames,md_values,tags,language):
        print "Successfully added "+str(len(good_filenames))+" entries to database."
    else:
        print "Error adding files to database."

def filter_filenames(filenames):
    good_filenames = []
    for filename in filenames:
        expanded_path = check_file(filename)
        if expanded_path: good_filenames.append(expanded_path)
    return good_filenames

def add_to_db2(filenames,dblocation,md_fieldnames,md_values,tags,language):

    conn=sqlite3.connect(dblocation)
    c=conn.cursor()

    '''add new metadata categories to the FILES table'''
    for name in md_fieldnames:
        try:
            c.execute("ALTER TABLE FILES ADD COLUMN "+name+" TEXT")
            print "Added column "+name+" to FILES table"
        except sqlite3.OperationalError:
            print "Column "+name+" is already in FILES table"

    namestring = "', '".join(md_fieldnames)
    if namestring != '': namestring = ", '"+namestring+"'"

    '''Now add each filename to database'''
    print "Adding files to database..."
    for idx,path in enumerate(filenames):
        #add filepath to FILES table with metadata

        valuestring = "', '".join(md_values[idx])
        if valuestring != '': valuestring = ", '"+valuestring+"'"

        sqlstr = 'INSERT INTO FILES (filepath'+namestring+') VALUES (\''+path+'\''+valuestring+')'

        c.execute(sqlstr)
        c.execute('SELECT max(rowid) FROM FILES')
        maxid = c.fetchone()[0]
        
        for tag in tags[idx]:
            if tag == '': continue
            t={'id':maxid,'tag':tag}
            c.execute("INSERT INTO tags VALUES (:id,:tag)",t)
        
        #compute TDM
        TDM_dict = make_TDM(path,language[idx])
        if TDM_dict is None:
            print 'Error encountered: rolling back database'
            conn.rollback()
            return False
        for key in TDM_dict:
            t={'id':maxid,'term':key,'count':TDM_dict[key]}
            c.execute("INSERT INTO NGRAMS VALUES (:id,:term,:count)",t)
        
        #print "Added entry "+str(maxid)+" to database."
    conn.commit()
    conn.close()
    return True

def add_to_db(filenames,dblocation,md_pairs,tags,language):

    conn=sqlite3.connect(dblocation)
    c=conn.cursor()

    '''add new metadata categories to the FILES table, and construct INSERT statement'''
    namestring = ""
    valuestring= ""

    # this is completely vulnerable to shell injection, and bad style. Instead of constructing sql statements like I've done, we should be using parameter substitution. However, I could not get it to work properly so I did this for now.

    for pair in md_pairs:

        namestring += (', '+pair[0])
        valuestring += (', \''+pair[1]+'\'')

        try:
            c.execute("ALTER TABLE FILES ADD COLUMN "+pair[0]+" TEXT")
            print "Added column "+pair[0]+" to FILES table"
        except sqlite3.OperationalError:
            print "Column "+pair[0]+" is already in FILES table"

    '''Now add each filename to database'''
    for path in filenames:
        #add filepath to FILES table with metadata
        sqlstr = 'INSERT INTO FILES (filepath'+namestring+') VALUES (\''+path+'\''+valuestring+')'
        c.execute(sqlstr)
        c.execute('SELECT max(rowid) FROM FILES')
        maxid = c.fetchone()[0]
        
        for tag in tags:
            t={'id':maxid,'tag':tag}
            c.execute("INSERT INTO tags VALUES (:id,:tag)",t)
        
        #compute TDM
        TDM_dict = make_TDM(path,language)
        if TDM_dict is None:
            print 'Error encountered: rolling back database'
            conn.rollback()
            return False
        for key in TDM_dict:
            t={'id':maxid,'term':key,'count':TDM_dict[key]}
            c.execute("INSERT INTO NGRAMS VALUES (:id,:term,:count)",t)
        
        print "Added entry "+str(maxid)+" to database."
    conn.commit()
    conn.close()
    return True

def get_legal_input(prompt):
    while True:
        raw = raw_input(prompt)
        if '\'' in raw or '?' in raw:
            print "Input must not contain characters \' or ?"
            continue
        else:
            return raw
        

def prompt_for_metadata():
    print 'Please provide a list of metadata categories you would like to add to this dataset, separated by commas (for example, "date, author, source", etc.) Note that this is DIFFERENT from tagging. You will be asked to provide tags in the next step.'
    
    md_raw = get_legal_input('> ')
    md_keyinput = [x.strip() for x in md_raw.split(',')]
    
    mdpairs=[]
    for key in md_keyinput:
        # skip forward if user just pressed ENTER (i.e. no metadata)
        if key == '': continue
        print 'Please enter a value for the field \''+key+'\'.'
        val = get_legal_input('> ')
        mdpairs.append((key.strip(),val.strip()))
    print 'Now enter a list of tags to associate with these files, again separated by commas.'
    tag_rawinput = get_legal_input('> ')
    tags=[x.strip() for x in tag_rawinput.split(',')]
    return mdpairs,tags


def check_file(filename):
    '''This routine checks a file to make sure it is suitable to add to the database. Right now it just tries to read the first 10 lines of the file with the UTF-8 codec; if that fails it returns False'''
    try:
        expanded_path = os.path.realpath(os.path.expanduser(filename))
        with codecs.open(expanded_path,'r',encoding='UTF-8') as inf:
            for count in range(10):
                inf.readline()
        return expanded_path
    except:
        return False

def make_TDM(filename,language):
    worddict={}
    
    '''open the file and create a list of all tokens in order (dependent on language - these are whitespace delimited words in English, and distinct characters in Chinese)'''
    with codecs.open(filename,'r',encoding="UTF-8") as inf:
        if language=='en':
            # if language is english,  split at whitespace and create an iterator whose elements are each word.
            all_words = inf.read().translate(ignored_characters_dict).lower().split()
            sep = " "
        elif language=='zh':
            # filter file to contain only CJK characters (i.e. unicode value >= 19968). return a string.
            all_words = filter(lambda x: ord(x)>19967, inf.read())
            sep = ""
        else:
            print "Unsupported language"
            return None

    #if the active dictionary is either not loaded, or is the wrong language, then reload it.
    if dictionary.get('LANGCODE1','')!=language:
        dictpath = os.path.join(program_directory,'dict-'+language+'.txt')
        try:
            with codecs.open(dictpath,'r',encoding='UTF-8') as inf:
                for line in inf:
                    dictionary[line.lower().strip()] = True
            dictionary['LANGCODE1']=language
        except:
            print 'Could not find dictionary file at '+dictpath+'. Aborting.'
            return None
            
    for i,x in enumerate(all_words):
        # add single token no matter what
        worddict[x]=worddict.get(x,0)+1
        # now add 2-4-gram if it's in the dictionary
        for y in range(2,5):
            word = sep.join(all_words[i:i+y])
            if word in dictionary: worddict[word]=worddict.get(word,0)+1

    return worddict
