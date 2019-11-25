# BlueMarket app.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

from flask import (Flask, render_template, request, url_for, redirect, flash)
from datetime import datetime
import random
import functions 

app = Flask(__name__)

#generate random secret key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

@app.route('/')
def loginPage():
    return render_template('login.html')

@app.route('/login/')
def login():
    return redirect(url_for('feed'))

@app.route('/feed/')
def feed():
    conn = functions.getConn()
    feed = functions.getFeed(conn)
    return render_template('feed.html', posts = feed)

@app.route('/feed/<category>/')
def feedCategory(category):
    conn = functions.getConn()
    feed = functions.getFeedCategory(conn,category)
    return render_template('feed.html', posts = feed)

@app.route('/post/<pid>')
def readPost(pid):
    conn = functions.getConn()
    post = functions.getPost(conn,pid)
    return render_template('post.html', posts = post)

@app.route('/myStuff/')
def myStuff():
    return render_template('myStuff.html')

@app.route('/makePost/', methods = ['GET', 'POST'])
def makePost():
    conn = functions.getConn()
    if request.method == 'GET':
        return render_template('makePost.html')
    else: 
        title = request.form.get('title')
        #date = datetime.now()
        #dateStr = date.strftime("%d/%m/%Y %H:%M:%S")
        category = request.form.get('category')
        pRange = request.form.get('price-range')
        pType = request.form.get('payment-type')
        pickup = request.form.get('pickup-location')
        description = request.form.get('description')
        functions.makePost(conn,title,category,pRange,pType,pickup,description)
        return redirect(url_for('feed'))

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)