Initial commit in scheduBackend
ngrok http --url=weasel-popular-terribly.ngrok-free.app 8000
daphne -b 0.0.0.0 -p 8000 schedu.asgi:application
watchfiles "daphne -b 0.0.0.0 -p 8000 schedu.asgi:application" .
Invoke-WebRequest -Uri "http://localhost:8000/api/core/register/department-head/" `
>> -Method POST `
>> -Headers @{"Content-Type"="application/json"} `
>> -Body '{"username": "depthead1", "email": "depthead1@example.com", "password": "securepass123", "phone": "1234567890"}'