# BlueMarket app.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

from flask import (Flask, render_template, request, url_for, redirect, flash, session)
from datetime import datetime
import random
import dbInteractions
from flask_cas import CAS
from threading import Thread, Lock

app = Flask(__name__)
lock = Lock()

#generate random secret key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'
# the following doesn't work :-(
app.config['CAS_AFTER_LOGOUT'] = 'after_logout'

@app.route('/')
def index():
    print('Session keys: ', list(session.keys()))
    if 'CAS_USERNAME' in session:
        user = session['CAS_USERNAME']
        conn = dbInteractions.getConn()
        dbInteractions.login(conn, user)
        return redirect(url_for('feed'))
    return render_template('login.html')

@app.route('/logged_in/', methods = ['GET', 'POST'])
def logged_in():
    flash("Successfully logged in!")
    return redirect(url_for('index'))

@app.route('/feed/')
def feed():
    conn = dbInteractions.getConn()
    feed = dbInteractions.getFeed(conn)
    return render_template('feed.html', posts = feed)

@app.route('/feed/<category>/')
def feedCategory(category):
    conn = dbInteractions.getConn()
    feed = dbInteractions.getFeedCategory(conn,category)
    return render_template('feed.html', posts = feed)

@app.route('/post/<pid>')
def readPost(pid):
    conn = dbInteractions.getConn()
    post = dbInteractions.getPost(conn,pid)
    return render_template('post.html', posts = post)

@app.route('/bookmark/<pid>')
def bookmarkPost(pid):
    print('reachedbookmark')
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    dbInteractions.bookmarkPost(conn, user, pid)
    return redirect(request.referrer)

@app.route('/search/', methods = ['GET', 'POST'])
def searchItems():
    conn = dbInteractions.getConn()
    if request.method == 'GET':
        return redirect(url_for('feed'))
    else:
        query = request.args.get('searchterm')
        pids = dbInteractions.getSearchPIDs(conn,query)
        posts = [dbInteractions.getPost(conn,pid) for pid in pids]
        return render_template('feed.html', posts = posts)

@app.route('/myStuff/')
def myStuff():
    conn = dbInteractions.getConn()
    posts = dbInteractions.getMyPosts(conn, session['CAS_USERNAME'])
    return render_template('myStuff.html', posts = posts)

@app.route('/myStuff/bookmarked/')
def getBookmarked():
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    posts = dbInteractions.getBookmarked(conn, user)
    return render_template('bookmarkedPost.html', posts = posts)

@app.route('/deletePost/<pid>', methods = ['GET', 'POST'])
def deletePost(pid):
    pid = int(pid)
    conn = dbInteractions.getConn()
    posts = dbInteractions.getMyPosts(conn, session['CAS_USERNAME'])
    if pid in [post['pid'] for post in posts]:
        dbInteractions.deletePost(conn, pid)
    return redirect(url_for('myStuff'))

@app.route('/makePost/', methods = ['GET', 'POST'])
def makePost():
    conn = dbInteractions.getConn()
    if request.method == 'GET':
        return render_template('makePost.html')
    else: 
        title = request.form.get('title')
        category = request.form.get('category')
        print("category: " + category)
        pRange = request.form.get('price-range')
        pType = request.form.get('payment-type')
        pickup = request.form.get('pickup-location')
        description = request.form.get('description')
        dbInteractions.makePost(conn,session['CAS_USERNAME'],title,category,pRange,pType,pickup,description)

        pid = dbInteractions.getLatestPid(conn)
        numItemsTest = request.form.get('numItems')
        print("numItemsTest" + str(numItemsTest))
        numItems = 5
        for i in range(1, numItems):
            iName = request.form['item_' + str(i)]
            iPrice = request.form['price_' + str(i)]
            iPhoto = request.form['photo_' + str(i)]
            iQuality = request.form['quality_' + str(i)]
            iIsRented = request.form['isRented_' + str(i)]
            iDescription = request.form['description_' + str(i)]
            dbInteractions.addItem(conn, pid, iName, iPrice, iQuality, iIsRented, iDescription)

        return redirect(url_for('feed'))


@app.route('/logout/', methods = ['GET', 'POST'])
def logout():
    return redirect(url_for('loginPage'))


if __name__ == '__main__':
    import os, sys
    if len(sys.argv) > 1:
        port=int(sys.argv[1])
        if not(1943 <= port <= 1950):
            print('For CAS, choose a port from 1943 to 1950')
            sys.exit()
    else:
        port=os.getuid()
    # uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)