# Blue Market
# Authors: Analiese Ludwig, Hannah Yi, Isabel Bryant
# tableCreation.sql

CREATE TABLE post (
     pid int auto_increment,
     name varchar(30),
     dateCreated datetime,
     category enum('Services', 'Textbooks', 'Clothing', 'Beauty',
                    'Food', 'Home', 'Entertainment', 'Looking For', 'Other'),
     priceRange enum('free', 'low', 'medium', 'high'),
     paymentType enum('cash', 'venmo', 'other'),
     pickUpLocation enum('Bates', 'Beebe','Cazenove', 'Cervantes', 'Claflin',
                        'Dower', 'Freeman', 'Lake House', 'McAfee', 'Munger',
                        'Pomeroy', 'Severance', 'Shafer', 'Stone-Davis','Tower Court', 
                        'Cedar Lodge', 'French House', 'Other', 'Instead' ),
     description varchar(200),
     primary key (pid));

CREATE TABLE item (
     iid int auto_increment,
     name varchar(30),
     price float(9,2),
     photo image,
     quality enum('new', 'like new', 'gently used', 'used', 'heavily used', 'poor'),
     isRented boolean,
     photo varchar(50),
     primary key (iid));

CREATE TABLE bookmark (
    uid,
    pid, 
    foreign key(uid) references user(uid),
    foreign key(pid) references post(pid));

CREATE TABLE interested (
    uid,
    iid, 
    foreign key(uid) references user(uid),
    foreign key(iid) references item(iid));

CREATE TABLE postsItems (
    iid,
    pid, 
    foreign key(iid) references item(iid),
    foreign key(pid) references post(pid));
