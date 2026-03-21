# Payment API Guide

Complete guide for integrating the Idrissimart payment API.  
All payment endpoints live under `/api/`.

---

## Table of Contents

1. [Overview](#overview)
2. [Payment Providers](#payment-providers)
3. [Payment Contexts](#payment-contexts)
4. [Endpoints Reference](#endpoints-reference)
   - [List Available Methods](#1-list-available-payment-methods)
   - [Initiate Payment](#2-initiate-a-payment)
   - [Upload Offline Receipt](#3-upload-offline-payment-receipt)
   - [Capture PayPal Order](#4-capture-paypal-order)
   - [Get Payment Status](#5-get-payment-status)
   - [List My Payments](#6-list-my-payments)
   - [Paymob Webhook Callback](#7-paymob-webhook-callback)
5. [Full Flow Examples](#full-flow-examples)
   - [Paymob Card/Wallet Flow](#paymob-cardwallet-flow)
   - [PayPal Flow](#paypal-flow)
   - [Offline Payment Flow](#offline-payment-flow)
6. [Error Responses](#error-responses)
7. [Environment Configuration](#environment-configuration)

---

## Overview

The payment API supports multiple providers and contexts.  
All endpoints except the Paymob webhook require a **JWT Bearer token**.

```http
Authorization: Bearer {access_token}
```

---

## Payment Providers

| Code            | Description                              | Type    |
|-----------------|------------------------------------------|---------|
| `paymob`        | Card, Meeza, Fawry, Wallet (via Paymob)  | Online  |
| `paypal`        | PayPal global payments                   | Online  |
| `bank_transfer` | Manual bank wire transfer                | Offline |
| `wallet`        | Mobile wallet (Vodafone Cash, etc.)      | Offline |
| `instapay`      | InstaPay transfer                        | Offline |

---

## Payment Contexts

The context controls which payment methods are shown and enforces different rules.

| Context            | When to use                                 |
|--------------------|---------------------------------------------|
| `ad_posting`       | Paying to post a classified ad              |
| `ad_upgrade`       | Upgrading an existing ad (highlighted, etc.)|
| `package_purchase` | Buying a publishing package                 |
| `product_purchase` | Cart / product checkout                     |

---

## Endpoints Reference

### 1. List Available Payment Methods

**`GET /api/payments/methods/`**

Returns the payment methods enabled for a specific context.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Query Parameters:**

| Parameter | Type   | Default      | Description                        |
|-----------|--------|--------------|------------------------------------|
| `context` | string | `ad_posting` | Payment context (see table above)  |

**Example Request:**
```http
GET /api/payments/methods/?context=package_purchase
Authorization: Bearer eyJ0eXAiOiJKV1Qi...
```

**Response (200 OK):**
```json
[
  { "code": "paymob",        "label": "بطاقة بنكية / Paymob" },
  { "code": "paypal",        "label": "PayPal" },
  { "code": "bank_transfer", "label": "تحويل بنكي" },
  { "code": "instapay",      "label": "InstaPay" }
]
```

---

### 2. Initiate a Payment

**`POST /api/payments/initiate/`**

Creates a payment record and returns the data needed to complete it.

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**

| Field              | Type    | Required | Description                                              |
|--------------------|---------|----------|----------------------------------------------------------|
| `provider`         | string  | Yes      | `paymob`, `paypal`, `bank_transfer`, `wallet`, `instapay`|
| `amount`           | decimal | Yes      | Payment amount e.g. `"99.50"`                            |
| `currency`         | string  | No       | Currency code. Default: `"EGP"`                          |
| `description`      | string  | No       | Human-readable description                               |
| `context`          | string  | No       | Payment context. Default: `"ad_posting"`                 |
| `metadata`         | object  | No       | Custom data e.g. `{"package_id": 2, "ad_id": 5}`        |
| `billing_data`     | object  | Paymob   | Customer billing details (see below)                     |
| `notification_url` | URL     | No       | Paymob: server callback URL                              |
| `redirection_url`  | URL     | No       | Paymob: redirect URL after payment                       |
| `return_url`       | URL     | PayPal   | URL after buyer approves PayPal payment                  |
| `cancel_url`       | URL     | PayPal   | URL if buyer cancels PayPal payment                      |

**`billing_data` fields (Paymob):**

```json
{
  "first_name": "Ahmed",
  "last_name": "Ali",
  "email": "ahmed@example.com",
  "phone_number": "+201001234567",
  "city": "Cairo",
  "country": "EG",
  "street": "123 Tahrir St",
  "building": "5",
  "floor": "2",
  "apartment": "10",
  "state": "Cairo",
  "postal_code": "11511"
}
```

Missing fields are automatically filled with `"NA"` or from the user's profile.

---

#### Response — Paymob (201 Created):
```json
{
  "payment_id": 42,
  "provider": "paymob",
  "status": "pending",
  "checkout_url": "https://accept.paymob.com/unifiedcheckout/?publicKey=...&clientSecret=..."
}
```

Redirect the user (or open a WebView) to `checkout_url`.  
Paymob will post the result to your `notification_url` webhook.

---

#### Response — PayPal (201 Created):
```json
{
  "payment_id": 43,
  "provider": "paypal",
  "status": "pending",
  "paypal_order_id": "9XW12345AB678901C",
  "approval_url": "https://www.sandbox.paypal.com/checkoutnow?token=9XW12345AB678901C"
}
```

Redirect the user to `approval_url`.  
After approval, call **[Capture PayPal Order](#4-capture-paypal-order)** with the `paypal_order_id`.

---

#### Response — Offline (bank_transfer / wallet / instapay) (201 Created):
```json
{
  "payment_id": 44,
  "provider": "instapay",
  "status": "pending",
  "message": "Payment record created. Please upload your receipt using POST /payments/{id}/upload_receipt/"
}
```

Show the user your bank/wallet details, then let them upload proof via the receipt endpoint.

---

### 3. Upload Offline Payment Receipt

**`POST /api/payments/{id}/upload_receipt/`**

Attach a photo/screenshot receipt to a pending offline payment.

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Form Data:**

| Field     | Type  | Required | Description            |
|-----------|-------|----------|------------------------|
| `receipt` | image | Yes      | JPEG, PNG, or PDF scan |

**Example Request:**
```bash
curl -X POST https://your-api.com/api/payments/44/upload_receipt/ \
  -H "Authorization: Bearer {access_token}" \
  -F "receipt=@/path/to/receipt.jpg"
```

**Response (200 OK):**
```json
{
  "id": 44,
  "user": { "id": 1, "username": "ahmed" },
  "provider": "bank_transfer",
  "provider_transaction_id": "",
  "amount": "250.00",
  "currency": "EGP",
  "status": "pending",
  "description": "Package purchase",
  "metadata": { "offline_method": "instapay", "context": "package_purchase" },
  "offline_payment_receipt": "http://domain.com/media/payment_receipts/receipt.jpg",
  "created_at": "2024-03-19T10:00:00Z",
  "updated_at": "2024-03-19T10:05:00Z",
  "completed_at": null
}
```

An admin reviews the receipt and manually marks it as completed from the Django admin panel.

---

### 4. Capture PayPal Order

**`POST /api/payments/paypal/capture/`**

Call this after the buyer is redirected back from PayPal with an approved order.

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**

| Field            | Type    | Required | Description                                        |
|------------------|---------|----------|----------------------------------------------------|
| `payment_id`     | integer | Yes      | The internal `payment_id` from the initiate response |
| `paypal_order_id`| string  | Yes      | The PayPal order ID (returned by initiate or from PayPal redirect) |

**Example Request:**
```json
{
  "payment_id": 43,
  "paypal_order_id": "9XW12345AB678901C"
}
```

**Response (200 OK) — Completed:**
```json
{
  "id": 43,
  "user": { "id": 1, "username": "buyer" },
  "provider": "paypal",
  "provider_transaction_id": "8GH98765XY123456Z",
  "amount": "29.99",
  "currency": "USD",
  "status": "completed",
  "description": "Basic Package Purchase",
  "metadata": { "package_id": 1, "context": "package_purchase" },
  "offline_payment_receipt": null,
  "created_at": "2024-03-19T10:00:00Z",
  "updated_at": "2024-03-19T10:02:00Z",
  "completed_at": "2024-03-19T10:02:00Z"
}
```

---

### 5. Get Payment Status

**`GET /api/payments/{id}/payment_status/`**

Quick status check for a specific payment.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "payment_id": 42,
  "status": "completed",
  "provider": "paymob",
  "amount": "99.50",
  "currency": "EGP",
  "provider_transaction_id": "TXN-987654321",
  "created_at": "2024-03-19T10:00:00Z",
  "completed_at": "2024-03-19T10:01:00Z"
}
```

**Payment statuses:**

| Status      | Meaning                              |
|-------------|--------------------------------------|
| `pending`   | Payment initiated, awaiting action   |
| `completed` | Payment successfully captured        |
| `failed`    | Payment was declined or errored      |
| `cancelled` | Payment was cancelled by the user    |
| `refunded`  | Payment has been refunded            |

---

### 6. List My Payments

**`GET /api/payments/`**

Returns the authenticated user's payment history (paginated).

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 44,
      "user": { "id": 1, "username": "ahmed" },
      "provider": "bank_transfer",
      "provider_transaction_id": "",
      "amount": "250.00",
      "currency": "EGP",
      "status": "pending",
      "description": "Package purchase",
      "metadata": { "offline_method": "instapay", "context": "package_purchase" },
      "offline_payment_receipt": "http://domain.com/media/payment_receipts/receipt.jpg",
      "created_at": "2024-03-19T10:00:00Z",
      "updated_at": "2024-03-19T10:05:00Z",
      "completed_at": null
    }
  ]
}
```

---

### 7. Paymob Webhook Callback

**`POST /api/payments/paymob/callback/`**  
**`GET  /api/payments/paymob/callback/`**

This endpoint is called automatically by Paymob's servers after a transaction.  
**Do not call this from your client app.**

Configure this URL in your Paymob dashboard under **"Notification URL"** or pass it as `notification_url` in the initiate call.

- No authentication required.
- Validates the request via HMAC-SHA512 signature.
- Automatically marks the corresponding `Payment` record as `completed` or `failed`.

**Response (200 OK):**
```json
{ "status": "received" }
```

---

## Full Flow Examples

### Paymob Card/Wallet Flow

```
Client                           API                         Paymob
  |                               |                             |
  |-- POST /payments/methods/ --->|                             |
  |<-- [{code:"paymob",...}] -----|                             |
  |                               |                             |
  |-- POST /payments/initiate/ -->|                             |
  |   {provider:"paymob",         |-- POST /v1/intention/ ----->|
  |    amount:100, ...}           |<-- {client_secret:...} -----|
  |<-- {checkout_url:...} --------|                             |
  |                               |                             |
  |-- Open checkout_url in        |                             |
  |   WebView/browser ----------->|                             |
  |                               |                             |
  |                               |<-- Webhook callback --------|
  |                               |    (POST /payments/         |
  |                               |     paymob/callback/)       |
  |                               |-- mark payment completed    |
  |                               |                             |
  |-- GET /payments/{id}/         |                             |
  |   payment_status/ ----------->|                             |
  |<-- {status:"completed"} ------|                             |
```

---

### PayPal Flow

```
Client                           API                         PayPal
  |                               |                             |
  |-- POST /payments/initiate/ -->|                             |
  |   {provider:"paypal",         |-- POST /v2/checkout/------->|
  |    amount:29.99,              |   orders                    |
  |    currency:"USD",            |<-- {id:"9XW...", links}-----|
  |    return_url:...,            |                             |
  |    cancel_url:...}            |                             |
  |<-- {approval_url:...} --------|                             |
  |                               |                             |
  |-- Redirect to approval_url -->|                             |
  |   (buyer approves)            |                             |
  |<-- Redirected to return_url --|                             |
  |   (with token in URL)         |                             |
  |                               |                             |
  |-- POST /payments/             |                             |
  |   paypal/capture/ ----------->|-- POST /v2/checkout/------->|
  |   {payment_id:43,             |   orders/{id}/capture       |
  |    paypal_order_id:"9XW..."} |<-- capture confirmed -------|
  |<-- {status:"completed"} ------|                             |
```

**Extracting the PayPal order ID from the return URL:**

PayPal redirects to your `return_url` with a `token` query parameter:
```
https://yourapp.com/payment/success?token=9XW12345AB678901C&PayerID=ABCDEF123456
```
Use `token` as the `paypal_order_id` in the capture call.

---

### Offline Payment Flow

```
Client                           API
  |                               |
  |-- POST /payments/initiate/ -->|
  |   {provider:"instapay",       |
  |    amount:150, currency:"EGP"}|
  |<-- {payment_id:44,            |
  |     status:"pending",         |
  |     message:"Upload receipt"} |
  |                               |
  |  (User makes bank transfer    |
  |   or InstaPay and screenshots |
  |   the confirmation)           |
  |                               |
  |-- POST /payments/44/          |
  |   upload_receipt/ ----------->|
  |   (multipart: receipt image)  |
  |<-- {offline_payment_receipt:  |
  |     "http://.../receipt.jpg"} |
  |                               |
  |  (Admin reviews receipt in    |
  |   Django admin and marks it   |
  |   as completed)               |
  |                               |
  |-- GET /payments/44/           |
  |   payment_status/ ----------->|
  |<-- {status:"completed"} ------|
```

---

## Error Responses

| HTTP Status | Meaning                                              |
|-------------|------------------------------------------------------|
| 400         | Validation error or invalid request body             |
| 401         | Missing or invalid JWT token                         |
| 503         | Payment gateway not configured (missing credentials) |
| 502         | Payment gateway returned an error                    |

**Example 400 (validation error):**
```json
{
  "provider": ["\"stripe\" is not a valid choice."],
  "amount": ["This field is required."]
}
```

**Example 503 (gateway not configured):**
```json
{
  "error": "Paymob payment gateway is not configured."
}
```

**Example 400 (method not allowed for context):**
```json
{
  "error": "Payment method 'paypal' is not available for context 'ad_posting'."
}
```

---

## Environment Configuration

Set these variables in your environment or `.env` file:

### Paymob
```env
PAYMOB_ENABLED=True
PAYMOB_SECRET_KEY=egy_sk_...
PAYMOB_PUBLIC_KEY=egy_pk_...
PAYMOB_API_KEY=...
PAYMOB_INTEGRATION_ID=...          # Card integration ID
PAYMOB_WALLET_INTEGRATION_ID=...   # Mobile wallet integration ID (optional)
PAYMOB_HMAC_SECRET=...             # For webhook signature verification
PAYMOB_CURRENCY=EGP
```

### PayPal
```env
PAYPAL_CLIENT_ID=AaB...
PAYPAL_CLIENT_SECRET=EbF...
PAYPAL_MODE=sandbox                # Use 'live' for production
```

These values are managed via **Django Constance** and can be updated at runtime from the admin panel at `/admin/constance/config/` without restarting the server.

### Site-level Payment Toggles

In the **Site Configuration** admin panel (`/admin/`), you can globally enable/disable:
- **Allow Online Payment** — controls Paymob and PayPal availability
- **Allow Offline Payment** — controls wallet and InstaPay availability

Per-context method availability is configured via **Payment Method Config** in the admin panel.
