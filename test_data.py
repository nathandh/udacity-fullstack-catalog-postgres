"""
Nathan D. Hernandez
Udacity FullStack NanoDegree

Test data population script
    - ver: 0.2  05/30/17 (PostgreSQL version)
    - ver: 0.1  05/2017
"""

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from database_setup import (Base, Category, Item, User, LoginType, Role, 
                            DATABASE)

engine = create_engine(URL(**DATABASE))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a login type
logintype = LoginType(source="google")
session.add(logintype)
session.commit()

# Create a ROLE with 'admin' permission
admin_role = Role(permission="admin")
session.add(admin_role)
session.commit()
# Regular Normal 'contributor' permission
contrib_role = Role(permission="contrib")
session.add(contrib_role)
session.commit()


# Create a sample user / assume they logged in via Google Auth
user1_roles = [admin_role, contrib_role]
user1 = User(logintype_id=logintype.id, roles=user1_roles,
             email="nathandhernandez@gmail.com")
session.add(user1)
session.commit()

# Create some test Category objects
cat1 = Category(name="Soccer",
                description=("A globally popular ball game in "
                             "which feet dominate play and scoring"),
                created_by=user1.id)
session.add(cat1)
session.commit()

cat2 = Category(name="Basketball",
                description=("A hoop/ball game with major "
                             "popularity in the United States"),
                created_by=user1.id)
session.add(cat2)
session.commit()

cat3 = Category(name="Baseball",
                description=("An American classic ball and bat game."),
                created_by=user1.id)
session.add(cat3)
session.commit()

cat4 = Category(name="Hockey",
                description=("Ice game played with a round "
                             "puck and a hockey stick."),
                created_by=user1.id)
session.add(cat4)
session.commit()

# Add some items to Categories
item1 = Item(name="Hoop & Net",
             description=("Brand new hoop with net. Made in USA."),
             created_by=user1.id,
             category_id=cat2.id)
session.add(item1)
session.commit()

item2 = Item(name="Shinguards",
             description=("To protect your shins during play"),
             created_by=user1.id,
             category_id=cat1.id)
session.add(item2)
session.commit()

item3 = Item(name="Wooden Bat",
             description="Made in USA wooden bat.",
             created_by=user1.id,
             category_id=cat3.id)
session.add(item3)
session.commit()

item4 = Item(name="Basketball",
             description="Leather NBA official basketball",
             created_by=user1.id,
             category_id=cat2.id)
session.add(item4)
session.commit()

item5 = Item(name="Hard Ball",
             description=("Hardball round baseball for "
                          "game play. Ages 8+."),
             created_by=user1.id,
             category_id=cat3.id)
session.add(item5)
session.commit()

item6 = Item(name="Standing Field Goal",
             description=("Standard size goal for "
                          "use in soccer. "
                          "Appropriate for all "
                          "ages."),
             created_by=user1.id,
             category_id=cat1.id)
session.add(item6)
session.commit()

item7 = Item(name="Batter's Helmet",
             description=("Hard topped helmet for "
                          "head protection when "
                          "batting."),
             created_by=user1.id,
             category_id=cat3.id)
session.add(item7)
session.commit()

item8 = Item(name="Round Puck",
             description=("Round puck (varying color) for "
                          "use on ICE surfaces."),
             created_by=user1.id,
             category_id=cat4.id)
session.add(item8)
session.commit()

item9 = Item(name="Hockey Stick",
             description=("League play hockey stick for "
                          "use on ICE surfaces."),
             created_by=user1.id,
             category_id=cat4.id)
session.add(item9)
session.commit()

item10 = Item(name="Catcher's Glove",
              description=("Glove specifically "
                           "designed for a catcher."),
              created_by=user1.id,
              category_id=cat3.id)
session.add(item10)
session.commit()

item11 = Item(name="Set of BASES",
              description=("A set of standard size bases "
                           "for baseball. Includes: 1st "
                           "base, 2nd base, 3rd base, "
                           "and HOME."),
              created_by=user1.id,
              category_id=cat3.id)
session.add(item11)
session.commit()

item12 = Item(name="Ref Court Whistle",
              description=("NBA referree court whistle."),
              created_by=user1.id,
              category_id=cat2.id)
session.add(item12)
session.commit()

print "Populated TEST catalog/item/user data!"
