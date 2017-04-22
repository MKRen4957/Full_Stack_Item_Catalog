from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Categories, Items, Users

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = Users(name="Robo Barista", email="tinnyTim@udacity.com")
session.add(User1)
session.commit()

# Categories for the catalog
soccer = Categories(name = "Soccer", user_id = 1)
session.add(soccer)
session.commit()

basketball = Categories(name = "Basketball", user_id = 1)
session.add(basketball)
session.commit()

baseball = Categories(name = "Baseball", user_id = 1)
session.add(baseball)
session.commit()

frisbee = Categories(name = "Frisbee", user_id = 1)
session.add(frisbee)
session.commit()

snowboarding = Categories(name = "Snowboarding", user_id = 1)
session.add(snowboarding)
session.commit()

rockclimbing = Categories(name = "Rock Climbing", user_id = 1)
session.add(rockclimbing)
session.commit()

foosball = Categories(name = "Foosball", user_id = 1)
session.add(foosball)
session.commit()

skating = Categories(name = "Skating", user_id = 1)
session.add(skating)
session.commit()

hockey = Categories(name = "Hockey", user_id = 1)
session.add(hockey)
session.commit()
