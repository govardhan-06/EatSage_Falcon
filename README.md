# Eatsage

## Overview

Eatsage is an innovative food delivery application that integrates AI and Blockchain technology to enhance the user experience. This app utilizes AI agents dedicated to specific tasks, creating a seamless and efficient system for food ordering and delivery.

## How Does the App Work?

The Eatsage app features three AI agents:

1. _Customer Agent_
2. _Valet Agent_
3. _Restaurant Agent_

### Customer Agent

The Customer Agent's backend is responsible for sending trigger notifications to the Restaurant Agent when an order is placed. The frontend is a basic chat interface powered by tiiuae/falcon-180b-chat.

### Restaurant Agent

The Restaurant Agent's backend sends trigger notifications to the Valet Agent when an order is accepted by the restaurant. The frontend displays a list of all available order requests.

### Valet Agent

The Valet Agent's frontend is a list view of all delivery options, allowing the valet to accept or decline orders.

### Additional Features

- The Customer Agent can find nearby restaurants using the device's location.
- Payments are processed through the Fetch Blockchain using the Almanac smart contract. Users must purchase 'FET' tokens, and payments are made automatically.

## Environment Variables

The .env file contains the following environment variables.
_Note:_ The values below are dummy values and should be replaced with actual credentials.

```sh
MONGO_DB_URI="mongodb+srv://username:password@restaurant.mongodb.net/?retryWrites=true&w=majority&appName=Restaurant"
AI71_BASE_URL = "https://api.ai71.ai/v1/"
AI71_API_KEY = "dummy-api-address"

# Customer Agent
CUST_NAME="EatSage_Customer"
CUST_SEED_PHRASE="customer is the king. Welcome to EatSage!!"
CUST_ADDRESS="agent1q0k2rwfj5up9s7z8896pyrchzqawdywcj4ua4vwhfdky0fstvvjtqu3f9kw"
CUST_STORAGE="agent1q0k2rwfj5u_data.json"

# Delivery Partner Agent
DEL_NAME="EatSage_Delivery"
DEL_SEED_PHRASE="EatSage delivery partner, committed to customer service"
DEL_ADDRESS="agent1qgu230r5w774zhc88ncs8ume2v9hzuf7crfeqn5r4pxmk98jp46wsg2mpdx"
DEL_STORAGE="agent1qgu230r5w7_data.json"

# Restaurant Agent
RES_NAME="EatSage_Restaurant"
RES_SEED_PHRASE="We are the elite eatsage restaurants!! Food Quality and Customer service is our topmost priority"
RES_ADDRESS="agent1q2h5xkny4c9kmde7c7hy3394y708us338j55a5y0yfk3t3udwqrxk4zp73s"
RES_STORAGE="agent1q2h5xkny4c_data.json"
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/govardhan-06/eatsage.git
```

2. Navigate to the project directory:

```bash
cd eatsage
```

3. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

4. Install the required packages:

```bash
pip install -r requirements.txt
```

5. Set up your .env file with the appropriate values.

## Usage

1. Start the backend:

```sh
python backend/src/__init__.py
```

2. Access the frontend and start interacting with the Eatsage app.

## License

This project is licensed under the Apache License. See the LICENSE file for details.

## Acknowledgements

Special thanks to the contributors and the open-source community for their support.
