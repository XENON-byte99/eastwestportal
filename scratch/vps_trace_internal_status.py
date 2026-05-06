import os, django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

c = Client()
try:
    print("Executing request...")
    response = c.post('/accounts/login/', {'login': 'testuser@ewubd.edu', 'password': 'testpassword'})
    print("STATUS_CODE:", response.status_code)
    print("Is login successful? (Redirect):", response.get('Location', 'No redirect'))
except Exception as e:
    import traceback
    print("EXCEPTION_OCCURRED")
    traceback.print_exc()
