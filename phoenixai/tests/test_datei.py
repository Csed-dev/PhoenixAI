import os
import sys
import math  # Unnötiger Import
import json  # Unnötiger Import

def calculate_area(radius):
    print("Berechne den Flächeninhalt")
    area = math.pi * radius ** 2
    return area

import random  # Import zwischen den Funktionen

def greet(name):
    print(f"Hallo, {name}!")

def unused_function():
    pass

def process_data(data):
    processed = []
    for item in data:
        if isinstance(item, int):
            processed.append(item * 2)
        elif isinstance(item, str):
            processed.append(item.upper())
    return processed

import datetime  # Noch ein unnötiger Import

def log_event(event):
    timestamp = datetime.datetime.now()
    print(f"{timestamp}: {event}")

def another_unused_function():
    pass

def compute_statistics(numbers):
    if not numbers:
        return None
    total = sum(numbers)
    average = total / len(numbers)
    variance = sum((x - average) ** 2 for x in numbers) / len(numbers)
    return {"total": total, "average": average, "variance": variance}

def faulty_function(x, y):
    return x / y  # Mögliche Division durch Null

import collections  # Unnötiger Import

def count_elements(items):
    counter = collections.Counter(items)
    return counter

def main():
    radius = 5
    area = calculate_area(radius)
    print(f"Der Flächeninhalt beträgt: {area}")

    name = "Alice"
    greet(name)

    data = [1, 2, "drei", 4, "fünf"]
    result = process_data(data)
    print(f"Verarbeitete Daten: {result}")

    log_event("Daten verarbeitet")

    stats = compute_statistics([1, 2, 3, 4, 5])
    print(f"Statistiken: {stats}")

    try:
        result = faulty_function(10, 0)
    except ZeroDivisionError:
        print("Fehler: Division durch Null!")

    counts = count_elements(['apple', 'banana', 'apple', 'cherry'])
    print(f"Elementzählung: {counts}")

if __name__ == "__main__":
    main()
