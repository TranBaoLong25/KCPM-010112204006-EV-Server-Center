import requests
import json

# 1. Register admin (might already be registered, we ignore 409 status code)
reg_payload = {
    "username": "admin",
    "email": "admin@evservice.com",
    "password": "Admin@123456",
    "role": "admin"
}
r = requests.post("http://localhost/api/register", json=reg_payload)
print("Register response:", r.status_code, r.text)

# 2. Login admin
login_payload = {
    "email_username": "admin@evservice.com",
    "password": "Admin@123456"
}
r = requests.post("http://localhost/api/login", json=login_payload)
print("Login response:", r.status_code, r.text)
try:
    token = r.json().get("access_token")
except Exception as e:
    token = None
    print("Could not extract token:", str(e))

if token:
    # 3. Request maintenance task with id=abc
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get("http://localhost/api/maintenance/tasks?id=abc", headers=headers)
    print("Request response status:", r.status_code)
    print("Request response body:", r.text)