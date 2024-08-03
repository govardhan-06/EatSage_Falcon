# EatSage API Documentation

## Introduction

The EatSage API provides endpoints to manage customer orders, restaurant confirmations, and valet services. This API is designed to interact with customer, restaurant, and valet agents to facilitate food ordering, preparation, and delivery processes.

### Order for Executing API Routes (for testing purposes)

```
/
/customer
/restaurant
/valet
/prompt
/confirmOrder
/currentOrders
/acceptOrder
/resConfirm
/callValet
/currentCall
/confirmCall
/getValet
/valetMessage
/confirmDelivery
/transactionStatus
/statusFoodPayment
/statusPayment
/clearStorage
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-repo/eatsage.git
   cd eatsage
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add the following:

   ```dotenv
   MONGO_DB_URI=""
   GROQ_API_KEY=""

   # Customer Agent
   CUST_NAME="EatSage_Customer"
   CUST_SEED_PHRASE="customer is the king. Welcome to EatSage!!"
   CUST_ADDRESS="agent1q0k2rwfj5up9s7z8896pyrchzqawdywcj4ua4vwhfdky0fstvvjtqu3f9kw"
   CUST_MAILBOX="96b28a58-60d4-46df-9de5-66d94d39da4b"
   CUST_STORAGE="agent1q0k2rwfj5u_data.json"

   # Delivery Partner Agent
   DEL_NAME="EatSage_Delivery"
   DEL_SEED_PHRASE="EatSage delivery partner, committed to customer service"
   DEL_ADDRESS="agent1qgu230r5w774zhc88ncs8ume2v9hzuf7crfeqn5r4pxmk98jp46wsg2mpdx"
   DEL_MAILBOX="c304507f-3f41-42ae-a63e-c0371b708790"
   DEL_STORAGE="agent1qgu230r5w7_data.json"

   # Restaurant Agent
   RES_NAME="EatSage_Restaurant"
   RES_SEED_PHRASE="We are the elite eatsage restaurants!! Food Quality and Customer service is our topmost priority"
   RES_ADDRESS="agent1q2h5xkny4c9kmde7c7hy3394y708us338j55a5y0yfk3t3udwqrxk4zp73s"
   RES_MAILBOX="f246b289-9173-4f9c-9f7e-c675cf810e04"
   RES_STORAGE="agent1q2h5xkny4c_data.json"
   ```

## Hosted Server

`https://clinical-amity-manifest-d5925019.koyeb.app/`

## Running the Server (local)

To run the FastAPI server, execute the following command:

```bash
uvicorn backend.application:app --reload
```

The server will start at `http://127.0.0.1:8000/` and the API documentation can be accessed at `http://127.0.0.1:8000/docs`.

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication is required to access these endpoints.

## Endpoints

### 1. General Endpoints

#### Redirect to Swagger UI (No need to access this route for frontend as this is for testing purpose)

- **URL**: `/`
- **Method**: `GET`
- **Description**: Redirects to the Swagger UI page.
- **Response**: Redirects to `/docs`.

#### Clear the agent storage

- **URL**: `/clearStorage`
- **Method**: `POST`
- **Description**: The storage for all the three agents will be cleared.
- **Response**: null
- **Note**: To be executed after the entire order-delivery cycle

### 2. Customer Endpoints

#### Run Customer Agent : This route triggers the customer agent. Upon accessing this route, customer agent will be get activated.

- **URL**: `/customer`
- **Method**: `POST`
- **Description**: Starts the customer agent.
- **Responses**:
  - `200 OK`: null
  - `500 Internal Server Error`: Error occurred while starting the customer agent.

#### Send Customer Prompt

- **URL**: `/prompt`
- **Method**: `POST`
- **Description**: Sends the user prompt to the customer agent.
- **Parameters**:
  - `prompt` (string): The prompt to send to the customer agent.
- **Responses**:
  - `200 OK`: Returns the restaurant and dishes from the customer agent.
  - `500 Internal Server Error`: Error occurred while sending the prompt.
- **Sample Prompt**
  - `I want to eat some italian dishes`
- **Sample Response**

```
  {
  "message": "Success",
  "restauarant": "Bistro Bliss",
  "dishes": [
    {
      "itemname": "Bruschetta",
      "description": "Grilled bread topped with fresh tomatoes and basil",
      "itemcost": 332
    },
    {
      "itemname": "Chicken Alfredo Pasta",
      "description": "Fettuccine pasta tossed in a creamy Alfredo sauce with grilled chicken",
      "itemcost": 196
    },
    {
      "itemname": "Tiramisu",
      "description": "Layered dessert with coffee-soaked ladyfingers and mascarpone cheese",
      "itemcost": 203
    },
    {
      "itemname": "Cappuccino",
      "description": "Espresso with steamed milk and foam",
      "itemcost": 596
    }
  ]
}
```

#### Confirm Customer Order

- **URL**: `/confirmOrder`
- **Method**: `POST`
- **Description**: Confirms an order sent by the customer agent. Once submitted, this will be sent to the restaurant agent.
- **Parameters**:
  - `req` (boolean): Confirmation status.
- **Responses**:
  - `200 OK`: Order confirmed.
  - `500 Internal Server Error`: Error occurred while confirming the order.
- **Note**: If the user denies the order suggested by the customer agent, then the prompt route must be initiated once again using the prompt given by the user.

#### Restaurant Confirmation Message

- **URL**: `/resConfirm`
- **Method**: `GET`
- **Description**: Gets confirmation message from the restaurant agent whether the order is accepted or not.
- **Responses**:
  - `200 OK`: Returns order details including order ID, status, total cost, and message.
  - `500 Internal Server Error`: Error occurred while fetching the confirmation message.
- **Sample Response**

```
{
  "message": "Thank you for choosing Bistro Bliss. Your order will be delivered soon...",
  "orderID": "9b9fef4c-e3b0-4f2b-a2a7-ce415dd9975d",
  "status": true,
  "totalCost": 1393.35
}
```

#### Valet Message

- **URL**: `/valetMessage`
- **Method**: `GET`
- **Description**: Reads the valet message.
- **Responses**:
  - `200 OK`: Returns valet address and message.
  - `500 Internal Server Error`: Error occurred while reading the valet message.
- **Sample Response**

```
{
  "message": "Success",
  "valet address": "agent1q2h5xkny4c9kmde7c7hy3394y708us338j55a5y0yfk3t3udwqrxk4zp73s",
  "valet message": "Valet Agent agent1qgu230r5w774zhc88ncs8ume2v9hzuf7crfeqn5r4pxmk98jp46wsg2mpdx picked up the order and will be delivering it soon..."
}
```

#### Confirm Order Delivery

- **URL**: `/confirmDelivery`
- **Method**: `POST`
- **Description**: Acknowledges order delivery and raises the payment.
- **Parameters**:
  - `req` (boolean): Delivery confirmation status.
- **Responses**:
  - `200 OK`: Order delivery confirmed.
  - `500 Internal Server Error`: Error occurred while confirming delivery.

#### Transaction Status

- **URL**: `/transactionStatus`
- **Method**: `GET`
- **Description**: Checks the transaction status.
- **Responses**:
  - `200 OK`: Returns the transaction status.
  - `500 Internal Server Error`: Error occurred while checking the transaction status.

### 3. Restaurant Endpoints

#### Run Restaurant Agent

- **URL**: `/restaurant`
- **Method**: `POST`
- **Description**: Starts the restaurant agent.
- **Responses**:
  - `200 OK`: Restaurant agent started successfully.
  - `500 Internal Server Error`: Error occurred while starting the restaurant agent.

#### Get Current Orders

- **URL**: `/currentOrders`
- **Method**: `GET`
- **Description**: Gets the current orders from the customer agent.
- **Responses**:
  - `200 OK`: Returns current orders.
  - `500 Internal Server Error`: Error occurred while fetching current orders.
- **Sample Response**

```
{
  "message": "Success",
  "orderID": "9b9fef4c-e3b0-4f2b-a2a7-ce415dd9975d",
  "customer_agent": "agent1q0k2rwfj5up9s7z8896pyrchzqawdywcj4ua4vwhfdky0fstvvjtqu3f9kw",
  "order": [
    {
      "itemname": "Bruschetta",
      "description": "Grilled bread topped with fresh tomatoes and basil",
      "itemcost": 332
    },
    {
      "itemname": "Chicken Alfredo Pasta",
      "description": "Fettuccine pasta tossed in a creamy Alfredo sauce with grilled chicken",
      "itemcost": 196
    },
    {
      "itemname": "Tiramisu",
      "description": "Layered dessert with coffee-soaked ladyfingers and mascarpone cheese",
      "itemcost": 203
    },
    {
      "itemname": "Cappuccino",
      "description": "Espresso with steamed milk and foam",
      "itemcost": 596
    }
  ],
  "totalCost": 1327
}
```

#### Accept Order

- **URL**: `/acceptOrder`
- **Method**: `POST`
- **Description**: Accepts an order from the customer agent.
- **Parameters**:
  - `req` (boolean): Order acceptance status.
- **Responses**:
  - `200 OK`: Order accepted.
  - `500 Internal Server Error`: Error occurred while accepting the order.
- **Note**: If the restaurant denies the order sent by the customer agent, then the prompt route must be initiated once again using the prompt given by the user. User must be informed about this order denial by the restaurant. The restaurant message can be accessed using the `/resConfirm` route

#### Call Valet

- **URL**: `/callValet`
- **Method**: `POST`
- **Description**: Calls the valet agent.
- **Responses**:
  - `200 OK`: Valet call initiated.
  - `500 Internal Server Error`: Error occurred while calling the valet.

#### Get Valet Information

- **URL**: `/getValet`
- **Method**: `GET`
- **Description**: Gets the valet agent's information.
- **Responses**:
  - `200 OK`: Returns valet address, message, and location.
  - `500 Internal Server Error`: Error occurred while fetching valet information.
- **Sample Response**

```
{
  "message": "Success",
  "valet address": "agent1qgu230r5w774zhc88ncs8ume2v9hzuf7crfeqn5r4pxmk98jp46wsg2mpdx",
  "valet message": "Received your delivery call. My current location: [50.1155, 8.6842]. Picking up the order in few minutes...",
  "valet location": [
    50.1155,
    8.6842
  ]
}
```

#### Status of Food Payment

- **URL**: `/statusFoodPayment`
- **Method**: `GET`
- **Description**: Gets the status of food payment.
- **Responses**:
  - `200 OK`: Returns food payment status.
  - `500 Internal Server Error`: Error occurred while checking food payment status.
- **Sample Response**

```
{
  "message": "Success",
  "orderID": "78c58ddd-0ed3-46a7-89cb-08020b596f57",
  "customer_agent": "agent1q0k2rwfj5up9s7z8896pyrchzqawdywcj4ua4vwhfdky0fstvvjtqu3f9kw",
  "valet address": "agent1qgu230r5w774zhc88ncs8ume2v9hzuf7crfeqn5r4pxmk98jp46wsg2mpdx",
  "paymentStatus": "Received payment from agent1qgu230r5w774zhc88ncs8ume2v9hzuf7crfeqn5r4pxmk98jp46wsg2mpdx. Thank You",
  "transaction hash": "BDB29E8851A2AE9F8C510FDFFBF28DC551B55A3629DD25A41361F40D5014E5AE"
}
```

### 4. Valet Endpoints

#### Run Valet Agent

- **URL**: `/valet`
- **Method**: `POST`
- **Description**: Starts the valet agent.
- **Responses**:
  - `200 OK`: Valet agent started successfully.
  - `500 Internal Server Error`: Error occurred while starting the valet agent.

#### Get Current Call

- **URL**: `/currentCall`
- **Method**: `GET`
- **Description**: Gets the current call from the restaurant agent.
- **Responses**:
  - `200 OK`: Returns current call details.
  - `500 Internal Server Error`: Error occurred while fetching current call details.
- **Sample Response**

```
{
  "message": "Order will be getting ready in few minutes...",
  "orderID": "9b9fef4c-e3b0-4f2b-a2a7-ce415dd9975d",
  "userloc": [
    50.1155,
    8.6842
  ],
  "restaurantloc": [
    50.1155,
    8.6842
  ],
  "totalCost": 1393.35
}
```

#### Confirm Delivery Call

- **URL**: `/confirmCall`
- **Method**: `POST`
- **Description**: Accepts a delivery call from the restaurant agent.
- **Parameters**:
  - `req` (boolean): Delivery call acceptance status.
- **Responses**:
  - `200 OK`: Delivery call accepted.
  - `500 Internal Server Error`: Error occurred while accepting the delivery call.
- **Note**: If the valet denies the delivery call sent by the restaurant agent, then the `/callValet` route must be initiated once again and this will reassign the valet. This feature will be useful in the future updates wherein multiple valet agents will be available.

#### Status of Payment

- **URL**: `/statusPayment`
- **Method**: `GET`
- **Description**: Confirms payment from the restaurant, marking the end of the delivery.
- **Responses**:
  - `200 OK`: Returns payment status.
  - `500 Internal Server Error`: Error occurred while confirming payment.
- **Sample Response**

```
{
  "message": "Success",
  "orderID": "78c58ddd-0ed3-46a7-89cb-08020b596f57",
  "profit": 66.34999999999991
}
```

## Error Handling

All error responses will be in the following format:

```json
{
  "error": "Error message"
}
```

## Usage (local)

To test the API, you can use tools like Postman or cURL. Make sure to follow the parameter requirements for each endpoint. For example, to run the customer agent, you can send a POST request to `/customer` using Postman or:

```bash
curl -X POST http://localhost:8000/customer
```

For more detailed API interaction, refer to the Swagger UI at `http://localhost:8000/docs`.

## Conclusion

The EatSage API facilitates efficient interaction between customer, restaurant, and valet agents, ensuring a smooth and automated process for food ordering, preparation, and delivery. Use the endpoints as described above to integrate with the EatSage backend service.
