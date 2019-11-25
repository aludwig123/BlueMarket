-- # Blue Market
-- # Authors: Analiese Ludwig, Hannah Yi, Isabel Bryant
-- # tableCreation.sql

drop table if exists user;
drop table if exists post;
drop table if exists item;
drop table if exists bookmark;
drop table if exists interested;
drop table if exists postsItems;

CREATE TABLE user (
    uid varchar(10),
    name varchar(50),
    email varchar(30),
    gradYear varchar(4),
    avatar blob,
    primary key (uid)
);

CREATE TABLE post (
    pid int auto_increment not null,
    name varchar(30),
    dateCreated timestamp not null default current_timestamp,
    category enum('Services', 'Textbooks', 'Clothing', 'Beauty',
                'Food', 'Home', 'Entertainment', 'Looking_For', 'School_Supplies', 'Other'),
    priceRange enum('free', 'low', 'medium', 'high'),
    paymentType enum('n/a', 'cash', 'venmo', 'other'),
    pickUpLocation enum('Bates', 'Beebe','Cazenove', 'Cervantes', 'Claflin',
                    'Dower', 'Freeman', 'Lake_House', 'McAfee', 'Munger',
                    'Pomeroy', 'Severance', 'Shafer', 'Stone-Davis','Tower_Court', 
                    'Cedar_Lodge', 'French_House', 'Other', 'Instead' ),
    description varchar(200),
    primary key (pid)
);

CREATE TABLE item (
    iid int auto_increment not null,
    name varchar(30),
    price float(9,2),
    photo blob,
    quality enum('new', 'like_new', 'gently_used', 'used', 'heavily_used', 'poor'),
    isRented boolean,
    description varchar(100),
    primary key (iid)
);

CREATE TABLE bookmark (
    uid int,
    pid int, 
    primary key (uid, pid)
);

CREATE TABLE interested (
    uid int,
    iid int, 
    primary key (uid, iid)
);

CREATE TABLE postsItems (
    iid int,
    pid int, 
    primary key (iid, pid)
);
