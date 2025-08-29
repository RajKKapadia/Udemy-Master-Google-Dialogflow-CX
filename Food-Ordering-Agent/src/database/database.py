import aiosqlite
import json
import datetime
import os
from typing import List, Dict, Any, Optional
# import asyncio

# Path to the database file
DB_PATH = "food_database.db"


# Function to create the database
async def create_database() -> None:
    """Create the SQLite database file if it doesn't exist."""
    try:
        # Simply opening a connection will create the file if it doesn't exist
        async with aiosqlite.connect(DB_PATH) as db:
            print(db)
            print(f"Database created or already exists at: {DB_PATH}")
    except Exception as e:
        print(f"Error creating database: {e}")
        raise


# Function to create tables
async def create_tables() -> None:
    """Create the necessary tables in the database."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Create items table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT UNIQUE NOT NULL,
                    ingredients TEXT NOT NULL,
                    quantity TEXT NOT NULL,
                    price REAL NOT NULL,
                    spicy_level TEXT NOT NULL,
                    synonyms TEXT NOT NULL
                )
            """)

            # Create orders table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number INTEGER UNIQUE NOT NULL,
                    amount REAL NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """)

            # Create order_items junction table for many-to-many relationship
            await db.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (item_id) REFERENCES items (id)
                )
            """)

            await db.commit()
            print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise


# Function to fetch an item by name
async def fetch_item_by_name(item_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch an item by its name.

    Args:
        item_name: The name of the item to fetch

    Returns:
        A dictionary with the item details or None if not found
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            # Check for exact match first
            cursor = await db.execute(
                "SELECT * FROM items WHERE item_name = ? COLLATE NOCASE", (item_name,)
            )
            item = await cursor.fetchone()

            # If no exact match, try to match with synonyms
            if item is None:
                cursor = await db.execute(
                    "SELECT * FROM items WHERE synonyms LIKE ?", (f"%{item_name}%",)
                )
                item = await cursor.fetchone()

            if item:
                item_dict = dict(item)
                # Convert the stored JSON strings back to lists
                item_dict["ingredients"] = json.loads(item_dict["ingredients"])
                item_dict["synonyms"] = json.loads(item_dict["synonyms"])
                return item_dict

            return None
    except Exception as e:
        print(f"Error fetching item: {e}")
        raise


# Function to create a new order
async def create_order(items: List[Dict[str, Any]]) -> int:
    """
    Create a new order with the provided items.

    Args:
        items: A list of dictionaries with keys 'item_name' and 'quantity'

    Returns:
        The order number of the created order
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            # Generate a new order number
            cursor = await db.execute(
                "SELECT MAX(order_number) as max_order FROM orders"
            )
            result = await cursor.fetchone()
            max_order = result["max_order"] if result["max_order"] is not None else 0
            new_order_number = max_order + 1

            # Calculate the total amount
            total_amount = 0
            order_items = []

            for item_entry in items:
                item_name = item_entry["item_name"]
                quantity = item_entry.get("quantity", 1)

                # Fetch the item to get its price
                cursor = await db.execute(
                    "SELECT id, price FROM items WHERE item_name = ? COLLATE NOCASE",
                    (item_name,),
                )
                item = await cursor.fetchone()

                if not item:
                    raise ValueError(f"Item '{item_name}' not found in the database")

                item_id = item["id"]
                item_price = item["price"]

                total_amount += item_price * quantity
                order_items.append({"item_id": item_id, "quantity": quantity})

            # Create the order
            current_time = datetime.datetime.now().isoformat()
            cursor = await db.execute(
                "INSERT INTO orders (order_number, amount, created_at) VALUES (?, ?, ?)",
                (new_order_number, total_amount, current_time),
            )
            order_id = cursor.lastrowid

            # Add the order items
            for order_item in order_items:
                await db.execute(
                    "INSERT INTO order_items (order_id, item_id, quantity) VALUES (?, ?, ?)",
                    (order_id, order_item["item_id"], order_item["quantity"]),
                )

            await db.commit()
            return new_order_number
    except Exception as e:
        print(f"Error creating order: {e}")
        raise


# Function to get order details
async def get_order_details(order_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the details of an order by its ID or order number.

    Args:
        order_id: The ID or order number of the order

    Returns:
        A dictionary with the order details or None if not found
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            # First check if the provided ID is an order_number
            cursor = await db.execute(
                "SELECT id, order_number, amount, created_at FROM orders WHERE order_number = ?",
                (order_id,),
            )
            order = await cursor.fetchone()

            # If not found by order_number, try finding by id
            if not order:
                cursor = await db.execute(
                    "SELECT id, order_number, amount, created_at FROM orders WHERE id = ?",
                    (order_id,),
                )
                order = await cursor.fetchone()

            # If still not found, return None
            if not order:
                return None

            order_dict = dict(order)
            order_dict["created_at"] = order_dict["created_at"]
            order_dict["items"] = []

            # Get the items in this order
            cursor = await db.execute(
                """
                SELECT i.id, i.item_name, i.ingredients, i.quantity as item_quantity, 
                       i.price, i.spicy_level, i.synonyms, oi.quantity as order_quantity
                FROM order_items oi
                JOIN items i ON oi.item_id = i.id
                WHERE oi.order_id = ?
            """,
                (order_dict["id"],),
            )

            items = await cursor.fetchall()
            for item in items:
                item_dict = dict(item)
                item_dict["ingredients"] = json.loads(item_dict["ingredients"])
                item_dict["synonyms"] = json.loads(item_dict["synonyms"])
                item_dict["quantity"] = item_dict.pop(
                    "order_quantity"
                )  # Rename order_quantity to quantity
                item_dict["item_quantity"] = item_dict[
                    "item_quantity"
                ]  # Keep the original item quantity
                order_dict["items"].append(item_dict)

            return order_dict
    except Exception as e:
        print(f"Error fetching order: {e}")
        raise


# Function to add all items from a JSON file
async def add_items_from_json(json_file_path: str) -> None:
    """
    Add all items from a JSON file to the database.

    Args:
        json_file_path: Path to the JSON file containing items
    """
    try:
        # Check if the file exists
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")

        # Load items from the JSON file
        with open(json_file_path, "r") as file:
            items = json.load(file)

        async with aiosqlite.connect(DB_PATH) as db:
            for item in items:
                # Convert lists to JSON strings for storage
                ingredients_json = json.dumps(item["ingredients"])
                synonyms_json = json.dumps(item["synonyms"])

                # Insert the item, or update if it already exists
                await db.execute(
                    """
                    INSERT OR REPLACE INTO items 
                    (item_name, ingredients, quantity, price, spicy_level, synonyms)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        item["item_name"],
                        ingredients_json,
                        item["quantity"],
                        item["price"],
                        item["spicy_level"],
                        synonyms_json,
                    ),
                )

            await db.commit()
            print(f"Successfully added {len(items)} items to the database")
    except Exception as e:
        print(f"Error adding items from JSON: {e}")
        raise


# # Example usage function
# async def main():
#     # # Create the database and tables
#     # await create_database()
#     # await create_tables()

#     # # Add items from JSON file
#     # items_file = "food_items.json"

#     # await add_items_from_json(items_file)

#     # # Fetch an item
#     # item = await fetch_item_by_name("Veg Pulao")
#     # if item:
#     #     print(item)
#     #     print(f"Found item: {item['item_name']}")

#     # Create an order
#     # order_items = [{"item_name": "Veg Pulao", "quantity": 2}]
#     # order_number = await create_order(order_items)
#     # print(f"Created order #{order_number}")

#     # # Get order details
#     # order = await get_order_details(1)
#     # if order:
#     #     print(f"Order #{order['order_number']} details:")
#     #     print(f"Amount: {order['amount']}")
#     #     print(f"Created at: {order['created_at']}")
#     #     print("Items:")
#     #     for item in order["items"]:
#     #         print(f"- {item['quantity']}x {item['item_name']} (₹{item['price']} each)")
#     pass


# if __name__ == "__main__":
#     asyncio.run(main())
