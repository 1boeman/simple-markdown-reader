from flask import Flask, url_for, request
import markdown2
from flask import render_template
import glob
import os
import io

app = Flask(__name__)

CONTENT_DIR = "../eten/"

@app.route('/opslaan',methods = ['POST', 'GET'] )
def opslaan():
  if request.method == 'POST':
    return render_template("result.html", result = request.form)

@app.route('/toevoegen')
def toevoegen():
  return render_template("toevoegen.html")


@app.route('/lijst')
def toon_lijst():
  # load article
  lijst = []
  for l in glob.glob(CONTENT_DIR + "*.md"):
    lijst.append({'title': l,'url': url_for('toon_artikel',artikel_id=os.path.basename(l)) })
    
  return render_template('list.html',files=lijst,name="lijst")

@app.route('/artikel/<artikel_id>')
def toon_artikel(artikel_id):
  # load article
  pathattempt,article_id = os.path.split(artikel_id) 
  file = io.open( CONTENT_DIR + artikel_id,"r", encoding="utf-8")
  md = file.read()
  html = markdown2.markdown(md)
  return render_template('artikel.html',content=html, name=artikel_id)


