# 📚 API Documentation - Sign Language App

## Base URL

```
http://localhost:5000
```

---

## Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Homepage |
| GET | `/video_feed` | Live video stream |
| GET | `/api/prediction` | Get current prediction |
| GET | `/api/history` | Get prediction history |
| GET | `/api/detected_text` | Get current text |
| POST | `/api/detected_text` | Modify detected text |
| GET | `/api/health` | Health check |

---

## Detailed Endpoint Documentation

### 1. GET `/` - Homepage

Returns the main HTML interface.

#### Request
```http
GET / HTTP/1.1
Host: localhost:5000
```

#### Response
- **Status**: 200 OK
- **Content-Type**: text/html
- **Body**: HTML page

#### Example
```bash
curl http://localhost:5000/
```

---

### 2. GET `/video_feed` - Live Video Stream

Returns continuous MJPEG video stream from webcam.

#### Request
```http
GET /video_feed HTTP/1.1
Host: localhost:5000
```

#### Response
- **Status**: 200 OK
- **Content-Type**: multipart/x-mixed-replace; boundary=frame
- **Body**: JPEG frame chunks

#### Headers
```
Content-Type: multipart/x-mixed-replace; boundary=frame
Cache-Control: max-age=0, must-revalidate
Connection: keep-alive
```

#### Frame Format
```
--frame
Content-Type: image/jpeg
Content-Length: 12345

[JPEG Binary Data]
--frame
...
```

#### Example (HTML)
```html
<img src="http://localhost:5000/video_feed" alt="Webcam" />
```

#### Notes
- Continuous stream (doesn't end)
- Update rate depends on configuration
- Automatically resizes frame in response
- Includes prediction drawn on frame

---

### 3. GET `/api/prediction` - Current Prediction

Returns the current gesture prediction with confidence score.

#### Request
```http
GET /api/prediction HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

#### Response (Success)
- **Status**: 200 OK
- **Content-Type**: application/json

```json
{
    "character": "'A'",
    "confidence": 87,
    "status": "success"
}
```

#### Response (Error)
- **Status**: 500 Internal Server Error

```json
{
    "error": "Predictor not initialized",
    "status": "error"
}
```

#### Response Parameters

| Field | Type | Description |
|-------|------|-------------|
| `character` | string | Predicted letter (A-Z) or '?' |
| `confidence` | int | Confidence as percentage (0-100) |
| `status` | string | "success" or "error" |

#### Example Request
```bash
curl http://localhost:5000/api/prediction
```

#### Example Response
```json
{
    "character": "'A'",
    "confidence": 92,
    "status": "success"
}
```

#### JavaScript Example
```javascript
fetch('/api/prediction')
    .then(response => response.json())
    .then(data => {
        console.log(`Predicted: ${data.character}`);
        console.log(`Confidence: ${data.confidence}%`);
    })
    .catch(error => console.error('Error:', error));
```

#### Update Frequency
- Called every 500ms by frontend
- If not needed, client can adjust interval
- No rate limiting

---

### 4. GET `/api/history` - Prediction History

Returns the last 30 predictions with timestamps.

#### Request
```http
GET /api/history HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

#### Response
- **Status**: 200 OK
- **Content-Type**: application/json

```json
{
    "history": [
        {
            "character": "'A'",
            "confidence": 0.92,
            "timestamp": "2024-01-01T14:30:45.123456"
        },
        {
            "character": "'B'",
            "confidence": 0.87,
            "timestamp": "2024-01-01T14:30:46.234567"
        }
    ],
    "count": 2
}
```

#### Response Parameters

| Field | Type | Description |
|-------|------|-------------|
| `history` | array | List of predictions |
| `history[].character` | string | Predicted letter |
| `history[].confidence` | float | Confidence (0-1) |
| `history[].timestamp` | string | ISO 8601 timestamp |
| `count` | int | Total items in history |

#### Example Request
```bash
curl http://localhost:5000/api/history
```

#### JavaScript Example
```javascript
fetch('/api/history')
    .then(response => response.json())
    .then(data => {
        console.log(`Total predictions: ${data.count}`);
        data.history.forEach(item => {
            console.log(`${item.character}: ${item.confidence.toFixed(2)}`);
        });
    });
```

#### Notes
- Returns up to 30 most recent predictions
- Older predictions are automatically discarded
- Useful for debugging and analysis

---

### 5. GET `/api/detected_text` - Get Current Text

Returns the currently detected/built text.

#### Request
```http
GET /api/detected_text HTTP/1.1
Host: localhost:5000
```

#### Response
- **Status**: 200 OK
- **Content-Type**: application/json

```json
{
    "text": "HELLO WORLD",
    "length": 11
}
```

#### Response Parameters

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Current detected text |
| `length` | int | Character count |

#### Example Request
```bash
curl http://localhost:5000/api/detected_text
```

#### Example Response
```json
{
    "text": "SIGN LANGUAGE",
    "length": 13
}
```

---

### 6. POST `/api/detected_text` - Modify Text

Adds, removes, or clears detected text.

#### Request
```http
POST /api/detected_text HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
    "action": "append",
    "char": "A"
}
```

#### Request Body Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | Yes | Action type: "append", "clear", "backspace" |
| `char` | string | No* | Character to append (*required for "append") |

#### Response (Success)
- **Status**: 200 OK
- **Content-Type**: application/json

```json
{
    "text": "HELLO A",
    "status": "success"
}
```

#### Response (Error)
- **Status**: 400 Bad Request

```json
{
    "error": "Invalid action",
    "status": "error"
}
```

#### Actions

##### append
Adds a character to the text.

```json
{
    "action": "append",
    "char": "A"
}
```

Response:
```json
{
    "text": "HELLO A",
    "status": "success"
}
```

##### clear
Removes all text.

```json
{
    "action": "clear"
}
```

Response:
```json
{
    "text": "",
    "status": "success"
}
```

##### backspace
Removes the last character.

```json
{
    "action": "backspace"
}
```

Response:
```json
{
    "text": "HELLO",
    "status": "success"
}
```

#### Example Requests

**Add character:**
```bash
curl -X POST http://localhost:5000/api/detected_text \
    -H "Content-Type: application/json" \
    -d '{"action": "append", "char": "H"}'
```

**Clear text:**
```bash
curl -X POST http://localhost:5000/api/detected_text \
    -H "Content-Type: application/json" \
    -d '{"action": "clear"}'
```

**Remove last character:**
```bash
curl -X POST http://localhost:5000/api/detected_text \
    -H "Content-Type: application/json" \
    -d '{"action": "backspace"}'
```

#### JavaScript Example
```javascript
// Add character
fetch('/api/detected_text', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action: 'append', char: 'A'})
})
.then(r => r.json())
.then(data => console.log(data.text));
```

---

### 7. GET `/api/health` - Health Check

Returns server and model status.

#### Request
```http
GET /api/health HTTP/1.1
Host: localhost:5000
```

#### Response
- **Status**: 200 OK
- **Content-Type**: application/json

```json
{
    "status": "healthy",
    "model_loaded": true,
    "timestamp": "2024-01-01T14:30:00.000000"
}
```

#### Response Parameters

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "healthy" or "error" |
| `model_loaded` | bool | Whether ML model is loaded |
| `timestamp` | string | Server timestamp (ISO 8601) |

#### Example Request
```bash
curl http://localhost:5000/api/health
```

#### Example Response
```json
{
    "status": "healthy",
    "model_loaded": true,
    "timestamp": "2024-01-01T14:35:22.456789"
}
```

#### Use Cases
- Verify server is running
- Check if model loaded successfully
- Monitor uptime
- Debugging connection issues

---

## Error Responses

### 404 Not Found

```json
{
    "error": "Route not found"
}
```

### 500 Internal Server Error

```json
{
    "error": "Internal server error"
}
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 404 Route not found | Incorrect URL | Check endpoint spelling |
| 500 Model not loaded | training not done | Run `python train_model.py` |
| 500 Webcam error | Camera not available | Check permissions, restart |
| 400 Bad request | Invalid JSON | Validate JSON syntax |

---

## Rate Limiting

Currently **no rate limiting** is implemented.

For production deployment, add:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/prediction')
@limiter.limit("30 per minute")
def get_prediction():
    ...
```

---

## CORS Configuration

For cross-origin requests, add to `app.py`:

```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

---

## Authentication

Currently **no authentication** is required.

For production, add:
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == 'admin' and password == 'secret':
        return 'admin'
    return None

@app.route('/api/prediction')
@auth.login_required
def get_prediction():
    ...
```

---

## Webhooks

Not currently implemented. Could be added for:
- Predictions reaching certain confidence
- Text generation events
- Error notifications

---

## Testing Endpoints

### Using cURL

```bash
# Health check
curl -X GET http://localhost:5000/api/health

# Get prediction
curl -X GET http://localhost:5000/api/prediction

# Get history
curl -X GET http://localhost:5000/api/history

# Get text
curl -X GET http://localhost:5000/api/detected_text

# Add character
curl -X POST http://localhost:5000/api/detected_text \
    -H "Content-Type: application/json" \
    -d '{"action": "append", "char": "H"}'
```

### Using Postman

1. Import collection from docs
2. Set base URL: `http://localhost:5000`
3. Send requests
4. View responses

### Using Python

```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Get prediction
response = requests.get('http://localhost:5000/api/prediction')
print(response.json())

# Add character
response = requests.post(
    'http://localhost:5000/api/detected_text',
    json={'action': 'append', 'char': 'A'}
)
print(response.json())
```

---

## WebSocket Support

Not currently implemented. Could be added for:
- Real-time bidirectional communication
- Reduced latency
- Streaming predictions
- Live multiplayer features

---

## API Versioning

Currently using `/api/` (v1 implied)

For future versions:
```
/api/v1/prediction
/api/v2/prediction
```

---

## Change Log

### v1.0.0 (Current)
- GET `/` - Homepage
- GET `/video_feed` - Video stream
- GET `/api/prediction` - Predictions
- GET `/api/history` - History
- GET/POST `/api/detected_text` - Text management
- GET `/api/health` - Health check

---

## Examples & Tutorials

### Complete Prediction Loop

```javascript
async function predictLoop() {
    const response = await fetch('/api/prediction');
    const data = await response.json();
    
    if (data.status === 'success') {
        console.log(`Character: ${data.character}`);
        console.log(`Confidence: ${data.confidence}%`);
        
        // Add to text if high confidence
        if (data.confidence > 80) {
            await addCharacter(data.character);
        }
    }
}

setInterval(predictLoop, 500);
```

### Text Building

```javascript
async function addCharacter(char) {
    const response = await fetch('/api/detected_text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'append', char})
    });
    
    const data = await response.json();
    console.log(`Text: ${data.text}`);
}

async function clearText() {
    await fetch('/api/detected_text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'clear'})
    });
}
```

### Error Handling

```javascript
async function safeFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification('API Error: ' + error.message, 'error');
        return null;
    }
}
```

---

This API documentation covers all current endpoints and their usage.
