import requests

# GET request to tasks endpoint with invalid ID and no token
r = requests.get("http://localhost/api/maintenance/tasks?id=abc")
print("Unauthenticated Request (id=abc):")
print("Response status:", r.status_code)
print("Response body:", r.text)

# GET request to tasks endpoint with valid ID and no token
r = requests.get("http://localhost/api/maintenance/tasks?id=1")
print("\nUnauthenticated Request (id=1):")
print("Response status:", r.status_code)
print("Response body:", r.text)
