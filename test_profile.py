import json
import requests

# Use the access token from the previous face login response
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NjAwNjEyLCJpYXQiOjE3NDQ1OTcwMTIsImp0aSI6ImVmODRmYzQ1Y2Y0NTQ0MDg5MTZhZWI1N2RjOWQ4OWNjIiwidXNlcl9pZCI6ImI4MmE2NWJkLThkMjYtNGUyNi1hZDNiLTU4NzNhMmY5NjcwNyJ9.Q4Qa3eslY_K1kDgfGK2lpmQeHqBoYNHCqfKrAbAxGRQ"

try:
    # Set up the headers with the Bearer token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Make the API request to get the user profile
    response = requests.get('http://127.0.0.1:8000/api/auth/profile/', headers=headers)
    
    # Print the response
    print("Status Code:", response.status_code)
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"Error: {e}") 