#!/usr/bin/env python

import sqlite3

# ==============================================================================
# Database Interface Code ======================================================
# ==============================================================================

def load_database():
    try:
        conn = sqlite3.connect("words.db")
    except:
        print("Error")

# Essentially main
def bootstrap():
    load_database()

bootstrap()
