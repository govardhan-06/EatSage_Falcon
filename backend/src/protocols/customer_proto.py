from uagents import Context, Model, Protocol
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
import os,re,json,sys,time
from typing import List
from backend.src.utils.exception import customException

AI71_BASE_URL = os.getenv("AI71_BASE_URL")
AI71_API_KEY = os.getenv("AI71_API_KEY")

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
    llm = ChatOpenAI(
        model="tiiuae/falcon-180B-chat",
        api_key=AI71_API_KEY,
        base_url=AI71_BASE_URL
    )

    # restaurant data context for the llm
    #incase of utilising an API, the api response can directly be requested from here
    background='''You are a friendly health assistant, who helps users to find the perfect food items based on their specific needs and preferences. "
    "You must suggest delicious and nutritious options to keep them feeling their best. "
    "You must choose the food items only from a single restaurant. This is a mandatory instruction which must not be violated."
    "The output must be in JSON format. You must answer in this format: "
    '{"Restaurant" : <value>, "Locality": <value>, "AreaName": <value>, "Dishes" :["itemname": <value>,"description": <value>,"itemcost": <value>]}'
    "The key names must be the same as given in the prompt"
    "The placeholders <value> must be filled with the correct data from the given context and should not be left as 'None'."
    "The output must be a proper meal rather than a list of dishes from the best available restaurant."
    "Strictly, stick to the provided context and output format must be as given below"
    "{"Restaurant": "Bistro Bliss", "Dishes": [{"itemname": "Bruschetta", "description": "Grilled bread topped with fresh tomatoes and basil", "itemcost": 332}, {"itemname": "Chicken Alfredo Pasta", "description": "Fettuccine pasta tossed in a creamy Alfredo sauce with grilled chicken", "itemcost": 196}, {"itemname": "Tiramisu", "description": "Layered dessert with coffee-soaked ladyfingers and mascarpone cheese", "itemcost": 203}, {"itemname": "Cappuccino", "description": "Espresso with steamed milk and foam", "itemcost": 596}]}"
    '''

    a=llm.invoke(
            [
                SystemMessage(content=background),
                HumanMessage(content=p.prompt),
            ]
    )

    background='''"You are a helpful chat assistant."
    "You must extract neccessary information from the given prompt like Restaurant name, Dish name, Description and price."
    "The output must be a JSON"
    "Follow this format: "
    '{"Restaurant" : <value>, "Locality": <value>, "AreaName": <value>, "Dishes" :["itemname": <value>,"description": <value>,"itemcost": <value>]}'
    "The '<value> spaces must be filled with the appropriate data from the given prompt and should not be left as 'None'."
    '''

    llmOutput=llm.invoke(
            [
                SystemMessage(content=background),
                HumanMessage(content=a.content),
            ]
    )

    print(llmOutput)
    json_match = re.search(r'\{.*\}', llmOutput.content, re.DOTALL)
    print(json_match.group(0))

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