from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse
from database import *
from session_helper import *

app = FastAPI()
inprogress_sessions={}

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_context = payload['queryResult']['outputContexts']
    session_id = extract_session_id(output_context[0]["name"])
    print(intent)

    intents = {
        "track.order - context: ongoing-tracking":track_order,
        "order.add - context: ongoing-order": add_order,
        "order.complete - context: ongoing-order": complete_order,
        "order.remove - context: ongoing-order": remove_from_order,
        "new.order": new_order,
        "order.accept- context: ongoing-order": accept_order,
        "Price": extract_price
    }


    response = intents[intent](parameters,session_id)
    return response


def track_order(parameters : dict,session_id):
    order_id = parameters['order_id']
    status = get_order_status(order_id)
    if status:
        fulfillment_text = f"The status of the order:{int(order_id)} is {status}"
    else:
        fulfillment_text = f"Order number:{int(order_id)} wasn't found"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def add_order(parameters : dict,session_id : str):
    food_items = parameters['food-item']
    quantities = parameters['number']
    if len(food_items)!=len(quantities):
        fulfillment_text = "Specify the numbers for the food items"
    else:
        new_food_dict = dict(zip(food_items, quantities))


        if session_id in inprogress_sessions:
            current_food_dict = inprogress_sessions[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_sessions[session_id] = current_food_dict
        else:
            inprogress_sessions[session_id] = new_food_dict

        order_str = get_str_from_dict(inprogress_sessions[session_id])
        fulfillment_text = f"Recived {order_str}, do you want anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})




def complete_order(parameters : dict,session_id : str):
    if session_id not in inprogress_sessions:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_sessions[session_id]
        order_id = save_to_db(order)

        if order_id==-1:
            fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        else:
            total_price = get_order_price(order_id)
            fulfillment_text = f"Awesome. We have placed your order. " \
                               f"Here is your order id: {order_id}. " \
                               f"Your order total price is {total_price} which you can pay at the time of delivery!"

        del inprogress_sessions[session_id]

    return JSONResponse(content={"fulfillmentText": fulfillment_text})



def save_to_db(order: dict):
    next_order_id = get_next_orderid()

    for food_item, quantity in order.items():
        status = insert_order_item(food_item,quantity,next_order_id)

        if status==-1:
            return -1

    insert_order_tracking(next_order_id,"in progress")
    return next_order_id


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_sessions:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })

    food_items = parameters["food-item"]
    current_order = inprogress_sessions[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = get_str_from_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}, Anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def new_order(parameters: dict, session_id: str):
    inprogress_sessions[session_id] = {}



def accept_order(parameters: dict, session_id: str):
    current_order = inprogress_sessions[session_id]
    order_str = get_str_from_dict(current_order)
    fulfillment_text = f"Amazing choice!! your order includes {order_str}, do you accept your order?"
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def extract_price(parameters: dict, session_id: str):
    item = parameters['food-item'][0]
    item_price = get_item_price(item)
    fulfillment_text = f"The Price of  {item} is {int(item_price)}$"
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
