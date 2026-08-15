import time, requests

s=time.time()
r=requests.post('http://127.0.0.1:8000/auth/login', data={'username':'admin@kazilink.com','password':'Admin123!'})
print('login', r.status_code, time.time()-s)

start=time.time()
try:
    tok=r.json().get('access_token')
    r2=requests.get('http://127.0.0.1:8000/users/me', headers={'Authorization':'Bearer '+tok})
    print('me', r2.status_code, time.time()-start)
except Exception as e:
    print('error getting /users/me', e)
