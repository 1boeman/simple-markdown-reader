from flask import Flask, url_for, request
import markdown2
import sqlite3
from flask import render_template
import glob
import os
import io
import yaml
import re

app = Flask(__name__)

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
DB = cfg['db']['file']

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

@app.route('/toevoegen')
def toevoegen():
  return render_template("toevoegen.html")


@app.route('/lijst')
def toon_lijst():
  # load article
  lijst = []
  conn = get_db()
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute('select * from recepten') 
  rows = c.fetchall() 

  return render_template('list.html',rows=rows,name="Recepten")

@app.route('/artikel/<artikel_id>')
def toon_artikel(artikel_id):
  # load article
  conn = get_db()
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute('select * from recepten where id = ?',(artikel_id)) 
  result = c.fetchone()
  content = dict(result)
  content['ingredienten'] = markdown2.markdown(result['ingredienten'])
  content['bereiding'] = markdown2.markdown(result['bereiding'])

  return render_template('artikel.html',content=content)

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
  conn.close()
 
  return 
