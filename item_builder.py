from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, User, Item

#engine = create_engine('postgresql+psycopg2://catalog:student@localhost:5432/stuff')
engine = create_engine('sqlite:///itemdb.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Create dummy user
user1 = User(name="Gaurav Rai", email="grai.dai@gmail.com",
             picture="https:\//images.unsplash.com/flagged/photo-1506521757945-f\
             6376c050d76?ixlib=rb-0.3.5&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=\
             1080&fit=max&s=81983720d36c98b68348655f21859e9b")
session.add(user1)
session.commit()

# Items in Soccer
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

soccerItem1 = Item(
            user_id=1, name="Adidas Gloro",
            description="The ball for the world cup",
            category=category1,
            picture="https:\//upload.wikimedia.org/wikipedia/co\
            mmons/thumb/d/d3/Soccerball.svg/313px-Soccerball.svg.png")
session.add(soccerItem1)
session.commit()

soccerItem2 = Item(
            user_id=1, name="Nike Pureshot",
            description="The balls in your wet dreams",
            category=category1,
            picture="https:\//upload.wikimedia.org/wikipedia/co\
            mmons/thumb/d/d3/Soccerball.svg/313px-Soccerball.svg.png")
session.add(soccerItem2)
session.commit()

# Items in Boxing
category2 = Category(name="Boxing")

session.add(category2)
session.commit()

boxingItem1 = Item(
            user_id=1, name="Golden Gloves",
            description="Not the golden gloves from the world cup",
            category=category2,
            picture="https:\//upload.wikimedia.org/wikipedia/co\
            mmons/9/94/HJRK_A_7_-_Gauntlets_of_Maximilian_I%2C_c._1514.jpg")
session.add(boxingItem1)
session.commit()

boxingItem2 = Item(
            user_id=1, name="Featherlight Shoes",
            description="The shoes are made to last forever \
            but also be light weight and also be soft in touch",
            category=category2,
            picture="https:\//upload.wikimedia.org/wikipedia/commons/8/86/S\
            alted_Lake_%28Salt_Crystal_Shoes_on_a_Frozen_Lake%29.jpg")
session.add(boxingItem2)
session.commit()


# Items in Fussball
category3 = Category(name="Fussball")

session.add(category3)
session.commit()

fussballItem1 = Item(
              user_id=1, name="Skin Deep Gloves",
              description="These gloves are especially for the big han\
              d-eye-coordination, but less in physical activity like running",
              category=category3,
              picture="https:\//upload.wikimedia.org/wikipedia/co\
              mmons/c/c8/Baby_foot_artlibre_jnl.jpg")
session.add(fussballItem1)
session.commit()
#DBSession.remove()
print "items added!"
