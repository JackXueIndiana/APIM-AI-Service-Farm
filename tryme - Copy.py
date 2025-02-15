'''
from openai import AzureOpenAI

client = AzureOpenAI(
   azure_endpoint="https://aifarmapim.azure-api.net/openai-load-balancing",
   api_key="your value",
   api_version="2024-06-01"
)

response = client.chat.completions.create(
   model="gpt-35-turbo",
   messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello! Please tell me the history of United States?"}
   ]
)
print(response)

'''

import requests
import json

# Set your endpoint and API key
endpoint = "https://aifarmapim.azure-api.net/openai-load-balancing"
api_key = "your value"
deployment_name = "gpt-35-turbo"
api_version = "2024-06-01"

# Define the headers and payload
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}
payload = {
    "model": "YOUR_MODEL_NAME",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Please tell me the history of United States."}
    ]
}

# Make the API request
response = requests.post(
    f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}",
    headers=headers,
    data=json.dumps(payload)
)

print(response.status_code)
print(response.json())

# Access response headers
response_headers = response.headers
print(response_headers)