# example_bad_code.py

def add_numbers(a, b):
  sum = a + b  # Naming convention warning: sum is a built-in function
  return sum

def print_message():
    print("Hello, world!") # Missing docstring warning

print_message() # Warning: if running as script, should be in a main guard
