#!/usr/bin/env python
# -*- coding: utf-8 -*
# ^ this seems to be how to handle characters like ê and א

import sqlite3 as sqlite
import urllib
from xml.dom.minidom import parseString
from HTMLParser import HTMLParser
import re

# Constants for indexing the array returned by sqlite to make reading easier
WORD = 0
FREQ = 1

# ==============================================================================
# Database Interface Code ======================================================
# ==============================================================================

class Database:

    def commit(self):
        if self.con:
            self.con.commit()

    def close(self):
        if self.con:
            self.con.close()

    # The code for persisting the Key-Value dictionary to disk
    def updateRows(self, dictionary):
        for k,v in dictionary.iteritems():
            self.cur.execute("""SELECT * FROM words WHERE word=:select_1""",
                             {'select_1':k})
            result = self.cur.fetchone()
            print result
            if result:
                num = result[FREQ] + v
                self.cur.execute("""UPDATE words SET frequency=:update_1
                                 WHERE word=:select_1""", {'update_1':num,
                                                           'select_1':k})
                self.commit()
            else:
                #self.cur.execute("""INSERT INTO words VALUES(?,?)""", (k,v))
                self.cur.execute("""INSERT INTO words
                                 VALUES(:insert_1,:insert_2)""",
                                 {'insert_1':k,'insert_2':v})
                self.commit()

    def __init__(self):
        try:
            # Notice that this function creates the file if it doesn't exist
            self.con = sqlite.connect("words.db")
            self.cur = self.con.cursor()

            # Create the table if it doesn't exists
            self.cur.execute("""CREATE TABLE IF NOT EXISTS words
                                    (word text, frequency INTEGER)""")
            self.commit()

        except sqlite.Error, e:
            print e

# ==============================================================================
# Text Processing Code =========================================================
# ==============================================================================

# A singleton object loaded into memory at start up and persisted to disk later
class WordDictionary:

    def __init__(self):
        self.words = {}

    # Creates new or updates old
    def addWord(word):
        key = word.uppercase()          # Convert all words to uppercase?
        if key in self.words:
            num = self.words[key] + 1
            self.words[key] = num
        else:                   
            self.words[key] = 1

class Article:

    def isolate_word(self, word):
        result = ""
        for char in word:
            result += char
        print result
        return result

   # def process_text(self):
   #     words = self.text.split(" ")
   #     for w in words:
   #         self.isolate_word(w)
    def process_text(self, regex='''([A-Z][a-z]+|[a-z]+)|(’n)'''):
        #'''([A-Z][a-z]+|[a-z]+)|(’n)'''
       iterator = re.finditer(regex, self.text)
       for m in iterator:
           self.isolate_word(m.group())

    def __init__(self, text=""):
        self.text = text

# ==============================================================================
# Network Interface Code =======================================================
# ==============================================================================

# This class downloads the RSS feed at the URl supplied and parses it for its
# elements
class Beeld:

    def __init__(self, url=None):
        self.url = url
        self.download()

    def download(self):
        self.f = urllib.urlopen(self.url)

    def contents(self):
        return self.f.read()

    def get_elems(self, elem):
        result = []
        doc = parseString(self.contents())
        node = doc.documentElement
        titles = doc.getElementsByTagName(elem)
        for t in titles:
            result.append(t.firstChild.data)
        return result

    def titles(self):
        return self.get_elems('title')

    def links(self):
        return self.get_elems('link')

# Opens a Beeld Article and extracts the actual text
class BeeldPage(HTMLParser):
    
    def download_and_parse(self):
        self.f = urllib.urlopen(self.url)
        contents = self.f.read()
        self.feed(contents)
        self.close()

    # The attributes are an array with 1 2-tuple in them
    def is_article_body(self, atts):
        return (atts[0][0] == 'class' and atts[0][1] == 'clr_left')

    # Overrride functions

    # Q: What is going on here?
    # A: The parser traverses tags and calls these functions when specific
    #    elements are found. Generally it finds a tag (calls handle_starttag)
    #    then handles_data before moving onto the next tag). We set a marker
    #    after the tag we want (main article) : self.lastTagIsArticle. When the
    #    handle_data function is called and this marker is true, that data is
    #    the actual article.

    def handle_starttag(self, tag, attrs):
        if (tag == "p" and len(attrs) == 1):
            if (self.is_article_body(attrs)):
                self.lastTagIsArticle = True
            else:
                self.lastTagIsArticle = False

    def handle_endtag(self, tag):
        if (tag == "html"):
            a = Article(self.articleText)
            a.process_text()

    def handle_data(self, data):
        if (self.lastTagIsArticle):
            self.articleText += data

    # Note: HTMLParser is an older class and therefore does not support 'super'
    # syntax.
    def __init__(self, url=None):
        HTMLParser.__init__(self)
        self.url = url
        self.articleText = ""
        self.lastTagIsArticle = False
        self.download_and_parse()

db = Database()
db.close()

w = Beeld("http://feeds.beeld.com/articles/Beeld/Tuisblad/rss")
link = w.links()[2]

b = BeeldPage(link)
