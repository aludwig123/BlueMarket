# BlueMarket app.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

from flask import (Flask, render_template, request, url_for, redirect, flash, session,
                    send_from_directory, Response, make_response, jsonify)
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
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10*1024*1024 # 1 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    isSeller = dbInteractions.getSellerB(conn, pid) == session['CAS_USERNAME']
    return render_template('post.html', post=post, items=items, isSeller=isSeller)

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
        posts = [dbInteractions.getPost(conn, postID['pid']) for postID in PIDS]
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

@app.route('/interested/')
def interestedItem():
    '''User marks that they are interested in an item'''
    iid = int(request.args.get('iid'))
    conn = dbInteractions.getConn()
    user = session['CAS_USERNAME']
    seller = dbInteractions.getSeller(conn, iid)
    if user == seller:
        return jsonify( {'msg': 'You cannot mark yourself interested in your own item!'} )
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
            return jsonify( {'msg': 'Seller notified!'} )
        else: 
            return jsonify( {'msg': 'You have already marked yourself as interested in this item!'} )
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
        filename = dbInteractions.getImageFilename(conn, pid)['photo']
        if filename != 'placeholder.png':
            dbInteractions.deletePost(conn, pid)
            return redirect(url_for('delete_file', filename=filename))
        dbInteractions.deletePost(conn, pid)
    return redirect(url_for('myStuff'))

@app.route('/editPost/edit-<pid>/', methods = ['GET', 'POST'])
def editPost(pid):
    '''Edit post given pid'''
    pid = int(pid)
    conn = dbInteractions.getConn()
    if request.method == 'GET':
        postInfo = dbInteractions.getPost(conn, pid)
        items = dbInteractions.getPostItems(conn, pid)
        if session['CAS_USERNAME'] == postInfo['uid']:
            return render_template('editPost.html', info=postInfo, items=items)
        else:
            flash("You might be a hacker, please do not edit post by modifying url!")
            return redirect(url_for('myStuff'))
    elif request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        pRange = request.form.get('price-range')
        pType = request.form.get('payment-type')
        pickup = request.form.get('pickup-location')
        description = request.form.get('description')
        
        # photo upload stuff
        # start by removing old photo from uploads folder:
        oldFilename = dbInteractions.getImageFilename(conn, pid)['photo']
        if oldFilename != 'placeholder.png':
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], oldFilename))
        file = request.files['file']
        filename = file.filename
        if filename == '':
            filename = 'placeholder.png'
        else:
            if file and allowed_file(filename):
                filename = secure_filename(filename) 
                # adding random string to filename in case that two posts upload images
                # with the same name
                filename = filename.split('.')[0] + ''.join([
                    random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                    'abcdefghijklmnopqrstuvxyz' +
                                    '0123456789'))
                            for i in range(20) ]) + '.' + filename.split('.')[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Please only upload files of the following type: JPG, JPEG, GIF or PNG')
                return redirect(request.url)
        
        # iterate through each item and update it in the item table 
        numItems = request.form['numItems']
        for i in range(1, int(numItems)+1):
            iid = request.form['iid_' + str(i)]
            iName = request.form['item_' + str(i)]
            iPrice = request.form['price_' + str(i)]
            iQuality = request.form['quality_' + str(i)]
            if iQuality == "":
                iQuality = None
            iIsRented = request.form['isRented_' + str(i)]
            iDescription = request.form['description_' + str(i)]

            # photo stuff
            # start by removing old item photo from uploads folder:
            oldItemFilename = dbInteractions.getItemImageFilename(conn, iid)['photo']
            if oldItemFilename != 'placeholder.png':
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'],
                        oldItemFilename))

            iPhoto = request.files['itemFile_' + str(i)]
            iPhotoFilename = iPhoto.filename
            if iPhotoFilename == '':
                iPhotoFilename = 'placeholder.png'
            else:
                if iPhoto and allowed_file(iPhotoFilename):
                    iPhotoFilename = secure_filename(iPhotoFilename)
                    iPhotoFilename = iPhotoFilename.split('.')[0] + ''.join([
                    random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                    'abcdefghijklmnopqrstuvxyz' +
                                    '0123456789'))
                            for i in range(20) ]) + '.' + iPhotoFilename.split('.')[1]
                    iPhoto.save(os.path.join(app.config['UPLOAD_FOLDER'], iPhotoFilename))
                else:
                    flash('Please only upload files of the following type: JPG, JPEG, GIF or PNG')
                    return redirect(url_for('myStuff'))
            dbInteractions.updateItem(conn, int(iid), pid, iName, float(iPrice), iQuality,
                                        int(iIsRented), iDescription, iPhotoFilename)

        dbInteractions.updatePost(conn,pid,session['CAS_USERNAME'],title,category,pRange,
                                        pType,pickup,description,filename)
        flash("Successfully updated post!")
        return redirect(url_for('myStuff'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/deleteFile/<filename>')
def delete_file(filename):
    if filename != 'placeholder.png':
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('myStuff'))

def allowed_file(filename):
    '''Checks if a file has an extension that is valid and secure'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/makePost/', methods = ['GET', 'POST'])
def makePost():
    '''Create post and add a minimum of one item'''
    conn = dbInteractions.getConn()
    if request.method == 'GET':
        return render_template('makePost.html')
    elif request.method == 'POST': 
        title = request.form.get('title')
        category = request.form.get('category')
        pRange = request.form.get('price-range')
        pType = request.form.get('payment-type')
        pickup = request.form.get('pickup-location')
        description = request.form.get('description')

        # photo upload
        file = request.files['file']
        filename = file.filename
        if filename == '':
            filename = 'placeholder.png'
        else:
            if file and allowed_file(filename):
                filename = secure_filename(filename) 
                # adding random string to filename in case that two posts upload images
                # with the same name
                filename = filename.split('.')[0] + ''.join([
                    random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                    'abcdefghijklmnopqrstuvxyz' +
                                    '0123456789'))
                            for i in range(20) ]) + '.' + filename.split('.')[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Please only upload files of the following type: JPG, JPEG, GIF or PNG')
                return redirect(request.url)

        pid = dbInteractions.makePost(conn,session['CAS_USERNAME'],title,category,pRange,
                                        pType,pickup,description,filename)
        pid = pid['last_insert_id()']

        # iterate through each item and add it to item table 
        numItems = request.form['numItems']
        for i in range(1, int(numItems)+1):
            iName = request.form['item_' + str(i)]
            iPrice = request.form['price_' + str(i)]
            iQuality = request.form['quality_' + str(i)]
            if iQuality == "":
                iQuality = None
            iIsRented = request.form['isRented_' + str(i)]
            iDescription = request.form['description_' + str(i)]
             
            iPhoto = request.files['itemFile_' + str(i)]
            iPhotoFilename = iPhoto.filename
            if iPhotoFilename == '':
                iPhotoFilename = 'placeholder.png'
            else:
                if iPhoto and allowed_file(iPhotoFilename):
                    iPhotoFilename = secure_filename(iPhotoFilename)
                    iPhotoFilename = iPhotoFilename.split('.')[0] + ''.join([
                    random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                    'abcdefghijklmnopqrstuvxyz' +
                                    '0123456789'))
                            for i in range(20) ]) + '.' + iPhotoFilename.split('.')[1]
                    iPhoto.save(os.path.join(app.config['UPLOAD_FOLDER'], iPhotoFilename))
                else:
                    flash('Please only upload files of the following type: JPG, JPEG, GIF or PNG')
                    dbInteractions.deletePost(conn, pid)
                    return redirect(request.url)
            
            dbInteractions.addItem(conn, pid, iName, float(iPrice), iQuality, int(iIsRented),
                                    iDescription, iPhotoFilename)
        flash("Your post has been created!")
        return redirect(url_for('feed'))

@app.route('/deleteItem/')
def deleteItem():
    iid = int(request.args.get('iid'))
    conn = dbInteractions.getConn()
    seller = dbInteractions.getSeller(conn, iid)
    if session['CAS_USERNAME'] == seller:
        dbInteractions.deleteItem(conn, iid)
        return jsonify( {'msg': 'Successfully deleted item from post! Reload page to see change.'} )
    else:
        return jsonify( {'msg': "You can't delete an item from a post you didn't create you stinky hacker you!"} )
    return redirect(request.referrer)

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