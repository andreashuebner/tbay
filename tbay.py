from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float,ForeignKey

engine = create_engine('postgresql://action:action@localhost:5432/tbay')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    userId = Column(Integer, ForeignKey('users.id'),
                             nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    bids = relationship("Bid",backref = "items")
    
    
def add_item(name,description,userId):
    #if item with same name exists already for same usersid, just return the existing item
    existingItemId = 0
    existing_items=session.query(Item.id).filter(Item.name == name,Item.userId == userId).all()
    
    for item in existing_items:
        existingItemId = item.id
        
    if existingItemId != 0:
        return item #if item with same name already exists for same user id, just return the existing item
    item = Item()
    item.name = name
    item.description = description
    item.userId = userId
    session.add(item)
    session.commit()
    return item
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    items = relationship("Item", backref="users")
    bids = relationship("Bid",backref="users")
    
class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer,primary_key=True)
    itemId = Column(Integer,ForeignKey('items.id'),nullable=False)
    userId = Column(Integer,ForeignKey('users.id'),nullable=False)
    price = Column(Float,nullable=False)
    
def place_bid(session,item,userMakingBidding,price):
    '''
    Make bid on existing item. 
    
    Args:
        session {object} Database session object
        item {instance of Item} Name of item to bid on
        userOwnerItem {instance of User} Owner of the item
        userMakingBidding {instance of User} User making the bid
        price {float} Price to bidd
    ''' 
    
    #Do not allow identical bids
    existingBiddingId = 0
    existingBids = session.query(Bid.id).filter(Bid.itemId == item.id,Bid.price == price) 
    numberIdenticalBids = 0
    for existingBid in existingBids:
        numberIdenticalBids += 1
    
    if numberIdenticalBids > 0:
        return
    
    bid = Bid()
    bid.itemId = item.id
    bid.userId = userMakingBidding.id
    bid.price = price
    session.add(bid)
    session.commit()
    
    

def add_user(session,username,password):
    ''' Adds a new dataset to User. If a user with the same name already exists,
    then the existing user will be updated instead of creating a new one
    '''
    
    #First query existing users to check whether username aleady exists
    existing_users=session.query(User.id).filter(User.username == username).all()
    idExistingUser = 0
    for user in existing_users:
        idExistingUser = user.id
        
    #if idExistingUser != 0, then user already exists, in this case, we only update
    #otherwise create new user
    
    if idExistingUser != 0:
        userToUpdate = session.query(User).get(idExistingUser)
        userToUpdate.password = password
        session.commit()
        return userToUpdate
        
    else:
        newUser = User(username = username,password = password)
        session.add(newUser)
        session.commit()
        return newUser
    

def main():
    #add three users to the database
    user1 = add_user(session,"Andreas", "123")
    user2 = add_user(session,"Peter", "456")
    user3 = add_user(session,"Andrea", "789")
    
    users = session.query(User).all()
    for user in users:
        print user.username
        print user.password
        print user.id
        
    #Let user Peter create auction for baseball item
    add_item("Baseball", "A test baseball", user2.id)
    items = session.query(Item).all()
    for item in items:
        print item.name
        print item.description
        
    #User Andreas makes bid
    place_bid(session, item, user1,38.99)
    #User Andrea makes bid
    place_bid(session,item,user3,50.38)
    
    #show existing bids
    bids = session.query(Bid).all()
    for bid in bids:
        itemId = bid.itemId
        userId = bid.userId
        user = session.query(User).get(userId)
        item = session.query(Item).get(itemId)
        itemName = item.name
        userName = user.username
        print("Current bids for item " + itemName)
        print("Bid by user " + userName)
        print("Made bid of " + str(bid.price))

Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()