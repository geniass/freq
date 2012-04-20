#!/usr/bin/env python

import sqlite3 as sqlite

# ==============================================================================
# Database Interface Code ======================================================
# ==============================================================================

class Database:

    def __init__(self):
        try:
            self.con = sqlite.connect("words.db")
            self.cur = self.con.cursor()
        except sqlite.Error, e:
            print e

    def close(self):
        if self.con:
            self.con.close()


db = Database()
db.close()
