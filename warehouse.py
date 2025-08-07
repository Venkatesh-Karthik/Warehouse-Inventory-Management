import pandas as pd
import numpy as np
import os

STACK_SIZE = 69
MAX_STACKS = 1000
MAX_CAPACITY = STACK_SIZE * MAX_STACKS
LOW_STOCK_THRESHOLD = 50

stock_file = "stock_data.csv"
orders_file = "order_history.csv"

def load_data():
    if os.path.exists(stock_file):
        return pd.read_csv(stock_file)
    return pd.DataFrame({
        "Item": pd.Series(dtype='str'),
        "Quantity": pd.Series(dtype='int'),
        "Price per Unit": pd.Series(dtype='float'),
        "Total Value": pd.Series(dtype='float'),
        "Location": pd.Series(dtype='int')
    })

def save_data():
    stock_df.to_csv(stock_file, index=False)

def log_order(item, quantity, price):
    order_entry = pd.DataFrame([{
        "Item": item,
        "Quantity": quantity,
        "Unit Price": price,
        "Total": round(quantity * price, 2)
    }])
    if os.path.exists(orders_file):
        order_entry.to_csv(orders_file, mode='a', header=False, index=False)
    else:
        order_entry.to_csv(orders_file, index=False)

def warehouse_space_used():
    total_items = stock_df["Quantity"].sum()
    percent_used = (total_items / MAX_CAPACITY) * 100
    return total_items, percent_used

def add_item():
    item = input("Enter item name: ").strip().title()
    try:
        quantity = int(input("Enter quantity: "))
        price_per_unit = float(input("Enter price per unit: "))
        location = int(input("Enter storage location (numeric): "))
    except ValueError:
        print("Invalid input.\n")
        return

    total_items, _ = warehouse_space_used()
    if total_items + quantity > MAX_CAPACITY:
        print("Not enough space in the warehouse.\n")
        return

    total_value = round(quantity * price_per_unit, 2)
    global stock_df

    if item in stock_df["Item"].values:
        stock_df.loc[stock_df["Item"] == item, "Quantity"] += quantity
        stock_df.loc[stock_df["Item"] == item, "Total Value"] += total_value
    else:
        new_row = {
            "Item": item,
            "Quantity": quantity,
            "Price per Unit": price_per_unit,
            "Total Value": total_value,
            "Location": location
        }
        stock_df = pd.concat([stock_df, pd.DataFrame([new_row])], ignore_index=True)

    print(f"{quantity} units of {item} added to location {location}.\n")
    save_data()

def view_stock():
    if stock_df.empty:
        print("No items in stock.\n")
    else:
        print("\nCurrent Stock Levels:")
        print(stock_df.sort_values(by="Item").to_string(index=False))
        total_items, percent_used = warehouse_space_used()
        print(f"\nWarehouse usage: {total_items}/{MAX_CAPACITY} items ({percent_used:.2f}% full)")

        low_stock_items = stock_df[stock_df["Quantity"] < LOW_STOCK_THRESHOLD]
        if not low_stock_items.empty:
            print("\nLow Stock Alerts:")
            print(low_stock_items[["Item", "Quantity"]].to_string(index=False))
    print()

def update_price():
    item = input("Enter item name to update price: ").strip().title()
    if item not in stock_df["Item"].values:
        print("Item not found.\n")
        return

    try:
        mode = input("Do you want to (I)ncrease or (D)ecrease the price? ").strip().upper()
        amount = float(input("Enter the amount to adjust: "))
    except ValueError:
        print("Invalid input.\n")
        return

    if mode not in ("I", "D"):
        print("Invalid mode.\n")
        return

    old_price = stock_df.loc[stock_df["Item"] == item, "Price per Unit"].values[0]
    new_price = old_price + amount if mode == "I" else old_price - amount
    quantity = stock_df.loc[stock_df["Item"] == item, "Quantity"].values[0]

    stock_df.loc[stock_df["Item"] == item, "Price per Unit"] = round(new_price, 2)
    stock_df.loc[stock_df["Item"] == item, "Total Value"] = round(quantity * new_price, 2)

    print(f"Price for {item} updated to ₹{new_price:.2f}.\n")
    save_data()

def place_order():
    item = input("Enter item to order: ").strip().title()
    if item not in stock_df["Item"].values:
        print("Item not found.\n")
        return

    try:
        quantity = int(input("Enter quantity to order: "))
    except ValueError:
        print("Invalid input.\n")
        return

    current_quantity = stock_df.loc[stock_df["Item"] == item, "Quantity"].values[0]
    if quantity > current_quantity:
        print("Not enough stock.\n")
        return

    stock_df.loc[stock_df["Item"] == item, "Quantity"] -= quantity
    price = stock_df.loc[stock_df["Item"] == item, "Price per Unit"].values[0]
    stock_df.loc[stock_df["Item"] == item, "Total Value"] -= round(price * quantity, 2)

    print(f"Picking {quantity} units of {item}...")
    print(f"Labeling and documentation generated.")
    print(f"Order dispatched via logistics partner.\n")

    log_order(item, quantity, price)

    if stock_df.loc[stock_df["Item"] == item, "Quantity"].values[0] == 0:
        stock_df.drop(stock_df[stock_df["Item"] == item].index, inplace=True)

    save_data()

def view_order_history():
    if not os.path.exists(orders_file):
        print("No orders placed yet.\n")
        return

    df = pd.read_csv(orders_file)
    if df.empty:
        print("Order log is empty.\n")
    else:
        print("\nOrder History:")
        print(df.to_string(index=False))
    print()

def main():
    global stock_df
    stock_df = load_data()

    while True:
        print("Warehouse Stock Management System")
        print("1. Add Item")
        print("2. View Stock")
        print("3. Update Item Price")
        print("4. Place Order")
        print("5. View Order History")
        print("6. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_item()
        elif choice == "2":
            view_stock()
        elif choice == "3":
            update_price()
        elif choice == "4":
            place_order()
        elif choice == "5":
            view_order_history()
        elif choice == "6":
            print("Exiting system...")
            break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    main()