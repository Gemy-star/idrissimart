# Phone OTP Verification API Guide

This guide explains how to use the phone number OTP (One-Time Password) verification endpoints.

---

## Overview

The verification flow has two steps:

1. **Send OTP** — provide a phone number, an SMS is sent with a code
2. **Verify OTP** — submit the code to confirm ownership and mark the phone as verified

A third endpoint lets you **check the current verification status** at any time.

---

## Authentication

All three endpoints require a valid JWT access token in the `Authorization` header.

```
Authorization: Bearer <access_token>
```

To obtain a token:

```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

---

## Endpoints

### 1. Send OTP

Sends a 6-digit OTP via SMS to the provided phone number. The number is saved to the user's profile.

```
POST /api/auth/send-otp/
```

**Request**

```json
{
  "phone": "+201234567890"
}
```

| Field | Type   | Required | Description                      |
|-------|--------|----------|----------------------------------|
| phone | string | Yes      | Phone number (with country code) |

**Success Response — `200 OK`**

```json
{
  "detail": "تم إرسال رمز التحقق بنجاح"
}
```

**Error Response — `400 Bad Request`**

```json
{
  "detail": "فشل في إرسال رمز التحقق"
}
```

---

### 2. Verify OTP

Submits the OTP code received via SMS. On success, the user's phone is marked as verified (`is_mobile_verified = true`).

```
POST /api/auth/verify-otp/
```

**Request**

```json
{
  "otp_code": "123456"
}
```

| Field    | Type   | Required | Description              |
|----------|--------|----------|--------------------------|
| otp_code | string | Yes      | 4–6 digit code from SMS  |

**Success Response — `200 OK`**

```json
{
  "detail": "تم التحقق من الجوال بنجاح",
  "is_mobile_verified": true
}
```

**Error Responses — `400 Bad Request`**

| Scenario                  | `detail` message                  |
|---------------------------|-----------------------------------|
| Wrong code                | رمز التحقق غير صحيح               |
| Code expired              | انتهت صلاحية رمز التحقق           |
| No code was sent yet      | لم يتم إرسال رمز التحقق           |

---

### 3. Check Verification Status

Returns whether the authenticated user's phone is currently verified.

```
GET /api/auth/verify-otp/
```

**Success Response — `200 OK`**

```json
{
  "is_mobile_verified": false,
  "phone": "+201234567890"
}
```

| Field              | Type    | Description                        |
|--------------------|---------|------------------------------------|
| is_mobile_verified | boolean | `true` if phone has been verified  |
| phone              | string  | The phone number on file (or null) |

---

## Complete Flow Example

### Step 1 — Login and get token

```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "ahmed",
  "password": "secret123"
}
```

```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

---

### Step 2 — Send OTP

```http
POST /api/auth/send-otp/
Authorization: Bearer eyJ...
Content-Type: application/json

{
  "phone": "+201234567890"
}
```

```json
{
  "detail": "تم إرسال رمز التحقق بنجاح"
}
```

The user receives an SMS with a code such as `847291`.

---

### Step 3 — Verify OTP

```http
POST /api/auth/verify-otp/
Authorization: Bearer eyJ...
Content-Type: application/json

{
  "otp_code": "847291"
}
```

```json
{
  "detail": "تم التحقق من الجوال بنجاح",
  "is_mobile_verified": true
}
```

---

### Step 4 — Confirm status (optional)

```http
GET /api/auth/verify-otp/
Authorization: Bearer eyJ...
```

```json
{
  "is_mobile_verified": true,
  "phone": "+201234567890"
}
```

---

## Notes

- The OTP expires after a configurable number of minutes (default: **10 minutes**). If it expires, repeat Step 2 to get a new code.
- Calling `send-otp` again with a new phone number will overwrite the previously stored number and reset verification status.
- The `is_mobile_verified` field is also available on the full user profile endpoint: `GET /api/users/me/`.
- SMS delivery depends on the SMS provider configured in the site settings (e.g., Twilio).
