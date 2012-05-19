iqss-text-organizer
===================

A simple python-based command line tool designed to make organizing data for textual analysis easy and scalable.

SETUP
----------

To use this program, clone the git repository into a directory on your computer and then add the directory to your PATH environment variable. On Linux, this means editing your .bashrc file to contain the line 

export PATH=/path/to/iqss-text-organizer:$PATH

Now you can use the command 'txtorg' to run the program from anywhere on your computer. On the first run, it will prompt you for a database location.

USAGE
-----------

1. Adding files to the database

From anywhere on your computer, you can run the command 'txtorg add [FILE]' to add a file or files to the database. You can use standard paths to specify files; for example, running 'txtorg add ./*.txt' would import all files with suffix '.txt' in the current directory.

When you run 'txtorg add', the program will prompt you for metadata and tags pertaining to the imported files. For example, if you were importing a batch of New York Times articles from year 2008, you could type "source, year" when asked for metadata field names, and then type "New York Times" and "2008" when asked to specify values. 

In addition to metadata, you can add a simple (comma-separated) list of tags to each batch of files when prompted.

2. Selecting and exporting files

To run iqss-text-organizer in interactive mode, you can simply run 'txtorg' from the command line. At the prompt (> ), you can choose how to subset the data and what to do with the subsetted data. Current supported commands are 'select', 'export', 'view', and 'quit'.

a) select

SYNTAX:
* select tag [TAG] --- selects all documents that are tagged with TAG
* select all --- selects all documents
* select where [FIELD] [=|<|>|!=] [VALUE] [and|or] [FIELD] [=|<|>|!=] [VALUE] [...] --- selects all documents with metadata field FIELD matching value VALUE. Uses SQL syntax, so you can write commands like "select where language = 'english'" or "select where year > 2008". Note that text values must be enclosed in single or double quotes.
* select containing TERM --- selects all documents that contain a given word TERM. This does not work with words containing non-latin characters.

b) export

SYNTAX:
* export files --- exports the full text of all selected documents to a directory
* (export tdm) --- exports a term-document matrix for all selected documents to a file

c) view

SYNTAX:
* view tags --- shows a list of all tags used in the database
* view fields --- shows a list of all metadata fields defined in the database
(unsupported in version 0)
