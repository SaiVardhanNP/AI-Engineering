import requests
from dotenv import load_dotenv
import os

load_dotenv()


my_env = os.getenv("MY_API_KEY")

print("my env is ", my_env)

payload = {"title": "AI Engineering", "body": "Learning HTTP Apis", "userId": 1}

headers = {"X-Student-Name": "Vardhan"}

try:
    response = requests.post(
        "https://jsonplaceholder.typicode.com/post", json=payload, headers=headers,timeout=10
    )

    response.raise_for_status()

    data = response.json()
    print(data)
except Exception as e:
    print(e)
