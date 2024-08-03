from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import sys,uvicorn,os,json
from starlette.responses import JSONResponse
import subprocess
from dotenv import load_dotenv
from uagents.query import query
from uagents import Model
from backend.src.utils.exception import customException
from backend.src.utils.logger import logging

load_dotenv()

CUST_ADDRESS=os.getenv("CUST_ADDRESS")
RES_ADDRESS=os.getenv("RES_ADDRESS")
DEL_ADDRESS=os.getenv("DEL_ADDRESS")

CUST_STORAGE=os.getenv("CUST_STORAGE")
RES_STORAGE=os.getenv("RES_STORAGE")
DEL_STORAGE=os.getenv("DEL_STORAGE")

class UserPrompt(Model):
    prompt: str

class Confirm(Model):
    confirm:bool

class CallValet(Model):
    confirm:int

class ValetDelivery(Model):
    orderID:str
    delivered:str

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    '''
    This function is used to redirect to the swaggerUI page.
    '''
    return RedirectResponse(url="/docs")
 
@app.post("/customer")
async def run_customer():
    '''
    This function is used to run the customer agent.
    '''
    try:
        subprocess.Popen(["python", "backend/src/agents/customer.py"])
    except Exception as e:
        raise customException(e,sys)

@app.post("/restaurant")
async def run_restaurant():
    '''
    This function is used to run the restaurant agent.
    '''
    try:
        subprocess.Popen(["python", "backend/src/agents/restaurants.py"])
    except Exception as e:
        raise customException(e,sys)
    
@app.post("/valet")
async def run_valet():
    '''
    This function is used to run the valet agent.
    '''
    try:
        subprocess.Popen(["python", "backend/src/agents/valet.py"])
    except Exception as e:
        raise customException(e,sys)

@app.post("/prompt")
async def cust_prompt(prompt:str):
    '''
    For Customer
    This function is used to send a prompt to the customer agent.
    Returns the model response as a JSON
    '''
    try:
        await query(destination=CUST_ADDRESS, message=UserPrompt(prompt=prompt), timeout=15.0)
        # Open and read the JSON file
        with open(CUST_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","restauarant":data["restaurant"], "dishes": data['dishes']}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.post("/confirmOrder")
async def cust_confirmation(req:bool):
    '''
    For Customer
    This function is used to confirm an order with the customer agent.
    '''
    try:
        if req:
            await query(destination=CUST_ADDRESS, message=Confirm(confirm=req), timeout=15.0)
            return JSONResponse(content={"message": "Order Confirmed"}, status_code=200)
        
        else:
            return JSONResponse(content={"message": "Sorry!! lets do it once again..."}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.get("/resConfirm")
async def res_confirmation():
    '''
    For Customer
    This function is used to get confirmation message from the restaurant agent.
    '''
    try:
        # Open and read the JSON file
        with open(CUST_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","orderID":data["orderID"], "status": data['status'],
                                     "totalCost":data["totalCost"],"message":data["message"]}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.get("/valetMessage")
async def valet_msg_read():
    '''
    For Customer
    This function is used to read the valet message
    '''
    try:
        # Open and read the JSON file
        with open(CUST_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","valet address":data["valet address"],
                                     "valet message":data["valet message"]}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.post("/confirmDelivery")
async def confirm_order_delivery(req:bool):
    '''
    For Customer
    This function is acknowledge order delivery and raise the Payment.
    '''
    try:
        if(req):
            with open(CUST_STORAGE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    raise customException(f"Error reading JSON file: {str(e)}", sys)
            await query(destination=CUST_ADDRESS, message=ValetDelivery(orderID=data['orderID'],delivered="yes"), timeout=20.0)
            return JSONResponse(content={"message": "Hurray!! Your order has been delivered"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Your order will be delivered soon..."}, status_code=200)
    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.get("/transactionStatus")
async def transaction_status():
    '''
    For Customer
    This function is used to check the transaction status
    '''
    try:
        # Open and read the JSON file
        with open(CUST_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","transaction status":data["transaction status"]}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.get("/currentOrders")
async def get_current_orders():
    '''
    For Restaurant
    This function is used to get the current orders from the customer agent.
    Returns the current orders as a JSON
    '''
    try:
        # Open and read the JSON file
        with open(RES_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","orderID":data["orderID"], "customer_agent": data["customer_agent"],
                                     "order": data["order"],"totalCost": data["totalCost"],}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.post("/acceptOrder")
async def accept_order(req:bool):
    '''
    For Restaurant
    This function is used to accept an order from the customer agent.
    '''
    if(req):
        try:
            await query(destination=RES_ADDRESS, message=Confirm(confirm=req), timeout=15.0)
            return JSONResponse(content={"message": "Order Accepted"}, status_code=200)

        except customException as e:
            logging.error(e)
            return JSONResponse(content={"error": {e}}, status_code=500)
    else:
        return JSONResponse(content={"message": "Currently we are not accepting any orders"}, status_code=200)

@app.post("/callValet")
async def accept_order():
    '''
    For Restaurant
    This function is used to call the valet agent.
    '''
    try:
        await query(destination=RES_ADDRESS, message=CallValet(confirm=1), timeout=15.0)
        return JSONResponse(content={"message": "Valet Call initiated"}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.get("/getValet")
async def get_valet():
    '''
    For Restaurant
    This function is used to get the valet agent's information.
    '''
    try:
        # Open and read the JSON file
        with open(RES_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","valet address":data["valet address"],
                                     "valet message": data["valet message"],"valet location": data["valet location"]}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.get("/statusFoodPayment")
async def status_food_payment():
    '''
    For Restaurant
    This function is used to get the status of food payment.
    '''
    try:
        # Open and read the JSON file
        with open(RES_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","orderID":data["orderID"], "customer_agent": data["customer_agent"], 
                                     "valet address":data['valet address'],'paymentStatus':data['paymentStatus'],
                                     'transaction hash':data['transaction hash']}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.get("/currentCall")
async def get_current_call():
    '''
    For Valet
    This function is used to get the current call from the restaurant agent.
    '''
    try:
        # Open and read the JSON file
        with open(DEL_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","orderID":data["orderID"], "userloc": data["userloc"],
                                     "restaurantloc": data["restaurantloc"],"message": data["message"],"totalCost": data["totalCost"],}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.post("/confirmCall")
async def confirmCall(req:bool):
    '''
    For Valet
    This function is used to accept a delivery call from the restaurant agent.
    '''
    if(req):
        try:
            await query(destination=DEL_ADDRESS, message=Confirm(confirm=req), timeout=15.0)
            return JSONResponse(content={"message": "Delivery Call Accepted"}, status_code=200)

        except customException as e:
            logging.error(e)
            return JSONResponse(content={"error": {e}}, status_code=500)
    else:
        return JSONResponse(content={"message": "Delivery Call Rejected"}, status_code=200)

@app.get("/statusPayment")
async def get_payment():
    '''
    For Valet
    This function is used to confirm payment from the restaurant i.e end of the delivery.
    '''
    try:
        # Open and read the JSON file
        with open(DEL_STORAGE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise customException(f"Error reading JSON file: {str(e)}", sys)

        return JSONResponse(content={"message": "Success","orderID":data["orderID"],'profit':data['profit']}, status_code=200)

    except customException as e:
        logging.error(e)
        return JSONResponse(content={"error": {e}}, status_code=500)

@app.post("/clearStorage")
def clear_agent_storage():
    '''
    This is used to clear the agent storage after the execution of the entire cycle
    '''
    try:
        l=["agent1q0k2rwfj5u_data.json","agent1q2h5xkny4c_data.json","agent1qgu230r5w7_data.json"]
        for file_path in l:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"{file_path} has been deleted successfully.")

    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

    
if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
