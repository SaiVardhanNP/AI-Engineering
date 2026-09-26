import time


def add_numbers(a: int, b: int) -> int:
    print(f"Adding {a} and {b}")

    time.sleep(20)

    return a + b

def failing_job():
    print("Starting failing job")
    raise Exception("Something went wrong")