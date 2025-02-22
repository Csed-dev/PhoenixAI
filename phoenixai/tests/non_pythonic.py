# Function to calculate factorial in an unpythonic way
def calculate_factorial(number):
    result = 1
    if number < 0:
        return None
    elif number == 0:
        return 1
    else:
        counter = 1
        while counter <= number:
            result = result * counter
            counter = counter + 1
    return result


# Unpythonic class with verbose methods
class UnpythonicClass:
    def __init__(self):
        self.data = []

    def add_item(self, item):
        # Append item using list concatenation
        self.data = self.data + [item]

    def get_items(self):
        items = []
        index = 0
        while index < len(self.data):
            items.append(self.data[index])
            index = index + 1
        return items


# Main function demonstrating various unpythonic constructs
def main():
    # Create instance of the unpythonic class
    my_object = UnpythonicClass()
    counter = 1
    while counter <= 5:
        my_object.add_item(counter)
        counter = counter + 1

    # Calculate factorial for numbers 1 to 5 and store in a dictionary
    factorial_results = {}
    for number in range(1, 6):
        factorial_results[number] = calculate_factorial(number)

    # Create a result string using unpythonic string concatenation
    result_string = ""
    keys = list(factorial_results.keys())
    keys.sort()
    for key in keys:
        result_string = result_string + "Factorial of " + str(key) + " is " + str(factorial_results[key]) + "\n"
    print(result_string)

    # Print items from the unpythonic class using a while loop
    items = my_object.get_items()
    index = 0
    while index < len(items):
        print("Item at index " + str(index) + " is " + str(items[index]))
        index = index + 1


if __name__ == "__main__":
    main()