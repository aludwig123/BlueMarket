# BlueMarket app.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

from flask import (Flask, render_template, request, url_for, redirect, flash, session)
from datetime import datetime
import random
import dbInteractions
from flask_cas import CAS

app = Flask(__name__)

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
    '''User logs into app using their Wellesley authentication.
        After authentication, redirect to feed.'''
    if 'CAS_USERNAME' in session:
        user = session['CAS_USERNAME']
        conn = dbInteractions.getConn()
        dbInteractions.login(conn, user)
        return redirect(url_for('feed'))
    return render_template('login.html')

@app.route('/logged_in/', methods = ['GET', 'POST'])
def logged_in():
    '''User has successfully logged in, redirect to index route.'''
    flash("Successfully logged in!")
    return redirect(url_for('index'))

@app.route('/feed/')
def feed():
    '''Gets the entire feed aka all the posts that exist in the database.
        Displays them in reverse chronological order.'''
    conn = dbInteractions.getConn()
    feed = dbInteractions.getFeed(conn)
    return render_template('feed.html', posts = feed)

@app.route('/feed/<category>/')
def feedCategory(category):
    '''Displays all posts with given category'''
    conn = dbInteractions.getConn()
    feed = dbInteractions.getFeedCategory(conn,category)
    return render_template('feed.html', posts = feed)

@app.route('/post/<pid>/')
def readPost(pid):
    '''Displays all the details of a post including its items, given the post id'''
    conn = dbInteractions.getConn()
    post = dbInteractions.getPost(conn,pid)
    items = dbInteractions.getPostItems(conn, pid)
    return render_template('post.html', posts = post, items=items)

@app.route('/bookmark/<pid>/')
def bookmarkPost(pid):
    '''Bookmark post given post id, using current user id'''
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    dbInteractions.bookmarkPost(conn, user, pid)
    return redirect(request.referrer)

@app.route('/search/', methods = ['GET', 'POST'])
def searchItems():
    '''Search items for given keyword and display each matching item's parent post'''
    conn = dbInteractions.getConn()
    if request.method == 'GET':
        query = request.args.get('searchterm')
        PIDS = dbInteractions.getSearchPIDs(conn,query)
        posts = [dbInteractions.getPost(conn, postID['pid'])[0] for postID in PIDS]
        return render_template('feed.html', posts = posts)

@app.route('/myStuff/')
def myStuff():
    '''Displays all posts created by the current user'''
    conn = dbInteractions.getConn()
    posts = dbInteractions.getMyPosts(conn, session['CAS_USERNAME'])
    return render_template('myStuff.html', posts = posts)

@app.route('/myStuff/bookmarked/')
def getBookmarked():
    '''Displays all posts bookmarked by the current user'''
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    posts = dbInteractions.getBookmarked(conn, user)
    return render_template('bookmarkedPost.html', posts = posts)

@app.route('/interested/<iid>/')
def interestedItem(iid):
    '''User marks that they are interested in an item'''
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    dbInteractions.interestedIn(conn, user, iid)
    return redirect(request.referrer)

@app.route('/myStuff/interested/')
def getInterestedIn():
    '''Displays all items the current user is interested in'''
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    items = dbInteractions.getInterestedIn(conn, user)
    return render_template('interestedItems.html', items = items)

@app.route('/deletePost/delete-<pid>/', methods = ['GET', 'POST'])
def deletePost(pid):
    '''Delete post given pid, will delete it's items too via cascade'''
    pid = int(pid)
    conn = dbInteractions.getConn()
    posts = dbInteractions.getMyPosts(conn, session['CAS_USERNAME'])
    if pid in [post['pid'] for post in posts]:
        dbInteractions.deletePost(conn, pid)
    return redirect(url_for('myStuff'))

@app.route('/editPost/edit-<pid>/', methods = ['GET', 'POST'])
def editPost(pid):
    '''Edit post given pid'''
    pid = int(pid)
    conn = dbInteractions.getConn()
    postInfo = dbInteractions.getPostInfo(conn, session['CAS_USERNAME'])
    if pid in [post['pid'] for post in posts]:
        dbInteractions.deletePost(conn, pid)
    return redirect(url_for('myStuff'))

@app.route('/makePost/', methods = ['GET', 'POST'])
def makePost():
    '''Create post and add a minimum of one item'''
    conn = dbInteractions.getConn()
    if request.method == 'GET':
        return render_template('makePost.html')
    else: 
        title = request.form.get('title')
        category = request.form.get('category')
        pRange = request.form.get('price-range')
        pType = request.form.get('payment-type')
        pickup = request.form.get('pickup-location')
        description = request.form.get('description')
        pid = dbInteractions.makePost(conn,session['CAS_USERNAME'],title,category,pRange,pType,pickup,description)

        # iterate through each item and add it to item table 
        numItems = request.form['numItems']
        for i in range(1, int(numItems)+1):
            iName = request.form['item_' + str(i)]
            iPrice = request.form['price_' + str(i)]
            #iPhoto = request.form['photo_' + str(i)]
            iQuality = request.form['quality_' + str(i)]
            iIsRented = request.form['isRented_' + str(i)]
            iDescription = request.form['description_' + str(i)]
            dbInteractions.addItem(conn, pid['last_insert_id()'], iName, float(iPrice), iQuality, int(iIsRented), iDescription)
        
        return redirect(url_for('feed'))


@app.route('/logout/', methods = ['GET', 'POST'])
def logout():
    '''Log user out'''
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
    app.debug = True
    app.run('0.0.0.0',port)