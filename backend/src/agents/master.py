from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low

'''
This script is used to test the functionality of the entire application
'''

import os,sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEL_ADDRESS=os.getenv("DEL_ADDRESS")
RES_ADDRESS=os.getenv("RES_ADDRESS")
CUST_ADDRESS=os.getenv("CUST_ADDRESS")

master=Agent(
    name="Master",
    port=8005,
    seed="Test",
    endpoint=["http://127.0.0.1:8005/submit"],
)

fund_agent_if_low(master.wallet.address())

class UserPrompt(Model):
    prompt:str

class OrderDetails(Model):
    location:list
    date:datetime
    restaurant:str
    order:dict
    max_price:float

@master.on_event('startup')
async def send_message(ctx:Context):
    await ctx.send(CUST_ADDRESS,UserPrompt(prompt="Suggest some italian dishes for dinner"))

@master.on_message(model=OrderDetails)
def process_order(ctx:Context, sender:str, order:OrderDetails):
    ctx.logger.info(f"Location: {order.location}")
    ctx.logger.info(f"Date: {order.date}")
    ctx.logger.info(f"Order Details: {order.order}")
    ctx.logger.info(f"Max Price: {order.max_price}")

if __name__=="__main__":
    master.run()

