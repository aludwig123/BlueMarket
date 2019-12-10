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
    #user logs into app using their Wellesley authentication
    print('Session keys: ', list(session.keys()))
    if 'CAS_USERNAME' in session:
        user = session['CAS_USERNAME']
        conn = dbInteractions.getConn()
        dbInteractions.login(conn, user)
        return redirect(url_for('feed'))
    return render_template('login.html')

@app.route('/logged_in/', methods = ['GET', 'POST'])
def logged_in():
    #user has successfully logged in
    flash("Successfully logged in!")
    return redirect(url_for('index'))

@app.route('/feed/')
def feed():
    #gets the entire feed, all the posts that exist in the database
    conn = dbInteractions.getConn()
    feed = dbInteractions.getFeed(conn)
    return render_template('feed.html', posts = feed)

@app.route('/feed/<category>/')
def feedCategory(category):
    #displays all posts with given category
    conn = dbInteractions.getConn()
    feed = dbInteractions.getFeedCategory(conn,category)
    return render_template('feed.html', posts = feed)

@app.route('/post/<pid>/')
def readPost(pid):
    #displays all the details of a post including its items given a post id
    conn = dbInteractions.getConn()
    post = dbInteractions.getPost(conn,pid)
    items = dbInteractions.getPostItems(conn, pid)
    return render_template('post.html', posts = post, items=items)

@app.route('/bookmark/<pid>/')
def bookmarkPost(pid):
    #bookmark post given post id, using user id 
    print('reachedbookmark')
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    dbInteractions.bookmarkPost(conn, user, pid)
    return redirect(request.referrer)

@app.route('/search/', methods = ['GET', 'POST'])
def searchItems():
    #search for keywork in items and display item's post
    conn = dbInteractions.getConn()
    if request.method == 'GET':
        query = request.args.get('searchterm')
        PIDS = dbInteractions.getSearchPIDs(conn,query)
        posts = [dbInteractions.getPost(conn, postID['pid'])[0] for postID in PIDS]
        return render_template('feed.html', posts = posts)

@app.route('/myStuff/')
def myStuff():
    #displays all posts made by user
    conn = dbInteractions.getConn()
    posts = dbInteractions.getMyPosts(conn, session['CAS_USERNAME'])
    return render_template('myStuff.html', posts = posts)

@app.route('/myStuff/bookmarked/')
def getBookmarked():
    #displays all posts bookmarked by user
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    posts = dbInteractions.getBookmarked(conn, user)
    return render_template('bookmarkedPost.html', posts = posts)

@app.route('/interested/<iid>/')
def interestedItem(iid):
    #mark interested in item by user
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    dbInteractions.interestedIn(conn, user, iid)
    return redirect(request.referrer)

@app.route('/myStuff/interested/')
def getInterestedIn():
    #displays all items interested in by user
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    items = dbInteractions.getInterestedIn(conn, user)
    return render_template('interestedItems.html', items = items)

@app.route('/deletePost/<pid>/', methods = ['GET', 'POST'])
def deletePost(pid):
    #delete post given pid, will delete it's items too
    pid = int(pid)
    conn = dbInteractions.getConn()
    posts = dbInteractions.getMyPosts(conn, session['CAS_USERNAME'])
    if pid in [post['pid'] for post in posts]:
        dbInteractions.deletePost(conn, pid)
    return redirect(url_for('myStuff'))

@app.route('/makePost/', methods = ['GET', 'POST'])
def makePost():
    #create post and add items if wanted
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
        pid = dbInteractions.makePost(conn,session['CAS_USERNAME'],title,category,pRange,pType,pickup,description)

        #pid = dbInteractions.getLatestPid(conn)
        numItemsTest = request.form['numItems']
        print("numItemsTest" + str(numItemsTest))
        numItems = 5
        for i in range(1, numItems):
            iName = request.form['item_' + str(i)]
            iPrice = request.form['price_' + str(i)]
            #iPhoto = request.form['photo_' + str(i)]
            iQuality = request.form['quality_' + str(i)]
            iIsRented = request.form['isRented_' + str(i)]
            iDescription = request.form['description_' + str(i)]
            dbInteractions.addItem(conn, pid['max(pid)'], iName, iPrice, iQuality, iIsRented, iDescription)

        return redirect(url_for('feed'))


@app.route('/logout/', methods = ['GET', 'POST'])
def logout():
    #log out user 
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