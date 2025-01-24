# Test Python 2 File with Code Smells

def func1(x, y):
    result = x + y;
    print
    "Sum is: ", result
    for i in xrange(10):
        print
        i;


def func2(a, b, c):
    if a > b and a > c:
        print
        "A is largest"
    elif b > a and b > c:
        print
        "B is largest"
    else:
        print
        "C is largest"
    return a + b + c


class Myclass:
    def __init__(self, name, age):
        self.name = name;
        self.age = age

    def display_info(self):
        print
        "Name:", self.name, "Age:", self.age


try:
    func1(5, 10)
    obj = Myclass("Test", 25)
    obj.display_info()
    func2(10, 20, 15)
except Exception, e:
    print
    "Error occurred: ", e