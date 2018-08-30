#!/usr/bin/env python

import sqlite3
import yaml

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

DB = cfg['db']
conn = sqlite3.connect( DB['file'] )

conn.execute('''CREATE TABLE if not exists recepten
                 (id INTEGER PRIMARY KEY,
                  pad TEXT UNIQUE,
                  titel TEXT NOT NULL,
                  ingredienten TEXT NOT NULL,
                  bereiding TEXT NOT NULL,
                  tijd REAL,
                  personen REAL);''')
conn.close()
