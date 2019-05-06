#!/usr/bin/env python
'''
  Index everything in the datbase
'''
from elasticsearch import Elasticsearch
import sqlite3
import yaml

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

with open("config.yml", 'r') as ymlfile:
  cfg = yaml.load(ymlfile)

es = Elasticsearch()
es.indices.create(index='kookboek', ignore=400)


DB = cfg['db']
conn = sqlite3.connect( DB['file'] )
conn.row_factory = dict_factory
    
cur = conn.cursor()

cur.execute('select * from recepten')
rows = cur.fetchall()
for row in rows:
  res = es.index(index='kookboek',id=row['id'],body=row)
  print res
conn.close()
