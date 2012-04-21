#!/usr/bin/env python
# -*- coding: utf-8 -*
# ^ this seems to be how to handle characters like ê and א

import sqlite3 as sqlite
import urllib
from xml.dom.minidom import parseString
from HTMLParser import HTMLParser

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


class WordDictionary:

    def __init__(self):
        self.words = {}

    def addWord(word):
        key = word.uppercase()          # Convert all words to uppercase?
        if key in self.words:
            num = self.words[key] + 1
            self.words[key] = num
        else:                   
            self.words[key] = 1

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
        print contents
        self.feed(contents)
        self.close()

    # Overrride functions

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

    # Note HTMLParser is an older class and therefore does not support 'super'
    # syntax
    def __init__(self, url=None):
        HTMLParser.__init__(self)
        self.url = url
        self.download_and_parse()

db = Database()
db.close()

w = Beeld("http://feeds.beeld.com/articles/Beeld/Tuisblad/rss")
link = w.links()[2]

b = BeeldPage(link)
