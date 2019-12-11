-- # Blue Market
-- # Authors: Analiese Ludwig, Hannah Yi, Isabel Bryant
-- # tableCreation.sql

SET FOREIGN_KEY_CHECKS = 0;
drop table if exists user;
drop table if exists post;
drop table if exists item;
drop table if exists bookmark;
drop table if exists interested;
drop table if exists postsItems;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE user (
    uid varchar(30),
    name varchar(50),
    gradYear varchar(4),
    avatar blob,
    primary key (uid)
)
ENGINE = InnoDB;

CREATE TABLE post (
    pid int auto_increment not null,
    uid varchar(30),
    name varchar(30),
    dateCreated timestamp not null default current_timestamp,
    category enum('Services', 'Textbooks', 'Clothing', 'Beauty',
    	     'Food', 'Home', 'Entertainment', 'Looking-For', 'School-Supplies', 'Other'),
    priceRange enum('free', 'low', 'medium', 'high'),
    paymentType enum('n/a', 'cash', 'venmo', 'cashVenmo', 'other'),
    pickUpLocation enum('Bates', 'Beebe','Cazenove', 'Cervantes', 'Claflin',
                    'Dower', 'Freeman', 'Lake-House', 'McAfee', 'Munger',
                    'Pomeroy', 'Severance', 'Shafer', 'Stone-Davis','Tower-Court', 
                    'Cedar-Lodge', 'French-House', 'Other', 'Instead' ),
    description varchar(200),
    primary key (pid)
)
ENGINE = InnoDB;

CREATE TABLE item (
    iid int auto_increment not null,
    pid int,
    name varchar(30),
    price float(9,2),
    photo blob,
    quality enum('new', 'like-new', 'gently-used', 'used', 'heavily-used', 'poor'),
    isRented boolean,
    description varchar(100),
    index (iid, pid),
    foreign key (pid) references post(pid) on delete cascade
)
ENGINE = InnoDB;

CREATE TABLE bookmark (
    uid varchar(30),
    pid int, 
    index (uid, pid),
    foreign key (uid) references user(uid) on delete cascade,
    foreign key (pid) references post(pid) on delete cascade
)
ENGINE = InnoDB;

CREATE TABLE interested (
    uid varchar(30),
    iid int, 
    index (uid, iid),
    foreign key (uid) references user(uid) on delete cascade,
    foreign key (iid) references item(iid) on delete cascade
)
ENGINE = InnoDB;
