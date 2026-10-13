import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            print(f"{func.__name__} : {elapsed:0.2f}s")

    return wrapper

@timer
def calculate(n):
    return sum(i*i for i in range(n))

result = calculate(100000)
print(result)



def decorator_a(func):
    def wrapper():
        print("A before")
        func()
        print("A after")
    return wrapper


def decorator_b(func):
    def wrapper():
        print("B before")
        func()
        print("B after")
    return wrapper


@decorator_a
@decorator_b
def hello():
    print("Hello")


hello()