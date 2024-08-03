from uagents import Context, Model, Protocol
import os,sys,uuid,geocoder
from geopy.distance import geodesic

from backend.src.utils.exception import customException

DEL_ADDRESS=os.getenv("DEL_ADDRESS")
CUST_ADDRESS=os.getenv("CUST_ADDRESS")

class OrderDetails(Model):
    location:list
    date:str
    restaurant:str
    order:list
    max_price:float

class AcceptOrder(Model):
    orderID:str
    totalCost:float
    status:bool
    message:str

class ValetMessage(Model):
    orderID:str
    userloc:list
    restaurantloc:list
    message:str
    totalCost:float

class ValetConfirm(Model):
    location:list
    message:str

class OrderPickupMessage(Model):
    deliveryPartner:str
    message:str

class Confirm(Model):
    confirm:bool

class CallValet(Model):
    confirm:int

take_Orders=Protocol("Taking Orders")
acceptOrders=Protocol("Accepting user orders")
valet_Message=Protocol("Messaging the Valet Agent")
get_valet=Protocol("Handling the Valet Agent")

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

@take_Orders.on_message(model=OrderDetails)
async def recieve_Orders(ctx:Context,sender:str,newOrders:OrderDetails):
    '''
    Function to receive orders from the customer agent
    '''
    rest_loc=agent_location()
    ctx.logger.info(f"New Order received from address {sender}")
    orderID = str(uuid.uuid4())

    # Initialize lists to store dish names, descriptions, and item costs
    dish_names = []
    dish_descriptions = []
    item_costs = []

    # Loop through the dishes and append the values to the respective lists
    for dish in newOrders.order:
        try:
            dish_names.append(dish['itemname'])
        except:
            dish_names.append(dish['name'])
        dish_descriptions.append(dish['description'])
        item_costs.append(dish['itemcost'])
    
    #Logging the order details for the restuarant's reference
    ctx.logger.info(f"Order ID : {orderID}")
    ctx.logger.info(f"Customer location : {newOrders.location}")
    for i in range(len(dish_names)):
        #Display order details to the restuarant
        ctx.logger.info(f"{dish_names[i]} - {item_costs[i]}")
    ctx.logger.info(f"Total Cost: {newOrders.max_price}")

    ctx.storage.set("location",rest_loc)
    ctx.storage.set("orderID",orderID)
    ctx.storage.set("customer_agent",sender)
    ctx.storage.set("customer_location",newOrders.location)
    ctx.storage.set("restaurant",newOrders.restaurant)
    ctx.storage.set("order",newOrders.order)
    ctx.storage.set("totalCost",newOrders.max_price)
    
    extraPay=0.05*ctx.storage.get('totalCost') #takes into account, the delivery fee and the handling charges
    final_bill=ctx.storage.get('totalCost') + extraPay

    ctx.storage.set("final_bill",final_bill)

@acceptOrders.on_query(model=Confirm,replies=AcceptOrder)
async def accept_Orders(ctx:Context,sender:str,req:Confirm):

    if req.confirm:
        res_message=f"Thank you for choosing {ctx.storage.get('restaurant')}. Your order will be delivered soon..."
        extraPay=0.05*ctx.storage.get('totalCost') #takes into account, the delivery fee and the handling charges
        final_bill=ctx.storage.get('totalCost') + extraPay
        await ctx.send(CUST_ADDRESS,AcceptOrder(orderID=ctx.storage.get('orderID'),totalCost=ctx.storage.get("final_bill"),status=req.confirm,message=res_message))
        ctx.logger.info(f"Final Bill: {final_bill}")

    else:
        res_message=f"We are really sorry!! Currently we are not accepting any orders"
        await ctx.send(CUST_ADDRESS,AcceptOrder(orderID=ctx.storage.get('orderID'),totalCost=ctx.storage.get("final_bill"),status=req.confirm,message=res_message))

@valet_Message.on_query(model=CallValet,replies=ValetMessage)
async def valetMessage(ctx:Context,sender:str,req:CallValet):
    valetMessage="Order will be getting ready in few minutes..."
    await ctx.send(DEL_ADDRESS,ValetMessage(orderID=ctx.storage.get('orderID'),userloc=ctx.storage.get('customer_location'),restaurantloc=ctx.storage.get('location'),message=valetMessage,totalCost=ctx.storage.get("final_bill")))

@get_valet.on_message(model=ValetConfirm,replies=OrderPickupMessage)
async def valet_confirm_message(ctx:Context, sender:str, valetmsg:ValetConfirm):
    ctx.logger.info(f"Valet Address: {valetmsg.location}")
    ctx.logger.info(f"Valet Message: {valetmsg.message}")

    ctx.storage.set("valet address",sender)
    ctx.storage.set("valet message",valetmsg.message)
    ctx.storage.set("valet location",valetmsg.location)

    cust_message=f"Valet Agent {sender} picked up the order and will be delivering it soon..."

    await ctx.send(CUST_ADDRESS,OrderPickupMessage(deliveryPartner=sender,message=cust_message))

    




