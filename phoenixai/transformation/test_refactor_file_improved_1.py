import datetime
import json
import os
import random

def manage_userData(file_path, user_data):
    """Manages user data."""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
        print("Created a new user data file.")
    with open(file_path, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(user_data)
        f.seek(0)
        json.dump(data, f, indent=4)
    print(f"Total users: {len(data)}")

def process_orders(orders):
    """Processes a list of orders."""
    if not orders:
        print("No orders to process.")
        return
    total_revenue = sum(order["amount"] for order in orders)
    most_expensive = max(orders, key=lambda x: x["amount"])
    high_value_orders = [order for order in orders if order["amount"] > 100]
    print(f"Total Revenue: ${total_revenue}")
    print(f"Most Expensive Order: {most_expensive}")
    print(f"Orders Exceeding $100: {len(high_value_orders)}")

def generate_random_data(file_path):
    """Generates random data for testing."""
    user_profiles = [
        {"name": f"User{random.randint(1, 1000)}", "age": random.randint(18, 60)}
        for _ in range(10)
    ]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_profiles, f, indent=4)
    average_age = sum(user["age"] for user in user_profiles) / len(user_profiles)
    print(f"Generated {len(user_profiles)} user profiles.")
    print(f"Average Age: {average_age}")
    with open("operation_log.txt", "a", encoding="utf-8") as log:
        log.write(f"[{datetime.datetime.now()}] Generated data in {file_path}\n")

def analyze_weather_data(data):
    """Analyzes weather data."""
    if not data:
        print("No weather data provided.")
        return
    average_temp = sum(day["temperature"] for day in data) / len(data)
    hottest_day = max(data, key=lambda x: x["temperature"])
    rainy_days = sum(1 for day in data if day.get("rain", False))
    print(f"Average Temperature: {average_temp}°C")
    print(f"Hottest Day: {hottest_day}")
    print(f"Days with Rain: {rainy_days}")

if __name__ == "__main__":
    manage_userData("users.json", {"name": "Alice", "age": 25})
    process_orders(
        [
            {"id": 1, "amount": 150.5},
            {"id": 2, "amount": 75.0},
            {"id": 3, "amount": 200.0},
        ]
    )
    generate_random_data("random_users.json")
    analyze_weather_data(
        [
            {"day": "Monday", "temperature": 22, "rain": False},
            {"day": "Tuesday", "temperature": 25, "rain": True},
            {"day": "Wednesday", "temperature": 30, "rain": False},
        ]
    )