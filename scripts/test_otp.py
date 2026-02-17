"""Test script para verificar el flujo OTP email."""
import urllib.request
import urllib.error
import urllib.parse
import json
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    urllib.request.HTTPRedirectHandler()
)

# Login
login_data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode()
req = urllib.request.Request('http://localhost:5001/login', data=login_data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
try:
    resp = opener.open(req)
    print(f"Login: {resp.status} {resp.url}")
except urllib.error.HTTPError as e:
    print(f"Login error: {e.code}")

# Call OTP API
api_data = json.dumps({'email': 'test@test.com'}).encode()
req2 = urllib.request.Request('http://localhost:5001/api/send_email_otp', data=api_data, method='POST')
req2.add_header('Content-Type', 'application/json')
try:
    resp2 = opener.open(req2)
    print(f"OTP API: {resp2.status}")
    print(f"Body: {resp2.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"OTP API error: {e.code}")
    print(f"Body: {e.read().decode()[:500]}")
