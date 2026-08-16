def format_user(user: dict) -> str:
    try:
        return f" Name: {user['name']}\n Email: {user['email']}\n Company: {user['company']['name']}"
    except Exception as e:
        print(e)
