import math

# function with bad naming and no docstrings
def func1(x, y):
    result = x+y; return result

# function with repetitive code
def func2(data):
    total = 0
    for i in range(len(data)):
        total += data[i]
    return total

# function with unused variables and poor formatting
def func3( data ):
    temp = 5 # unused variable
    total=0
    for value in data: total+=value
    return total

# non-pythonic code with unnecessary conditions
def func4(numbers):
    even_numbers = []
    for n in numbers:
        if n % 2 == 0: even_numbers.append(n)
    return even_numbers

# overly complex function
def func5(a,b,c,d):
    if a > b:
        if c > d:
            return a+c
        else:
            return a+d
    else:
        if c > d:
            return b+c
        else:
            return b+d

# function with hardcoded values and poor readability
def func6():
    result = 0
    for i in [1,2,3,4,5]:
        result = result + i
    return result

# large function without modularity
def func7(data):
    count = 0
    for value in data:
        if value > 0:
            count += 1
    negatives = 0
    for value in data:
        if value < 0:
            negatives += 1
    return count, negatives

# magic numbers and non-descriptive variable names
def func8():
    x = 3.14 * 10 * 10
    y = 2 * 3.14 * 10
    return x, y
