from uagents import Context, Model, Protocol
from uagents.network import wait_for_tx_to_complete
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
import os,re,json,sys,time
from typing import List
from backend.src.utils.exception import customException

#For getting the current date, location of the users
from datetime import datetime
import geocoder
 
makeOrder=Protocol(name="Make Orders",version="1.0")
sendOrder=Protocol("Sending the confirmed order to restaurant",version="1.0")
getResConfirm=Protocol(name="Getting Restaurant Confirmation",version="1.0")
orderPickupConfirm=Protocol(name="Valet Agent Delivery",version="1.0")
confirmDelivery=Protocol(name="Confirming whether the valet has delivered or not",version="1.0")

MASTER="agent1qturspnj7cpr2z9axv8pkrlwpqyre63pj2j3e3pewacyq3x3wur57e8czsm"

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

DEL_ADDRESS=os.getenv("DEL_ADDRESS")
RES_ADDRESS=os.getenv("RES_ADDRESS")
 
class UserPrompt(Model):
    prompt:str

class Response(Model):
    response:str

class OrderDetails(Model):
    location:list
    date:str
    restaurant:str
    order:list
    max_price:float

class Confirm(Model):
    confirm:bool

class AcceptOrder(Model):
    orderID:str
    totalCost:float
    status:bool
    message:str

class OrderPickupMessage(Model):
    deliveryPartner:str
    message:str

class Acknowledgment(Model):
    message:str
    final_bill:float

class ValetDelivery(Model):
    orderID:str
    delivered:str

DENOM = "atestfet"  #Since we are in dev phase

def agent_location() -> list:
    '''
    This function returns the location of the agent using IP address.
    '''
    try:
        g = geocoder.ip('me')
 
        agent_loc = g.latlng
    except Exception as e:
        raise customException(e,sys)

    return agent_loc

def testAgent(req):
    # Test the agent_location function
    return req
 
@makeOrder.on_query(model=UserPrompt,replies=OrderDetails)
async def make_Order(ctx:Context,sender:str,p:UserPrompt):
    '''
    This function handles the messages from the user and prepares the order according to the user requirements.
    '''
    current_loc=agent_location()
    # restaurant data context for the llm
    #incase of utilising an API, the api response can directly be requested from here
    context=[
'{"data": {"About": {"Name": "Bistro Bliss", "Ratings": 4.7, "Locality": "Pallavaram", "AreaName": "Kotturpuram", "City": "Chennai", "Cuisines": ["Japanese", "Thai"]}, "Menu": {"Starters": [{"name": "Garlic Bread", "description": "Toasted bread with garlic butter.", "isVeg": true, "price": 488, "inStock": false}, {"name": "Stuffed Mushrooms", "description": "Mushrooms filled with cheese and herbs, baked to perfection.", "isVeg": true, "price": 188, "inStock": true}], "Main Course": [{"name": "Thai Green Curry", "description": "Spicy green curry with vegetables and basil.", "isVeg": true, "price": 454, "inStock": false}, {"name": "Grilled Salmon", "description": "Salmon fillet grilled to perfection.", "isVeg": false, "price": 285, "inStock": false}, {"name": "Chicken Alfredo Pasta", "description": "Fettuccine pasta tossed in a creamy Alfredo sauce with grilled chicken.", "isVeg": false, "price": 196, "inStock": true}, {"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": true, "price": 296, "inStock": true}, {"name": "Beef Stroganoff", "description": "Tender beef strips in a creamy mushroom sauce.", "isVeg": false, "price": 253, "inStock": true}, {"name": "Veg Biryani", "description": "Aromatic rice dish with mixed vegetables and spices.", "isVeg": true, "price": 518, "inStock": true}, {"name": "Spaghetti Carbonara", "description": "Pasta in a creamy carbonara sauce with pancetta and Parmesan.", "isVeg": false, "price": 521, "inStock": true}], "Desserts": [{"name": "Ice Cream Sundae", "description": "Vanilla ice cream with chocolate syrup and nuts.", "isVeg": true, "price": 347, "inStock": true}], "Beverages": [{"name": "Herbal Tea", "description": "Caffeine-free herbal tea with calming properties.", "isVeg": true, "price": 408, "inStock": true}, {"name": "Lemonade", "description": "Fresh lemonade with a hint of mint.", "isVeg": true, "price": 340, "inStock": false}, {"name": "Mango Smoothie", "description": "Refreshing smoothie made with fresh mangoes.", "isVeg": true, "price": 170, "inStock": true}, {"name": "Fruit Punch", "description": "Refreshing mix of fruit juices and soda.", "isVeg": true, "price": 521, "inStock": false}, {"name": "Green Tea", "description": "Healthy and soothing green tea.", "isVeg": true, "price": 276, "inStock": false}, {"name": "Iced Coffee", "description": "Chilled coffee with a hint of cream.", "isVeg": true, "price": 305, "inStock": false}, {"name": "Espresso", "description": "Strong and rich coffee.", "isVeg": true, "price": 248, "inStock": true}, {"name": "Cappuccino", "description": "Espresso with steamed milk and foam.", "isVeg": true, "price": 596, "inStock": true}], "Salads": [{"name": "Caprese Salad", "description": "Sliced tomatoes, mozzarella, and basil with balsamic glaze.", "isVeg": true, "price": 128, "inStock": true}, {"name": "Greek Salad", "description": "Tomatoes, cucumbers, olives, and feta cheese with Greek dressing.", "isVeg": true, "price": 405, "inStock": true}, {"name": "Caesar Salad", "description": "Crisp romaine lettuce with Caesar dressing, croutons, and Parmesan.", "isVeg": true, "price": 369, "inStock": true}, {"name": "Coleslaw", "description": "Shredded cabbage and carrots with a creamy dressing.", "isVeg": true, "price": 430, "inStock": false}], "Sandwiches": [{"name": "BLT Sandwich", "description": "Bacon, lettuce, and tomato on toasted bread.", "isVeg": false, "price": 209, "inStock": true}, {"name": "Tuna Sandwich", "description": "Tuna salad sandwich with lettuce and tomato.", "isVeg": false, "price": 253, "inStock": true}, {"name": "Club Sandwich", "description": "Triple-decker sandwich with chicken, bacon, lettuce, and tomato.", "isVeg": false, "price": 552, "inStock": false}, {"name": "Chicken Panini", "description": "Grilled chicken, cheese, and vegetables pressed in a panini.", "isVeg": false, "price": 326, "inStock": true}, {"name": "Veggie Wrap", "description": "Wrap filled with fresh vegetables and a creamy dressing.", "isVeg": true, "price": 501, "inStock": true}], "Pizza": [{"name": "Four Cheese Pizza", "description": "Pizza with a blend of four cheeses.", "isVeg": true, "price": 552, "inStock": false}, {"name": "Veggie Pizza", "description": "Pizza loaded with a variety of vegetables.", "isVeg": true, "price": 480, "inStock": true}, {"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": true, "price": 490, "inStock": true}, {"name": "Pepperoni Pizza", "description": "Pizza topped with spicy pepperoni slices.", "isVeg": false, "price": 578, "inStock": true}], "Pasta": [{"name": "Penne Arrabbiata", "description": "Penne pasta in a spicy tomato sauce.", "isVeg": true, "price": 510, "inStock": false}, {"name": "Spaghetti Carbonara", "description": "Pasta in a creamy carbonara sauce with pancetta and Parmesan.", "isVeg": false, "price": 233, "inStock": false}, {"name": "Fettuccine Alfredo", "description": "Creamy Alfredo sauce with fettuccine pasta.", "isVeg": true, "price": 380, "inStock": false}], "Burgers": [{"name": "Bacon Cheeseburger", "description": "Beef patty with bacon, cheese, lettuce, and tomato.", "isVeg": false, "price": 201, "inStock": false}]}}}',
'{"data": {"About": {"Name": "Taste Paradise", "Ratings": 3.9, "Locality": "Perambur", "AreaName": "Besant Nagar", "City": "Chennai", "Cuisines": ["Lebanese", "Turkish"]}, "Menu": {"Starters": [{"name": "Stuffed Mushrooms", "description": "Mushrooms filled with cheese and herbs, baked to perfection.", "isVeg": true, "price": 188, "inStock": true}, {"name": "Chicken Wings", "description": "Spicy and tangy chicken wings.", "isVeg": false, "price": 364, "inStock": true}, {"name": "Spring Rolls", "description": "Crispy rolls filled with vegetables.", "isVeg": true, "price": 543, "inStock": false}], "Main Course": [{"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": true, "price": 296, "inStock": true}, {"name": "Grilled Salmon", "description": "Salmon fillet grilled to perfection.", "isVeg": false, "price": 285, "inStock": false}, {"name": "Thai Green Curry", "description": "Spicy green curry with vegetables and basil.", "isVeg": true, "price": 454, "inStock": false}], "Desserts": [{"name": "Cheesecake", "description": "Creamy cheesecake with a graham cracker crust.", "isVeg": true, "price": 100, "inStock": false}, {"name": "Chocolate Lava Cake", "description": "Warm chocolate cake with a gooey center.", "isVeg": true, "price": 253, "inStock": true}, {"name": "Tiramisu", "description": "Layered dessert with coffee-soaked ladyfingers and mascarpone cheese.", "isVeg": true, "price": 203, "inStock": true}, {"name": "Panna Cotta", "description": "Italian creamy dessert with a vanilla flavor.", "isVeg": true, "price": 472, "inStock": false}, {"name": "Fruit Tart", "description": "Pastry tart filled with custard and topped with fresh fruits.", "isVeg": true, "price": 567, "inStock": false}, {"name": "Apple Pie", "description": "Classic apple pie with a flaky crust and spiced apple filling.", "isVeg": true, "price": 127, "inStock": false}], "Beverages": [{"name": "Lemonade", "description": "Fresh lemonade with a hint of mint.", "isVeg": true, "price": 340, "inStock": false}, {"name": "Mango Smoothie", "description": "Refreshing smoothie made with fresh mangoes.", "isVeg": true, "price": 170, "inStock": true}, {"name": "Fruit Punch", "description": "Refreshing mix of fruit juices and soda.", "isVeg": true, "price": 521, "inStock": false}, {"name": "Cappuccino", "description": "Espresso with steamed milk and foam.", "isVeg": true, "price": 596, "inStock": true}, {"name": "Espresso", "description": "Strong and rich coffee.", "isVeg": true, "price": 248, "inStock": true}, {"name": "Iced Coffee", "description": "Chilled coffee with a hint of cream.", "isVeg": true, "price": 305, "inStock": false}], "Salads": [{"name": "Caprese Salad", "description": "Sliced tomatoes, mozzarella, and basil with balsamic glaze.", "isVeg": true, "price": 128, "inStock": true}, {"name": "Coleslaw", "description": "Shredded cabbage and carrots with a creamy dressing.", "isVeg": true, "price": 430, "inStock": false}, {"name": "Greek Salad", "description": "Tomatoes, cucumbers, olives, and feta cheese with Greek dressing.", "isVeg": true, "price": 405, "inStock": true}, {"name": "Caesar Salad", "description": "Crisp romaine lettuce with Caesar dressing, croutons, and Parmesan.", "isVeg": true, "price": 369, "inStock": true}, {"name": "Quinoa Salad", "description": "Quinoa mixed with vegetables and a tangy vinaigrette.", "isVeg": true, "price": 571, "inStock": true}], "Sandwiches": [{"name": "Chicken Panini", "description": "Grilled chicken, cheese, and vegetables pressed in a panini.", "isVeg": false, "price": 326, "inStock": true}, {"name": "Veggie Wrap", "description": "Wrap filled with fresh vegetables and a creamy dressing.", "isVeg": true, "price": 501, "inStock": true}, {"name": "Club Sandwich", "description": "Triple-decker sandwich with chicken, bacon, lettuce, and tomato.", "isVeg": false, "price": 552, "inStock": false}, {"name": "Tuna Sandwich", "description": "Tuna salad sandwich with lettuce and tomato.", "isVeg": false, "price": 253, "inStock": true}], "Pizza": [{"name": "Pepperoni Pizza", "description": "Pizza topped with spicy pepperoni slices.", "isVeg": false, "price": 578, "inStock": true}, {"name": "BBQ Chicken Pizza", "description": "Pizza with BBQ sauce, grilled chicken, and onions.", "isVeg": false, "price": 586, "inStock": true}, {"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": true, "price": 490, "inStock": true}], "Pasta": [{"name": "Pesto Pasta", "description": "Pasta tossed with basil pesto sauce.", "isVeg": true, "price": 165, "inStock": false}, {"name": "Fettuccine Alfredo", "description": "Creamy Alfredo sauce with fettuccine pasta.", "isVeg": true, "price": 380, "inStock": false}], "Burgers": [{"name": "Classic Cheeseburger", "description": "Beef patty with cheese, lettuce, and tomato.", "isVeg": false, "price": 367, "inStock": false}, {"name": "Chicken Burger", "description": "Grilled chicken patty with lettuce and mayo.", "isVeg": false, "price": 445, "inStock": true}, {"name": "Bacon Cheeseburger", "description": "Beef patty with bacon, cheese, lettuce, and tomato.", "isVeg": false, "price": 201, "inStock": false}, {"name": "Veggie Burger", "description": "Vegetarian patty with lettuce, tomato, and cheese.", "isVeg": true, "price": 482, "inStock": false}, {"name": "BBQ Burger", "description": "Beef patty with BBQ sauce and crispy onions.", "isVeg": false, "price": 539, "inStock": true}]}}}',
'{"data": {"About": {"Name": "Savory Delights", "Ratings": 3.5, "Locality": "Kodambakkam", "AreaName": "T. Nagar", "City": "Chennai", "Cuisines": ["Greek", "Indian"]}, "Menu": {"Starters": [{"name": "Chicken Skewers", "description": "Grilled chicken skewers with a savory marinade.", "isVeg": false, "price": 381, "inStock": false}, {"name": "Bruschetta", "description": "Grilled bread topped with fresh tomatoes and basil.", "isVeg": true, "price": 332, "inStock": false}, {"name": "Chicken Wings", "description": "Spicy and tangy chicken wings.", "isVeg": false, "price": 364, "inStock": true}, {"name": "Garlic Bread", "description": "Toasted bread with garlic butter.", "isVeg": true, "price": 488, "inStock": false}, {"name": "Nachos with Cheese", "description": "Crispy nachos topped with melted cheese.", "isVeg": true, "price": 293, "inStock": false}, {"name": "Stuffed Mushrooms", "description": "Mushrooms filled with cheese and herbs, baked to perfection.", "isVeg": true, "price": 188, "inStock": true}], "Main Course": [{"name": "Veg Biryani", "description": "Aromatic rice dish with mixed vegetables and spices.", "isVeg": true, "price": 518, "inStock": true}, {"name": "Thai Green Curry", "description": "Spicy green curry with vegetables and basil.", "isVeg": true, "price": 454, "inStock": false}, {"name": "Chicken Alfredo Pasta", "description": "Fettuccine pasta tossed in a creamy Alfredo sauce with grilled chicken.", "isVeg": false, "price": 196, "inStock": true}, {"name": "Beef Stroganoff", "description": "Tender beef strips in a creamy mushroom sauce.", "isVeg": false, "price": 253, "inStock": true}, {"name": "Spaghetti Carbonara", "description": "Pasta in a creamy carbonara sauce with pancetta and Parmesan.", "isVeg": false, "price": 521, "inStock": true}, {"name": "Grilled Salmon", "description": "Salmon fillet grilled to perfection.", "isVeg": false, "price": 285, "inStock": false}, {"name": "Paneer Butter Masala", "description": "Paneer cubes cooked in a rich tomato and cream sauce.", "isVeg": true, "price": 214, "inStock": true}], "Desserts": [{"name": "Brownies", "description": "Rich and fudgy chocolate brownies.", "isVeg": true, "price": 582, "inStock": false}, {"name": "Chocolate Lava Cake", "description": "Warm chocolate cake with a gooey center.", "isVeg": true, "price": 253, "inStock": true}, {"name": "Ice Cream Sundae", "description": "Vanilla ice cream with chocolate syrup and nuts.", "isVeg": true, "price": 347, "inStock": true}, {"name": "Tiramisu", "description": "Layered dessert with coffee-soaked ladyfingers and mascarpone cheese.", "isVeg": true, "price": 203, "inStock": true}, {"name": "Apple Pie", "description": "Classic apple pie with a flaky crust and spiced apple filling.", "isVeg": true, "price": 127, "inStock": false}, {"name": "Fruit Tart", "description": "Pastry tart filled with custard and topped with fresh fruits.", "isVeg": true, "price": 567, "inStock": false}], "Beverages": [{"name": "Lemonade", "description": "Fresh lemonade with a hint of mint.", "isVeg": true, "price": 340, "inStock": false}, {"name": "Espresso", "description": "Strong and rich coffee.", "isVeg": true, "price": 248, "inStock": true}, {"name": "Mango Smoothie", "description": "Refreshing smoothie made with fresh mangoes.", "isVeg": true, "price": 170, "inStock": true}, {"name": "Herbal Tea", "description": "Caffeine-free herbal tea with calming properties.", "isVeg": true, "price": 408, "inStock": true}, {"name": "Cappuccino", "description": "Espresso with steamed milk and foam.", "isVeg": true, "price": 596, "inStock": true}, {"name": "Fruit Punch", "description": "Refreshing mix of fruit juices and soda.", "isVeg": true, "price": 521, "inStock": false}], "Salads": [{"name": "Greek Salad", "description": "Tomatoes, cucumbers, olives, and feta cheese with Greek dressing.", "isVeg": true, "price": 405, "inStock": true}, {"name": "Caprese Salad", "description": "Sliced tomatoes, mozzarella, and basil with balsamic glaze.", "isVeg": true, "price": 128, "inStock": true}], "Sandwiches": [{"name": "Chicken Panini", "description": "Grilled chicken, cheese, and vegetables pressed in a panini.", "isVeg": false, "price": 326, "inStock": true}, {"name": "Tuna Sandwich", "description": "Tuna salad sandwich with lettuce and tomato.", "isVeg": false, "price": 253, "inStock": true}], "Pizza": [{"name": "Veggie Pizza", "description": "Pizza loaded with a variety of vegetables.", "isVeg": true, "price": 480, "inStock": true}, {"name": "Pepperoni Pizza", "description": "Pizza topped with spicy pepperoni slices.", "isVeg": false, "price": 578, "inStock": true}, {"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": true, "price": 490, "inStock": true}, {"name": "Four Cheese Pizza", "description": "Pizza with a blend of four cheeses.", "isVeg": true, "price": 552, "inStock": false}, {"name": "BBQ Chicken Pizza", "description": "Pizza with BBQ sauce, grilled chicken, and onions.", "isVeg": false, "price": 586, "inStock": true}], "Pasta": [{"name": "Penne Arrabbiata", "description": "Penne pasta in a spicy tomato sauce.", "isVeg": true, "price": 510, "inStock": false}, {"name": "Fettuccine Alfredo", "description": "Creamy Alfredo sauce with fettuccine pasta.", "isVeg": true, "price": 380, "inStock": false}, {"name": "Lasagna", "description": "Layered pasta with meat sauce and cheese.", "isVeg": false, "price": 130, "inStock": true}, {"name": "Pesto Pasta", "description": "Pasta tossed with basil pesto sauce.", "isVeg": true, "price": 165, "inStock": false}], "Burgers": [{"name": "Chicken Burger", "description": "Grilled chicken patty with lettuce and mayo.", "isVeg": false, "price": 445, "inStock": true}, {"name": "Veggie Burger", "description": "Vegetarian patty with lettuce, tomato, and cheese.", "isVeg": true, "price": 482, "inStock": false}, {"name": "Classic Cheeseburger", "description": "Beef patty with cheese, lettuce, and tomato.", "isVeg": false, "price": 367, "inStock": false}, {"name": "BBQ Burger", "description": "Beef patty with BBQ sauce and crispy onions.", "isVeg": false, "price": 539, "inStock": true}]}}}',
'{"data": {"About": {"Name": "Gastronomy Grove", "Ratings": 3.7, "Locality": "Nandambakkam", "AreaName": "Sholinganallur", "City": "Chennai", "Cuisines": ["Mediterranean", "Greek"]}, "Menu": {"Starters": [{"name": "Stuffed Mushrooms", "description": "Mushrooms filled with cheese and herbs, baked to perfection.", "isVeg": true, "price": 188, "inStock": true}, {"name": "Garlic Bread", "description": "Toasted bread with garlic butter.", "isVeg": true, "price": 488, "inStock": false}, {"name": "Chicken Wings", "description": "Spicy and tangy chicken wings.", "isVeg": false, "price": 364, "inStock": true}, {"name": "Nachos with Cheese", "description": "Crispy nachos topped with melted cheese.", "isVeg": true, "price": 293, "inStock": false}, {"name": "Bruschetta", "description": "Grilled bread topped with fresh tomatoes and basil.", "isVeg": true, "price": 332, "inStock": false}, {"name": "Veg Pakoras", "description": "Vegetables dipped in chickpea flour batter and fried.", "isVeg": true, "price": 255, "inStock": true}, {"name": "Spring Rolls", "description": "Crispy rolls filled with vegetables.", "isVeg": true, "price": 543, "inStock": false}], "Main Course": [{"name": "Grilled Salmon", "description": "Salmon fillet grilled to perfection.", "isVeg": false, "price": 285, "inStock": false}, {"name": "Spaghetti Carbonara", "description": "Pasta in a creamy carbonara sauce with pancetta and Parmesan.", "isVeg": false, "price": 521, "inStock": true}, {"name": "Chicken Alfredo Pasta", "description": "Fettuccine pasta tossed in a creamy Alfredo sauce with grilled chicken.", "isVeg": false, "price": 196, "inStock": true}, {"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": true, "price": 296, "inStock": true}], "Desserts": [{"name": "Ice Cream Sundae", "description": "Vanilla ice cream with chocolate syrup and nuts.", "isVeg": true, "price": 347, "inStock": true}, {"name": "Brownies", "description": "Rich and fudgy chocolate brownies.", "isVeg": true, "price": 582, "inStock": false}, {"name": "Fruit Tart", "description": "Pastry tart filled with custard and topped with fresh fruits.", "isVeg": true, "price": 567, "inStock": false}], "Beverages": [{"name": "Herbal Tea", "description": "Caffeine-free herbal tea with calming properties.", "isVeg": true, "price": 408, "inStock": true}, {"name": "Lemonade", "description": "Fresh lemonade with a hint of mint.", "isVeg": true, "price": 340, "inStock": false}, {"name": "Mango Smoothie", "description": "Refreshing smoothie made with fresh mangoes.", "isVeg": true, "price": 170, "inStock": true}, {"name": "Fruit Punch", "description": "Refreshing mix of fruit juices and soda.", "isVeg": true, "price": 521, "inStock": false}, {"name": "Cappuccino", "description": "Espresso with steamed milk and foam.", "isVeg": true, "price": 596, "inStock": true}, {"name": "Iced Coffee", "description": "Chilled coffee with a hint of cream.", "isVeg": true, "price": 305, "inStock": false}], "Salads": [{"name": "Caprese Salad", "description": "Sliced tomatoes, mozzarella, and basil with balsamic glaze.", "isVeg": true, "price": 128, "inStock": true}, {"name": "Greek Salad", "description": "Tomatoes, cucumbers, olives, and feta cheese with Greek dressing.", "isVeg": true, "price": 405, "inStock": true}, {"name": "Coleslaw", "description": "Shredded cabbage and carrots with a creamy dressing.", "isVeg": true, "price": 430, "inStock": false}, {"name": "Quinoa Salad", "description": "Quinoa mixed with vegetables and a tangy vinaigrette.", "isVeg": true, "price": 571, "inStock": true}, {"name": "Caesar Salad", "description": "Crisp romaine lettuce with Caesar dressing, croutons, and Parmesan.", "isVeg": true, "price": 369, "inStock": true}], "Sandwiches": [{"name": "BLT Sandwich", "description": "Bacon, lettuce, and tomato on toasted bread.", "isVeg": false, "price": 209, "inStock": true}], "Pizza": [{"name": "Veggie Pizza", "description": "Pizza loaded with a variety of vegetables.", "isVeg": true, "price": 480, "inStock": true}, {"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": true, "price": 490, "inStock": true}, {"name": "Pepperoni Pizza", "description": "Pizza topped with spicy pepperoni slices.", "isVeg": false, "price": 578, "inStock": true}], "Pasta": [{"name": "Spaghetti Carbonara", "description": "Pasta in a creamy carbonara sauce with pancetta and Parmesan.", "isVeg": false, "price": 233, "inStock": false}, {"name": "Pesto Pasta", "description": "Pasta tossed with basil pesto sauce.", "isVeg": true, "price": 165, "inStock": false}, {"name": "Fettuccine Alfredo", "description": "Creamy Alfredo sauce with fettuccine pasta.", "isVeg": true, "price": 380, "inStock": false}, {"name": "Penne Arrabbiata", "description": "Penne pasta in a spicy tomato sauce.", "isVeg": true, "price": 510, "inStock": false}, {"name": "Lasagna", "description": "Layered pasta with meat sauce and cheese.", "isVeg": false, "price": 130, "inStock": true}], "Burgers": [{"name": "BBQ Burger", "description": "Beef patty with BBQ sauce and crispy onions.", "isVeg": false, "price": 539, "inStock": true}]}}}',
    ]
    
    llm=ChatGroq(temperature=0,model="llama3-70b-8192",api_key=GROQ_API_KEY)
    chat_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                "You are a friendly health assistant, who helps users to find the perfect food items based on their specific needs and preferences. "
                "You must suggest delicious and nutritious options to keep them feeling their best. "
                "You must choose the food items only from a single restaurant. This is a mandatory instruction which must not be violated."
                "The output must be in JSON format. You must answer in this format: "
                '{"Restaurant" : <value>, "Locality": <value>, "AreaName": <value>, "Dishes" :["itemname": <value>,"description": <value>,"itemcost": <value>]}'
                "The key names must be the same as given in the prompt"
                "The placeholders <value> must be filled with the correct data from the given context and should not be left as 'None'."
                "The output must be a proper meal rather than a list of dishes from the best available restaurant."
                "Strictly, stick to the provided context"
                f" Use this context to suggest the food items and restaurant: {context}"
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
    )
    chain_suggest = chat_template | llm
    llmOutput = chain_suggest.invoke({"text": p.prompt})

    response_modifier_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                "You are a helpful chat assistant."
                "You must extract neccessary information from the given prompt like Restaurant name, Dish name, Description and price."
                "The output must be a JSON"
                "Follow this format: "
                '{"Restaurant" : <value>, "Locality": <value>, "AreaName": <value>, "Dishes" :["itemname": <value>,"description": <value>,"itemcost": <value>]}'
                "The '<value> spaces must be filled with the appropriate data from the given prompt and should not be left as 'None'."
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
    )

    chain_modifier= response_modifier_template | llm
    llmOutput=chain_modifier.invoke({"text":llmOutput.content})
    json_match = re.search(r'\{.*\}', llmOutput.content, re.DOTALL)

    if json_match:
        json_string = json_match.group(0)
        
        # Parse the JSON string into a dictionary
        data_dict = json.loads(json_string)
        
        # Print the dictionary
        ctx.logger.info(f"Response: {data_dict}")
        
    else:
        ctx.logger.info(f"Response: {llmOutput.content}")
    
    restaurant=data_dict['Restaurant']
    dishes=data_dict['Dishes']
    max_price=0.0
    for dish in dishes:
        max_price+=dish['itemcost']
    
    ctx.storage.set("location",current_loc)
    ctx.storage.set("restaurant",restaurant)
    ctx.storage.set("dishes",dishes)
    ctx.storage.set("time",datetime.now().isoformat())
    ctx.storage.set("max_price",max_price)

@sendOrder.on_query(model=Confirm,replies=OrderDetails)
async def confirm_order(ctx: Context,sender:str, user_confirmation: Confirm):
    if(user_confirmation.confirm):
        await ctx.send(RES_ADDRESS, OrderDetails(location=ctx.storage.get("location"), 
                                                 date=ctx.storage.get("time"), 
                                                 restaurant=ctx.storage.get("restaurant"),
                                                 order=ctx.storage.get("dishes"), 
                                                 max_price=ctx.storage.get("max_price")))

@getResConfirm.on_message(model=AcceptOrder)
async def rest_confirm(ctx:Context, sender:str, resMessage:AcceptOrder):
    ctx.logger.info(f"Order ID: {resMessage.orderID}")
    ctx.logger.info(f"Order status: {resMessage.status}")
    ctx.logger.info(f"Total Price: {resMessage.totalCost}")
    ctx.logger.info(f"Message: {resMessage.message}")

    ctx.storage.set("orderID",resMessage.orderID)
    ctx.storage.set("status",resMessage.status)
    ctx.storage.set("totalCost",resMessage.totalCost)
    ctx.storage.set("message",resMessage.message)

@orderPickupConfirm.on_message(model=OrderPickupMessage,replies=Acknowledgment)
async def order_pickup(ctx:Context, sender:str, orderPickupMessage:OrderPickupMessage):
    ctx.logger.info(f"Valet Agent Address: {sender}")
    ctx.logger.info(f"Message: {orderPickupMessage.message}")

    ctx.storage.set("valet address",sender)
    ctx.storage.set("valet message",orderPickupMessage.message)

@confirmDelivery.on_query(model=ValetDelivery,replies=Acknowledgment)
async def confirm_delivery(ctx:Context,sender:str, valetDelivery:ValetDelivery):
    if (valetDelivery.delivered=="yes"):
        ack_message="Ordered delivered. Thank You."
        await ctx.send(DEL_ADDRESS,Acknowledgment(message=ack_message,final_bill=ctx.storage.get("totalCost")))