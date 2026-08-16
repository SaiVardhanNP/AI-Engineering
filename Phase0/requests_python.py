import requests
import httpx

response= requests.get('https://jsonplaceholder.typicode.com/users/1')

print(response.status_code)
print(response.json()['name'])

print(response.json()['email'])

print(response.json()['company']['name'])

httpx_response= httpx.get("https://jsonplaceholder.typicode.com/users/1")

print(httpx_response.json())