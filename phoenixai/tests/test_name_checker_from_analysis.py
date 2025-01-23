def x(a, b):
    c = a + b
    return c


def y(n):
    r = 1
    for i in range(1, n + 1):
        r *= i
    return r


def z(lst):
    s = 0
    for num in lst:
        s += num
    return s / len(lst) if lst else 0


class A:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def do(self):
        return self.a * self.b

    def check(self):
        return self.a > self.b


def bignum(x):
    if x > 100:
        return True
    return False


q = 42
d = "Hello"
e = x(q, 10)
f = y(5)
g = z([1, 2, 3, 4, 5])

obj = A(e, f)
h = obj.do()
k = obj.check()
m = bignum(h)

print(h, k, m)
