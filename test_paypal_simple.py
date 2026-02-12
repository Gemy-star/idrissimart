#!/usr/bin/env python
"""
Simple PayPal Authentication Test
Tests if PayPal credentials work with the PayPal API
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
os.environ["DJANGO_LOG_FILE"] = os.path.join(os.getcwd(), "test.log")

django.setup()

import requests
from constance import config

print("\n" + "=" * 60)
print("PAYPAL AUTHENTICATION TEST")
print("=" * 60)

# Get credentials
client_id = config.PAYPAL_CLIENT_ID
client_secret = config.PAYPAL_CLIENT_SECRET
mode = config.PAYPAL_MODE

print(f"\nMode: {mode}")
print(
    f"Client ID: {client_id[:20]}..."
    if len(client_id) > 20
    else f"Client ID: {client_id}"
)
print(
    f"Secret: {client_secret[:20]}..."
    if len(client_secret) > 20
    else f"Secret: {client_secret}"
)

# Determine correct URL based on mode
if mode.lower() == "sandbox":
    base_url = "https://api-m.sandbox.paypal.com"
else:
    base_url = "https://api-m.paypal.com"

print(f"\nUsing endpoint: {base_url}")

# Try to get access token
url = f"{base_url}/v1/oauth2/token"
headers = {"Accept": "application/json", "Accept-Language": "en_US"}
data = {"grant_type": "client_credentials"}

print(f"\nRequest URL: {url}")
print(f"Authenticating with Client ID...")

try:
    response = requests.post(
        url, headers=headers, data=data, auth=(client_id, client_secret), timeout=10
    )

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"\n✓ SUCCESS! Access token obtained:")
        print(f"  Token: {access_token[:50]}...")
        print(f"  Token Type: {token_data.get('token_type')}")
        print(f"  Expires In: {token_data.get('expires_in')} seconds")
    else:
        print(f"\n✗ AUTHENTICATION FAILED!")
        print(f"\nResponse Body:")
        print(response.text)

        # Additional diagnostics
        print("\n" + "=" * 60)
        print("DIAGNOSTICS")
        print("=" * 60)

        if response.status_code == 401:
            print("⚠️  401 Unauthorized - Invalid credentials")
            print("\nPossible issues:")
            print("1. PAYPAL_CLIENT_ID is incorrect")
            print("2. PAYPAL_CLIENT_SECRET is incorrect")
            print("3. The credentials don't match the mode (sandbox vs live)")
            print("4. Check PayPal Developer Dashboard: https://developer.paypal.com/")
        elif response.status_code == 400:
            print("⚠️  400 Bad Request - Malformed request")
            error_data = response.json()
            print(f"Error: {error_data.get('error')}")
            print(f"Error Description: {error_data.get('error_description')}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"\n✗ CONNECTION ERROR!")
    print(f"Error: {str(e)}")
    print("\nPossible issues:")
    print("1. Network connectivity problem")
    print("2. PayPal API is temporarily unavailable")
    print("3. Firewall or proxy blocking the request")

print("\n" + "=" * 60)
