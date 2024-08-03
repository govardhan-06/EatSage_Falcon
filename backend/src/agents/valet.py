from uagents import Agent,Context,Model
from uagents.network import wait_for_tx_to_complete
from uagents.setup import fund_agent_if_low

import os,sys
from dotenv import load_dotenv

from backend.src.protocols.valet_proto import get_Calls,confirm_Calls

load_dotenv()

NAME=os.getenv("DEL_NAME")
SEED_PHRASE=os.getenv("DEL_SEED_PHRASE")
RES_ADDRESS=os.getenv("RES_ADDRESS")
CUST_ADDRESS=os.getenv("CUST_ADDRESS")

valet=Agent(
    name=NAME,
    port=8003,
    seed=SEED_PHRASE,
    endpoint=["http://127.0.0.1:8003/submit"]
)

fund_agent_if_low(valet.wallet.address())

valet.include(get_Calls,publish_manifest=True)
valet.include(confirm_Calls,publish_manifest=True)

class PaymentRequest(Model):
    wallet_address: str
    amount: int
    denom: str
 
class TransactionInfo(Model):
    tx_hash: str
    amount:str
    denom:str

class Acknowledgment(Model):
    message:str
    final_bill:float

class TransactionStatus(Model):
    status:str

@valet.on_message(model=Acknowledgment,replies=PaymentRequest)
async def request_bill_payment(ctx: Context,sender:str,Acknowledgment:str):
    AMOUNT=Acknowledgment.final_bill
    DENOM="atestfet"
    await ctx.send(CUST_ADDRESS,PaymentRequest(wallet_address=str(valet.wallet.address()), amount=AMOUNT, denom=DENOM))

@valet.on_message(model=TransactionInfo,replies=TransactionStatus)
async def confirm_transaction(ctx: Context, sender: str, msg: TransactionInfo):
    ctx.logger.info(f"Received transaction info from {sender}: {msg}")
 
    tx_resp = await wait_for_tx_to_complete(msg.tx_hash, ctx.ledger)
    coin_received = tx_resp.events["coin_received"]
 
    if (
        coin_received["receiver"] == str(valet.wallet.address())
        and coin_received["amount"] == f"{msg.amount}{msg.denom}"
    ):
        ctx.logger.info(f"Transaction was successful: {coin_received}")

        await ctx.send(CUST_ADDRESS,TransactionStatus(status="Transaction successfull!! Thank you."))
        await ctx.send(RES_ADDRESS,TransactionStatus(status=f"Received payment from user: {sender}.Kindly raise the request for the required fund..."))

@valet.on_message(model=PaymentRequest, replies=TransactionInfo)
async def send_payment(ctx: Context, sender: str, msg: PaymentRequest):
    ctx.logger.info(f"Received payment request from {sender}: {msg}")
    transaction = ctx.ledger.send_tokens(msg.wallet_address, msg.amount, msg.denom, valet.wallet)
    
    ctx.storage.set('profit',ctx.storage.get("totalCost")-msg.amount)
    await ctx.send(RES_ADDRESS, TransactionInfo(tx_hash=transaction.tx_hash,amount=msg.amount,denom=msg.denom))

@valet.on_message(model=TransactionStatus)
async def send_status(ctx: Context, sender: str, msg: TransactionStatus):
    ctx.logger.info(f"Message from {sender}: {msg.status}")

if __name__=="__main__":
    valet.run()

