#!/usr/bin/env python
# -*- coding: utf-8 -*
# ^ this seems to be how to handle characters like ê and א

import sqlite3 as sqlite

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

    def __init__(self):
        try:
            self.con = sqlite.connect("words.db")
            self.cur = self.con.cursor()

            # Create the table if it doesn't exists
            self.cur.execute(""" CREATE TABLE IF NOT EXISTS words
                                    (word text, frequency real)""")
            self.commit()

        except sqlite.Error, e:
            print e


class WordDictionary:

    def __init__(self):
        self.words = {}

    def addWord(word):
        key = word.uppercase()          # Maybe convert all words to uppercase?
        if key in self.words:
            num = self.words[key] + 1   # increment count for that word
            self.words[key] = num       # puht it behck!
        else:                           # new word
            self.words[key] = 1         # set the count to 1


db = Database()
db.close()
