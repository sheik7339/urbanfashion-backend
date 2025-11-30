import os, django, json, requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urbanfashion.settings')
# No need to setup django for API call, just use requests

url = 'http://localhost:8000/api/token/'
payload = {'username': 'admin', 'password': 'admin123'}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(payload), headers=headers)
print('Status code:', response.status_code)
print('Response body:', response.text)
