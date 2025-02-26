# A non-pythonic Python script with code smells

def func1(numbers):
    result = 0
    for i in range(len(numbers)):
        result = result + numbers[i]
    print("The sum of the list is: " + str(result))

def func2(words):
    for i in range(len(words)):
        word = words[i]
        if len(word) > 5:
            print(word + " is a long word.")
        else:
            print(word + " is a short word.")

def func3():
    data = [1, 2, 3, 4, 5]
    squares = []
    for i in data:
        squares.append(i * i)
    for i in range(len(squares)):
        print("Square of " + str(data[i]) + " is " + str(squares[i]))

def func4():
    my_dict = {}
    keys = ['name', 'age', 'city']
    values = ['Alice', 25, 'New York']
    for i in range(len(keys)):
        my_dict[keys[i]] = values[i]
    for key in my_dict:
        print(key + ": " + str(my_dict[key]))

def func5(matrix):
    transposed = []
    for i in range(len(matrix[0])):
        row = []
        for j in range(len(matrix)):
            row.append(matrix[j][i])
        transposed.append(row)
    for row in transposed:
        print(row)

def func6(num_list):
    results = []
    for i in range(len(num_list)):
        if num_list[i] % 2 == 0:
            results.append(num_list[i])
    print("Even numbers are: " + str(results))

class MyClass:
    def __init__(self, value):
        self.value = value

    def repeat_value(self, times):
        result = []
        for i in range(times):
            result.append(self.value)
        print("Repeated values are: " + str(result))

# Test the functions
func1([1, 2, 3, 4, 5])
func2(['apple', 'cat', 'elephant', 'banana'])
func3()
func4()
func5([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
func6([1, 2, 3, 4, 5, 6])

obj = MyClass("test")
obj.repeat_value(3)