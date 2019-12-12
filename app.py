# BlueMarket app.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

from flask import (Flask, render_template, request, url_for, redirect, flash, session,
                    send_from_directory)
from datetime import datetime
import random
import dbInteractions
import imghdr
from werkzeug import secure_filename
from flask_cas import CAS
from flask_mail import Mail, Message

app = Flask(__name__)

# SEND EMAIL
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='localhost',    # default; works on Tempest
    MAIL_PORT=25,               # default
    MAIL_USE_SSL=False,         # default
    MAIL_USERNAME='bluemark@wellesley.edu'
)
mail = Mail(app)

#generate random secret key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# CAS LOGIN
CAS(app)
app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'
app.config['CAS_AFTER_LOGOUT'] = 'after_logout'

# FILE UPLOAD
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

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
    seller = dbInteractions.getSellerB(conn, pid)
    if user == seller:
        flash("You cannot bookmark your own post!")
    else:
        isBookmarked = dbInteractions.checkIsBookmarked(conn, user, pid)
        if not isBookmarked:
            dbInteractions.bookmarkPost(conn, user, pid)
            flash("You have bookmarked this post!")
        else:
            flash("You have already bookmarked this post!")
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

@app.route('/unbookmark/<pid>')
def unbookmarkPost(pid):
    '''Unbookmark post for current user given pid'''
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    posts = dbInteractions.unbookmarkPost(conn, user, pid)
    flash("Post has been removed from your bookmarks!")
    return redirect(request.referrer)

@app.route('/interested/<iid>/')
def interestedItem(iid):
    '''User marks that they are interested in an item'''
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    seller = dbInteractions.getSeller(conn, iid)
    if user == seller:
        flash("You cannot mark yourself interested in your own item!")
    else:
        checkInterested = dbInteractions.checkIsInterestedIn(conn, user, iid)
        if not checkInterested:
            sellerId,itemName = dbInteractions.interestedIn(conn, user, iid)
            msg = Message(subject="Blue Market: Someone is interested in your item!",
                            sender=user+"@wellesley.edu",
                            recipients=[sellerId+"@wellesley.edu"],
                            body='''Dear '''+ sellerId+ ''', \n\n
                                        Someone is interested in purchasing your item for sale: '''+ itemName+'''\n 
                                        To contact the buyer, please respond to this email or contact them at '''+user+'''@wellesley.edu \n\n
                                        Thanks for using Blue Market! ''')
            mail.send(msg)
            flash("Seller notified!")
        else: 
            flash("You have already marked yourself as interested in this item!")
    return redirect(request.referrer)

@app.route('/myStuff/interested/')
def getInterestedIn():
    '''Displays all items the current user is interested in'''
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    items = dbInteractions.getInterestedIn(conn, user)
    return render_template('interestedItems.html', items = items)

@app.route('/deletePost/<pid>/', methods = ['GET', 'POST'])
def deletePost(pid):
    '''Delete post given pid, will delete it's items too via cascade'''
    pid = int(pid)
    conn = dbInteractions.getConn()
    posts = dbInteractions.getMyPosts(conn, session['CAS_USERNAME'])
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
        pid = pid['last_insert_id()']
        # photo upload stuff
        try:
            f = request.files['pic']
            fsize = os.fstat(f.stream.fileno()).st_size
            if fsize > app.config['MAX_CONTENT_LENGTH']:
                raise Exception('File is too big')
            mime_type = imghdr.what(f)
            if not mime_type or mime_type.lower() not in ['jpeg','gif','png', 'jpg']:
                raise Exception('Not recognized as JPG, JPEG, GIF or PNG: {}'
                                    .format(mime_type))
            filename = secure_filename('{}.{}'.format(pid,mime_type))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            f.save(pathname)
            dbInteractions.uploadImage(conn, pid, filename)
            
        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            #return render_template('form.html')

        # iterate through each item and add it to item table 
        numItems = request.form['numItems']
        for i in range(1, int(numItems)+1):
            iName = request.form['item_' + str(i)]
            iPrice = request.form['price_' + str(i)]
            #iPhoto = request.form['photo_' + str(i)]
            iQuality = request.form['quality_' + str(i)]
            iIsRented = request.form['isRented_' + str(i)]
            iDescription = request.form['description_' + str(i)]
            dbInteractions.addItem(conn, pid, iName, float(iPrice), iQuality, int(iIsRented), iDescription)
        flash("Your post has been created!")
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