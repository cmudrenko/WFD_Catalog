from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Days, MealOption, User

# Intiate database and provide shortcuts to update database with new meals
engine = create_engine('sqlite:///whatsfordinner.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a user
User1 = User(
            name="Chris Mudrenko",
            email="sara.mudrenko@gmail.com")
session.add(User1)
session.commit()

# Create Days of the Week and Unassigned Meals
category1 = Days(user_id=1, name="Monday")
session.add(category1)
session.commit()

category2 = Days(user_id=1, name="Tuesday")
session.add(category2)
session.commit()

category3 = Days(user_id=1, name="Wednesday")
session.add(category3)
session.commit()

category4 = Days(user_id=1, name="Thursday")
session.add(category4)
session.commit()

category5 = Days(user_id=1, name="Friday")
session.add(category5)
session.commit()

category6 = Days(user_id=1, name="Saturday")
session.add(category6)
session.commit()

category7 = Days(user_id=1, name="Sunday")
session.add(category7)
session.commit()

category8 = Days(user_id=1, name="None")
session.add(category8)
session.commit()


# Add Template meals into Days
mealOption1 = MealOption(
                        user_id=1,
                        name="Enchiladas and Refried Beans",
                        ingredients="Enchilada Sauce, "
                        "Refried Beans, Tortillas, "
                        "Mexican Cheese",
                        days=category1)
session.add(mealOption1)
session.commit()

mealOption1 = MealOption(
                        user_id=1,
                        name="Tacos and Refried Beans",
                        ingredients="Taco Sauce, "
                        "Taco Shells, Ground Turkey, "
                        "Refried Beans",
                        days=category2)
session.add(mealOption1)
session.commit()

mealOption1 = MealOption(
                        user_id=1,
                        name="Burgers and Fries",
                        ingredients="Gluten Free Buns, "
                        "Sliced Cheese, Ground Beef Patties, "
                        "Potato fries",
                        days=category3)
session.add(mealOption1)
session.commit()

mealOption1 = MealOption(
                        user_id=1,
                        name="Spaghetti and Meatballs",
                        ingredients="Ground Turkey, "
                        "Gluten Free Bread Crumbs, "
                        "Pasta Sauce, Thin Spaghetti",
                        days=category4)
session.add(mealOption1)
session.commit()

mealOption1 = MealOption(
                        user_id=1,
                        name="Steak and Potatoes",
                        ingredients="Beef steak, "
                        "Potatoes, Sour Cream, "
                        "Shredded Cheese, Bacon",
                        days=category5)
session.add(mealOption1)
session.commit()

mealOption1 = MealOption(
                        user_id=1,
                        name="Pizza",
                        ingredients="Cauliflower Crust, "
                        "Pizza Sauce, Pepperonis, "
                        "Italian Blend for Cheese",
                        days=category6)
session.add(mealOption1)
session.commit()

mealOption1 = MealOption(
                        user_id=1,
                        name="Waffles and Bacon",
                        ingredients="Gluten Free Bisquick, "
                        "Bacon, Syrup, Butter",
                        days=category7)
session.add(mealOption1)
session.commit()

mealOption1 = MealOption(
                        user_id=1,
                        name="Baked Ziti",
                        ingredients="Gluten Free Penne Pasta, "
                        "Pasta Sauce, Ricotta Cheese, "
                        "Parmeasean Cheese, Ground Turkey",
                        days=category8)
session.add(mealOption1)
session.commit()

mealOption1 = MealOption(
                        user_id=1,
                        name="Chili and Corn Bread",
                        ingredients="Ground Turkey, Chili Powder,"
                        "Diced Tomatos, Black Beans, "
                        "Gluten Free Corn Bread Mix",
                        days=category8)
session.add(mealOption1)
session.commit()


print ("Added days and meals!")
