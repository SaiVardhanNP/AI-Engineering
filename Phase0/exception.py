def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")

    return a // b


def create_task(title, priority):
    if len(title) == 0:
        raise ValueError("Title cant be empty")
    if priority < 0:
        raise ValueError("Priority can't be negative")
    return {title, priority}


try:
    result = divide(10, 0)

except Exception as e:
    print(e)

user = {"name": "Vardhan"}

try:
    print(user["email"])
except KeyError as e:
    print(f"The target key {e} is not found!")

try:
    create_task("Build Claude", -30)
except Exception as e:
    print(e)

print("Hey there!")
