import mysql.connector

def get_order_status(order_id: int):
    # Connect to MySQL
    cnx = mysql.connector.connect(
        host= 'localhost',
        user= 'root',
        password= 'root',
        database= 'pandeyji_eatery'
    )

    # Create a cursor
    cursor = cnx.cursor()

    # Execute the query
    query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
    print(query)
    cursor.execute(query)
    # Fetch the result
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    if result:
        return result[0]
    else:
        None



def get_next_orderid():
    cnx = mysql.connector.connect(
        host= 'localhost',
        user= 'root',
        password= 'root',
        database= 'pandeyji_eatery'
    )

    # Create a cursor
    cursor = cnx.cursor()

    # Get the current maximum order_id
    cursor.execute("SELECT MAX(order_id) FROM orders")
    max_order_id = cursor.fetchone()[0] or 0  # If no orders exist, start from 0

    cursor.close()
    cnx.close()
    if max_order_id is None:
        return 1
    return max_order_id + 1


def insert_order_item(food_item, quantity, order_id):
    cnx = mysql.connector.connect(
        host= 'localhost',
        user= 'root',
        password= 'root',
        database= 'pandeyji_eatery'
    )

    try:

        # Create a cursor
        cursor = cnx.cursor()

        # Call the stored procedure or function
        cursor.callproc("insert_order_item", (food_item, quantity, order_id))

        # Commit the changes
        cnx.commit()

        print(f"New order item added with order_id: {order_id}, food_item: {food_item}, quantity: {quantity}")
        return 1

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and cnx.is_connected():
            cnx.close()


def get_order_price(order_id):
    cnx = mysql.connector.connect(
        host= 'localhost',
        user= 'root',
        password= 'root',
        database= 'pandeyji_eatery'
    )

    # Create a cursor
    cursor = cnx.cursor()

    # Get the current maximum order_id
    cursor.execute(f"SELECT get_total_order_price({order_id})")
    total_price = cursor.fetchone()[0] or 0  # If no orders exist, start from 0

    cursor.close()
    cnx.close()
    return total_price



def insert_order_tracking(order_id,status):
    # Connect to MySQL
    cnx = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='pandeyji_eatery'
    )

    # Create a cursor
    cursor = cnx.cursor()

    # Insert the new order_id into the table
    cursor.execute("INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)", (order_id, status))

    # Commit the changes
    cnx.commit()
    cursor.close()
    cnx.close()


def get_item_price(item):
    cnx = mysql.connector.connect(
        host= 'localhost',
        user= 'root',
        password= 'root',
        database= 'pandeyji_eatery'
    )

    # Create a cursor
    cursor = cnx.cursor()
    print(f"****************{item}*******************")
    # Get the current maximum order_id
    cursor.execute(f"SELECT get_price_for_item('{item}')")
    item_price = cursor.fetchone()[0] or 0  # If no orders exist, start from 0

    cursor.close()
    cnx.close()
    return item_price