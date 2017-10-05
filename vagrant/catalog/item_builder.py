from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, User, Item

engine = create_engine('sqlite:///itemsDatabase.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Create dummy user
user1 = User(name="Udemy Boro", email="manic@monday.com",
             picture="https://images.unsplash.com/flagged/photo-1506521757945-f\
             6376c050d76?ixlib=rb-0.3.5&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=\
             1080&fit=max&s=81983720d36c98b68348655f21859e9b")
session.add(user1)
session.commit()

# Items in Soccer
category1 = Category(name = "Soccer")

session.add(category1)
session.commit()

soccerItem1 = Item(user_id=1, name="Adidas Gloro", description="The ball for the world cup",
                   cat_id=1, picture="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Soccerball.svg/313px-Soccerball.svg.png")
session.add(soccerItem1)
session.commit()

soccerItem2 = Item(user_id=1, name="Nike Pureshot", description="The balls in your wet dreams",
                   cat_id=1, picture="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Soccerball.svg/313px-Soccerball.svg.png")
session.add(soccerItem2)
session.commit()



print "items added!"
