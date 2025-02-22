x = 10
y = 20
z = 30


class MathOperations:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def sum_numbers(self):
        return self.a + self.b + self.c

    def multiply_numbers(self):
        result = 0
        i = 0
        while i < self.b:
            result += self.a
            i += 1
        return result

    def find_max(self):
        max_value = self.a
        if self.b > max_value:
            max_value = self.b
        if self.c > max_value:
            max_value = self.c
        return max_value


def main():
    operations = MathOperations(x, y, z)
    print("The sum is: " + str(operations.sum_numbers()))
    print("The product is: " + str(operations.multiply_numbers()))
    print("The maximum value is: " + str(operations.find_max()))


main()
