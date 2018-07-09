from flask import Flask
import markdown2
from flask import render_template
from os import listdir
import os
import io

app = Flask(__name__)

CONTENT_DIR = "../eten/"


@app.route('/artikel/<artikel_id>')
def toon_artikel(artikel_id):
  # load article
  pathattempt,article_id = os.path.split(artikel_id) 
  file = io.open( CONTENT_DIR + artikel_id,"r", encoding="utf-8")
  md = file.read()
  html = markdown2.markdown(md)
  return render_template('artikel.html',content=html, name=artikel_id)


@app.route('/user/<username>')
def show_user_profile(username):
  # show the user profile for that user
  return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
  # show the post with the given id, the id is an integer
  return 'Post %d' % post_id

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
  # show the subpath after /path/
  return 'Subpath %s' % subpath

