from typing import Literal


def calculator(
    a: int, b: int, operation: Literal["add", "sub", "mul", "div", "mod"]
) -> float:
    if operation == "add":
        return a + b
    elif operation == "sub":
        return a - b
    elif operation == "mul":
        return a * b
    elif operation == "div":
        return a / b
    elif operation == "mod":
        return a % b
    # modulus operation
    else:
        raise ValueError("Unsupported operation")
