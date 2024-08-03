from uagents import Agent,Context,Model
from uagents.network import wait_for_tx_to_complete
from uagents.setup import fund_agent_if_low

import os,sys
from dotenv import load_dotenv
from backend.src.protocols.restaurant_proto import take_Orders,get_valet,acceptOrders,valet_Message

load_dotenv()

NAME=os.getenv("RES_NAME")
SEED_PHRASE=os.getenv("RES_SEED_PHRASE")
DEL_ADDRESS=os.getenv("DEL_ADDRESS")
CUST_ADDRESS=os.getenv("CUST_ADDRESS")

restaurant=Agent(
    name=NAME,
    port=8002,
    seed=SEED_PHRASE,
    endpoint=["http://127.0.0.1:8002/submit"],
)

fund_agent_if_low(restaurant.wallet.address())

restaurant.include(take_Orders,publish_manifest=True)
restaurant.include(get_valet,publish_manifest=True)
restaurant.include(acceptOrders,publish_manifest=True)
restaurant.include(valet_Message,publish_manifest=True)

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

@restaurant.on_message(model=TransactionStatus,replies=PaymentRequest)
async def request_bill_payment(ctx: Context,sender:str,TransactionStatus:str):
    DENOM="atestfet"
    await ctx.send(DEL_ADDRESS,PaymentRequest(wallet_address=str(restaurant.wallet.address()), amount=ctx.storage.get('totalCost'), denom=DENOM))

@restaurant.on_message(model=TransactionInfo,replies=TransactionStatus)
async def confirm_transaction(ctx: Context, sender: str, msg: TransactionInfo):
    ctx.logger.info(f"Received transaction info from {sender}: {msg}")
 
    tx_resp = await wait_for_tx_to_complete(msg.tx_hash, ctx.ledger)
    coin_received = tx_resp.events["coin_received"]
 
    if (
        coin_received["receiver"] == str(restaurant.wallet.address())
        and coin_received["amount"] == f"{msg.amount}{msg.denom}"
    ):
        ctx.logger.info(f"Transaction was successful: {coin_received}")
 
        ctx.storage.set('paymentStatus',f"Received payment from {sender}. Thank You")
        ctx.storage.set('transaction hash',msg.tx_hash)
        await ctx.send(DEL_ADDRESS,TransactionStatus(status=f"Received payment from {sender}. Thank You"))

if __name__=="__main__":
    restaurant.run()

