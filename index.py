from flask import Flask, url_for, request, flash, redirect,session, render_template, json
from elasticsearch import Elasticsearch
import markdown2
import sqlite3
import glob
import os
import io
import yaml
import re

app = Flask(__name__)

config_file = os.path.join(os.path.dirname(__file__), 'config.yml')  
with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
DB = cfg['db']['file']
app.secret_key = bytes (cfg['app_secret'])

def get_db():
  conn = sqlite3.connect(DB)
  return conn

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404


@app.route('/opslaan',methods = ['POST', 'GET'] )
def opslaan():
  if request.method == 'POST':
    dataverwerken(request.form)      
    return render_template("result.html", result = request.form)
  else:
    return render_template('404.html'), 404

@app.route('/verwijderen/<artikel_id>')
def verwijderen(artikel_id):
  conn = get_db()
  c = conn.cursor()
  c.execute(''' delete from recepten where id = ? ''', [artikel_id])
  conn.commit()
  conn.close()
 
  flash( artikel_id+ ' is echt helemaal verwijderd')
  return redirect(url_for('toon_aanpassen_lijst'), code=302)

@app.route('/toevoegen')
def toevoegen():
  return render_template("toevoegen.html")

@app.route('/simple_query',strict_slashes=False)
def es_simple_query():
  query = request.args.get('q')
  res = ''
  if len(query):
    es = Elasticsearch()
    res = es.search(index='',
      body={
        "query": {
          "simple_query_string" : {
              "query": query,
              "default_operator": "and"
          }
        }
    })
  #return json.dumps(res)
  return render_template('search.html',results=res,query=query)

@app.route('/')
def toon_lijst():
  # load article
  lijst = []
  conn = get_db()
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute('select * from recepten order by titel') 
  rows = c.fetchall() 

  return render_template('list.html',rows=rows,name="Recepten")

@app.route('/aanpassen')
def toon_aanpassen_lijst():
  # load article
  lijst = []
  conn = get_db()
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute('select * from recepten order by titel') 
  rows = c.fetchall() 

  return render_template('list.html',rows=rows,name="Recepten",edit=True)

@app.route('/wijzig_artikel/<artikel_id>')
def wijzig_artikel(artikel_id):
  conn = get_db()
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute('select * from recepten where id = ?',(artikel_id,)) 
  result = c.fetchone()
  content = dict(result)
  return render_template('toevoegen.html',artikel=content)
 

@app.route('/artikel/<artikel_id>')
def toon_artikel(artikel_id):
  # load article
  conn = get_db()
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute('select * from recepten where id = ?',(artikel_id,)) 
  result = c.fetchone()
  content = dict(result)
 
  content['tijd'] = int(result['tijd'])
  content['personen'] = int(result['personen'])
  content['ingredienten'] = markdown2.markdown(result['ingredienten'])
  content['bereiding'] = markdown2.markdown(result['bereiding'])

  return render_template('artikel.html',content=content)

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
  return d

def indexeren(artikel_id):
  es = Elasticsearch()
  conn = get_db()
  conn.row_factory = dict_factory
  c = conn.cursor()
  c.execute('select * from recepten where id = ?',(artikel_id,)) 
  result = c.fetchall()
  row = result.pop()

  es.index(index='kookboek',id=row['id'],body=row)
  conn.close()

def dataverwerken(form):
  conn = get_db()
  c = conn.cursor()
  identifier = int(form['id'])
  if int(form['id']) == 0:
    values = [form['titel'], form['ingredienten'],form['bereiding'], form['tijd'], form['personen']]
    c.execute(''' insert into recepten
                    (titel,ingredienten,bereiding,tijd,personen) 
                      VALUES ( ?,?,?,?,? )''',values)
    identifier = c.lastrowid
  elif int(form['id']) > 0:
    values = [form['titel'], form['ingredienten'],form['bereiding'], form['tijd'], form['personen'], form['id']]
    c.execute(''' update recepten
                    set titel = ?, ingredienten = ?, bereiding = ?,  tijd = ?, personen = ?
                      where id = ? ''',values)
  
  conn.commit() 
  indexeren(identifier)
  conn.close()
 
  return 
