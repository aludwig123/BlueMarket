# BlueMarket functions.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

import dbi

def getConn():
    # Return connection to bluemark_db
    dsn = dbi.read_cnf('~/cs304/BlueMarket/static/bluemarket_db.cnf')
    conn = dbi.connect(dsn)
    conn.select_db('bluemark_db')
    return conn

def makePost(conn,user,title,category,pRange,pType,pickup,description):
    # makes simple post with no items
    curs = dbi.dictCursor(conn)
    curs.execute('insert into post(uid,name,category,priceRange,paymentType,pickUpLocation,description) values (%s,%s,%s,%s,%s,%s,%s)',
                [user,title,category,pRange,pType,pickup,description])

def getFeed(conn):
    #get home feed
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post order by dateCreated DESC')
    return curs.fetchall()

def getFeedCategory(conn, category):
    #get feed for category
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where category = %s order by dateCreated DESC', [category])
    return curs.fetchall()

def getPost(conn, pid):
    #get all post info given id
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where pid = %s', [pid])
    return curs.fetchall()

def login(conn, user):
    curs = dbi.dictCursor(conn)
    curs.execute('select * from user where uid = %s', [user])
    if not curs.fetchall(): #if this user does not exist in the user table yet
        curs.execute('insert into user(uid) values(%s)', [user])

def getMyPosts(conn, user):
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where uid = %s', [user])
    return curs.fetchall()
