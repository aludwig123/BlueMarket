# BlueMarket app.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

from flask import (Flask, render_template, request, url_for, redirect, flash, session)
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

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    session['user'] = request.form.get('loginEmail')
    user = session['user']
    print(user)
    conn = functions.getConn()
    functions.login(conn, user)
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
    conn = functions.getConn()
    posts = functions.getMyPosts(conn, session['user'])
    return render_template('myStuff.html', posts = posts)

@app.route('/makePost/', methods = ['GET', 'POST'])
def makePost():
    conn = functions.getConn()
    if request.method == 'GET':
        return render_template('makePost.html')
    else: 
        title = request.form.get('title')
        category = request.form.get('category')
        pRange = request.form.get('price-range')
        pType = request.form.get('payment-type')
        pickup = request.form.get('pickup-location')
        description = request.form.get('description')
        functions.makePost(conn,session['user'],title,category,pRange,pType,pickup,description)
        return redirect(url_for('feed'))

@app.route('/addItem/', methods = ['GET', 'POST'])
def addItem():
    conn = functions.getConn()
    if request.method == 'GET':
        return render_template('makePost.html')
    else:
        item = request.form.get('item')
        price = request.form.get('price')
        quality = request.form.get('quality')
        if (request.form.get('isRented') == "True"):
            isRented = 1
        else:
            isRented = 0
        description = request.form.get('description')
        #functions.addItem(conn, item, price, quality, isRented, description)
        return redirect(url_for('feed'))

@app.route('/logout/', methods = ['GET', 'POST'])
def logout():
    return redirect(url_for('loginPage'))


if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)