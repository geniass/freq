#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ^ this seems to be how to handle characters like ê and א

import sqlite3 as sqlite
import urllib
from xml.dom.minidom import parseString
from HTMLParser import HTMLParser
import re

# Constants for indexing the array returned by sqlite to make reading easier
WORD = 0
FREQ = 1
URL = 0

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

    # Check if this url is already in the db. If it is, we shouldn't scan the
    # page again, so return TRUE. If it is not, write the url to the db and
    # return FALSE

    # WEIRD: using :select_1 etc. isn't working in this method and only in this
    # method. No idea why. Actually, maybe something to do with encoding
    def check_url_in_DB(self, url):
        self.cur.execute("""SELECT * FROM urls WHERE url=?""",
                         (url,))
        result = self.cur.fetchone()
        print result
        if result:
            # The url is already in the db; it has already been scanned, so
            # we shouldn't scan it again
            print ("""The url %s hase already been scanned! Skipping to next \
                   one...""" %(result[URL]))
            return True
        else:
            self.cur.execute("""INSERT INTO urls
                             VALUES(?)""", (url,))
            return False


    # The code for persisting the Key-Value dictionary to disk
    def update_word_rows(self, dictionary):
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
            else:
                #self.cur.execute("""INSERT INTO words VALUES(?,?)""", (k,v))
                self.cur.execute("""INSERT INTO words
                                 VALUES(:insert_1,:insert_2)""",
                                 {'insert_1':k,'insert_2':v})
                
    def __init__(self):
        try:
            # Notice that this function creates the file if it doesn't exist
            self.con = sqlite.connect("words.db")
            self.cur = self.con.cursor()

            # Create the table, if it doesn't exists, to store words and their
            # frequencies
            self.cur.execute("""CREATE TABLE IF NOT EXISTS words
                                    (word text, frequency INTEGER)""")
            # Create the table, if it doesn't exist, to store already-scanned urls
            self.cur.execute("""CREATE TABLE IF NOT EXISTS urls
                                    (url text)""")
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
    def add_word(self, word):
        key = word.capitalize()          # Capitalize first char of every word
        if key in self.words:
            num = self.words[key] + 1
            self.words[key] = num
        else:                   
            self.words[key] = 1

class Article:

    def process_text(self, regex='''([A-Z][a-z]+|[a-z]+)|(’n)'''):
        #'''([A-Z][a-z]+|[a-z]+)|(’n)'''
       iterator = re.finditer(regex, self.text)
       words = [m.group().decode("utf-8") for m in iterator]
       return words

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

    # Returns the Page's list-of-words generator
    def get_words(self):
        return self.words

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
            self.words = a.process_text()

    def handle_data(self, data):
        if (self.lastTagIsArticle):
            self.articleText += data

    # Note: HTMLParser is an older class and therefore does not support 'super'
    # syntax.
    def __init__(self, url=None):
        HTMLParser.__init__(self)
        self.url = url
        self.articleText = ""
        self.words = []
        self.lastTagIsArticle = False
        self.download_and_parse()

def main():
    db = Database()
    wd = WordDictionary()

    url = """http://feeds.beeld.com/articles/Beeld/Tuisblad/rss"""
    w = Beeld(url)
    link = w.links()[3].decode("utf-8")

    scanUrl = db.check_url_in_DB(link)
    if not scanUrl:
        # Url not in db
        b = BeeldPage(link)
        words = b.get_words()
        for w in words:
            wd.add_word(w)
        print wd.words
        db.update_word_rows(wd.words)
        db.commit()
    else:
        # Already scanned. Error printed in checkUrlInDB
        pass
    
    db.close()

if __name__ == "__main__":
    main()
