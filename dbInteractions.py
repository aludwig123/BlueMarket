# BlueMarket functions.py
# Authors: Isabel Bryant, Analiese Ludwig, Hannah Yi
# Wellesley College CS304
# Fall 2019

import dbi
from threading import Thread, Lock

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
    curs.execute('select max(pid) from post where uid = %s',[user])
    return curs.fetchone()

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
    #logging in a user, new or repeat user 
    curs = dbi.dictCursor(conn)
    curs.execute('select * from user where uid = %s', [user])
    if not curs.fetchall(): #if this user does not exist in the user table yet
        curs.execute('insert into user(uid) values(%s)', [user])

def getMyPosts(conn, user):
    #get all posts by user given connection and user uid
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where uid = %s', [user])
    return curs.fetchall()

def getSearchPIDs(conn, query):
    #returns all pids that have items containing the query
    curs = dbi.dictCursor(conn)
    curs.execute('select distinct pid from item where name like %s', ['%' + query + '%'])
    return curs.fetchall()

def deletePost(conn, pid):
    #delete post given post id
    curs = dbi.dictCursor(conn)
    curs.execute('delete from post where pid = %s', [pid])
    
def bookmarkPost(conn, uid, pid):
    #given post id and user id, insert into bookmark table
    curs = dbi.dictCursor(conn)
    curs.execute('insert into bookmark values(%s, %s)', [uid, pid])

def getBookmarked(conn, user):
    #gets posts bookmarked by user
    curs = dbi.dictCursor(conn)
    curs.execute('select * from post where pid in (select pid from bookmark where uid = %s)', [user])
    return curs.fetchall()

def interestedIn(conn, uid, iid):
    #given item id and user id, insert those values into interested table
    curs = dbi.dictCursor(conn)
    curs.execute('insert into interested values(%s, %s)', [uid, iid])

def getInterestedIn(conn, uid):
    #gets items the given user is interested in 
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from item where iid in (select iid from interested where uid = %s)''', [uid])
    return curs.fetchall()

def addItem(conn, pid, name, price, quality, isRented, description):
    #insert a new item into the item table
    curs = dbi.dictCursor(conn)
    curs.execute('''insert into item(pid, name, price, quality, isRented, description)
                    values(%s,%s,%s,%s,%s,%s)''', [pid, name, price, quality, isRented, description])

def getPostItems(conn, pid):
    #get items associated with pid
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from item where pid = %s''', [pid])
    return curs.fetchall()

def getLatestPid(conn):
    #returns the latest pid
    curs = dbi.dictCursor(conn)
    curs.execute('''select max(pid) from post''')
    thing = curs.fetchone()['max(pid)']
    return (thing + 1)
