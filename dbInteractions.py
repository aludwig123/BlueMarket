# BlueMarket functions.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

import dbi

def getConn():
    '''Return connection to bluemark_db'''
    dsn = dbi.read_cnf('~/cs304/BlueMarket/static/bluemarket_db.cnf')
    conn = dbi.connect(dsn)
    conn.select_db('bluemark_db')
    return conn

def makePost(conn,user,title,category,pRange,pType,pickup,description):
    '''Make a new post (no items), return the most recent inserted pid by current thread.'''
    curs = dbi.dictCursor(conn)
    curs.execute('''insert into post(uid,name,category,priceRange,paymentType,pickUpLocation,description)
                    values (%s,%s,%s,%s,%s,%s,%s)''',
                [user,title,category,pRange,pType,pickup,description])
    curs.execute('''select last_insert_id()''')
    return curs.fetchone()

def uploadImage(conn, pid, filename):
    curs = dbi.dictCursor(conn)
    curs.execute('''update post set photo=%s where pid=%s''',
                [filename, pid])

def getFeed(conn):
    '''Get home feed by returning all posts in reverse chronological order'''
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post order by dateCreated DESC')
    return curs.fetchall()

def getFeedCategory(conn, category):
    '''Return info of all posts in feed for given category'''
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where category = %s order by dateCreated DESC', [category])
    return curs.fetchall()

def getPost(conn, pid):
    '''Get post info given post id'''
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where pid = %s', [pid])
    return curs.fetchall()

def login(conn, user):
    '''Handle user log in. If new user, insert into user table.'''
    curs = dbi.dictCursor(conn)
    curs.execute('select * from user where uid = %s', [user])
    if not curs.fetchall(): #if this user does not exist in the user table yet
        curs.execute('insert into user(uid) values(%s)', [user])

def getMyPosts(conn, user):
    '''Returns all posts by user given connection and user uid'''
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where uid = %s order by dateCreated DESC', [user])
    return curs.fetchall()

def getSearchPIDs(conn, query):
    '''Returns all pids that have items containing the query'''
    curs = dbi.dictCursor(conn)
    curs.execute('select distinct pid from item where name like %s', ['%' + query + '%'])
    return curs.fetchall()

def deletePost(conn, pid):
    '''Delete post given its post id'''
    curs = dbi.dictCursor(conn)
    curs.execute('delete from post where pid = %s', [pid])
    
def bookmarkPost(conn, uid, pid):
    '''Given post id and user id, insert into bookmark table'''
    curs = dbi.dictCursor(conn)
    curs.execute('insert into bookmark values(%s, %s)', [uid, pid])

def getBookmarked(conn, user):
    '''Returns posts that have been bookmarked by the given user'''
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where pid in (select pid from bookmark where uid = %s)', [user])
    return curs.fetchall()

def interestedIn(conn, uid, iid):
    '''Given item id and user id, insert those values into interested table'''
    curs = dbi.dictCursor(conn)
    curs.execute('insert into interested values(%s, %s)', [uid, iid])
    curs.execute('select uid from post where pid = (select pid from item where iid = %s)',[iid])
    sellerId = curs.fetchone()
    curs.execute('select name from item where iid = %s',[iid])
    itemName = curs.fetchone()
    return (sellerId['uid'], itemName['name'])

def getSeller(conn, iid):
    '''Return seller id given item id'''
    curs = dbi.dictCursor(conn)
    curs.execute('select uid from post where pid = (select pid from item where iid = %s)',[iid])
    return curs.fetchone()['uid']

def getSellerB(conn, pid):
    '''Return seller id given post id'''
    curs = dbi.dictCursor(conn)
    curs.execute('select uid from post where pid = %s',[pid])
    return curs.fetchone()['uid']

def checkIsInterestedIn(conn, uid, iid):
    '''Given item id and user id, check if user already marked item as interested in
    Returns true if user is already interested in item'''
    curs = dbi.dictCursor(conn)
    curs.execute('select * from interested where uid = %s and iid = %s',[uid,iid])
    return len(curs.fetchall()) != 0

def checkIsBookmarked(conn, uid, pid):
    '''Given post id and user id, check if user already bookmarked post
    Returns true if post is already bookmarked'''
    curs = dbi.dictCursor(conn)
    curs.execute('select * from bookmark where uid = %s and pid = %s',[uid,pid])
    return len(curs.fetchall()) != 0

def unbookmarkPost(conn, uid, pid):
    '''Given user id and post id, remove from bookmark table'''
    curs = dbi.dictCursor(conn)
    curs.execute('delete from bookmark where uid = %s and pid = %s', [uid, pid])

def getInterestedIn(conn, uid):
    '''Returns items the given user is interested in'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from item where iid in (select iid from interested where uid = %s)''', [uid])
    return curs.fetchall()

def addItem(conn, pid, name, price, quality, isRented, description):
    '''Insert an item into the item table'''
    curs = dbi.dictCursor(conn)
    curs.execute('''insert into item(pid, name, price, quality, isRented, description)
                    values(%s,%s,%s,%s,%s,%s)''', [pid, name, price, quality, isRented, description])

def getPostItems(conn, pid):
    '''Get all items of a given post'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from item where pid = %s''', [pid])
    return curs.fetchall()

