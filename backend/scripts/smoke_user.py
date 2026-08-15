import json, urllib.request, urllib.parse

try:
    data = urllib.parse.urlencode({'username':'admin@kazilink.com','password':'Admin123!'}).encode()
    req = urllib.request.Request('http://127.0.0.1:8000/auth/login', data=data, method='POST')
    req.add_header('Content-Type','application/x-www-form-urlencoded')
    resp = urllib.request.urlopen(req)
    tok = json.load(resp)['access_token']
    req2 = urllib.request.Request('http://127.0.0.1:8000/users/me')
    req2.add_header('Authorization', f'Bearer {tok}')
    resp2 = urllib.request.urlopen(req2)
    print('STATUS', resp2.getcode())
    print(resp2.read().decode())
except Exception as e:
    import traceback; traceback.print_exc()
