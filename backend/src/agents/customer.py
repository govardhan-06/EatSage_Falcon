from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

import os,sys
from dotenv import load_dotenv

from backend.src.protocols.customer_proto import makeOrder,sendOrder,getResConfirm,orderPickupConfirm,confirmDelivery

load_dotenv()

'''
This is the script for customer agent
'''

NAME=os.getenv("CUST_NAME")
SEED_PHRASE=os.getenv("CUST_SEED_PHRASE")
DEL_ADDRESS=os.getenv("DEL_ADDRESS")

customer=Agent(
    name=NAME,
    port=8001,
    seed=SEED_PHRASE,
    endpoint=["http://127.0.0.1:8001/submit"],
)

fund_agent_if_low(customer.wallet.address())

customer.include(makeOrder,publish_manifest=True)
customer.include(sendOrder,publish_manifest=True)
customer.include(getResConfirm,publish_manifest=True)
customer.include(orderPickupConfirm,publish_manifest=True)
customer.include(confirmDelivery,publish_manifest=True)

class PaymentRequest(Model):
    wallet_address: str
    amount: int
    denom: str
 
class TransactionInfo(Model):
    tx_hash: str
    amount:str
    denom:str

class TransactionStatus(Model):
    status:str

@customer.on_message(model=PaymentRequest, replies=TransactionInfo)
async def send_payment(ctx: Context, sender: str, msg: PaymentRequest):
    ctx.logger.info(f"Received payment request from {sender}: {msg}")
    fund_agent_if_low(customer.wallet.address())
    transaction = ctx.ledger.send_tokens(msg.wallet_address, msg.amount, msg.denom, customer.wallet)
    ctx.storage.set("transaction hash",transaction.tx_hash)
    await ctx.send(DEL_ADDRESS, TransactionInfo(tx_hash=transaction.tx_hash,amount=msg.amount,denom=msg.denom))

@customer.on_message(model=TransactionStatus)
async def send_status(ctx: Context, sender: str, msg: TransactionStatus):
    ctx.logger.info(f"Message from {sender}: {msg.status}")
    ctx.storage.set("transaction status",msg.status)

if __name__=="__main__":
    customer.run()

