# Nomisma API Reference

Complete API documentation for the Nomisma coin analysis system.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. This may be added in future versions.

---

## Coins API

### List Coins

```http
GET /api/coins
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 50, max: 100)
- `country` (string): Filter by country
- `year_min` (int): Minimum year
- `year_max` (int): Maximum year
- `denomination` (string): Filter by denomination
- `condition_grade` (string): Filter by condition
- `is_for_sale` (boolean): Filter by sale status
- `search` (string): Search across multiple fields
- `sort_by` (string): Field to sort by (default: "created_at")
- `sort_order` (string): "asc" or "desc" (default: "desc")

**Response:**
```json
[
  {
    "id": "uuid",
    "inventory_number": "NOM-0001",
    "country": "United States",
    "denomination": "1 Cent",
    "year": 1943,
    "condition_grade": "Very Fine",
    "primary_image": "path/to/image.jpg",
    "obverse_image": "path/to/obverse.jpg",
    "reverse_image": "path/to/reverse.jpg",
    "estimated_value": 1.50,
    "is_for_sale": false
  }
]
```

### Get Coin

```http
GET /api/coins/{coin_id}
```

**Response:**
```json
{
  "id": "uuid",
  "inventory_number": "NOM-0001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "country": "United States",
  "denomination": "1 Cent",
  "year": 1943,
  "mint_mark": "D",
  "composition": "Steel with zinc coating",
  "condition_grade": "Very Fine",
  "notes": "Wartime steel penny",
  "images": [...],
  "analyses": [...],
  "valuations": [...]
}
```

### Create Coin

```http
POST /api/coins
```

**Request Body:**
```json
{
  "country": "United States",
  "denomination": "1 Cent",
  "year": 1943,
  "mint_mark": "D",
  "composition": "Steel",
  "condition_grade": "Very Fine",
  "notes": "Wartime steel penny"
}
```

### Update Coin

```http
PUT /api/coins/{coin_id}
```

**Request Body:** Same as Create Coin

### Delete Coin

```http
DELETE /api/coins/{coin_id}
```

### Upload Image

```http
POST /api/coins/{coin_id}/images
```

**Form Data:**
- `file`: Image file
- `image_type`: "obverse", "reverse", "edge", or "detail"
- `is_primary`: boolean

---

## Microscope API

### List Devices

```http
GET /api/microscope/devices
```

**Response:**
```json
{
  "success": true,
  "cameras": [
    {
      "index": 0,
      "name": "Camera 0",
      "resolution": "1920x1080",
      "fps": 30,
      "device": "/dev/video0"
    }
  ]
}
```

### Capture Image

```http
POST /api/microscope/capture?camera_index=0&side_hint=obverse
```

**Response:**
```json
{
  "success": true,
  "file_path": "temp/capture_obverse_20240101_120000_abc123.jpg",
  "url": "/images/temp/capture_obverse_20240101_120000_abc123.jpg",
  "timestamp": "20240101_120000",
  "side": {
    "label": "obverse",
    "detected_label": "obverse",
    "confidence": 0.7
  },
  "quality": {
    "blur_score": 210.5,
    "brightness": 114.2,
    "is_blurry": false,
    "is_dark": false,
    "is_bright": false,
    "ok": true
  }
}
```

### Get Preview

```http
GET /api/microscope/preview?camera_index=0
```

Returns a JPEG image stream.

---

## AI Analysis API

### Analyze Coin

```http
POST /api/ai/analyze
```

**Request Body:**
```json
{
  "image_path": "temp/capture_20240101_120000.jpg",
  "coin_id": "uuid" // optional
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "identification": {
      "country": "United States",
      "denomination": "1 Cent",
      "year": 1943,
      "mint_mark": "D",
      "composition": "Steel with zinc coating"
    },
    "condition": {
      "grade": "Very Fine",
      "wear_level": "Light",
      "surface_quality": "Good"
    },
    "defects": {...},
    "authenticity": {
      "assessment": "Likely Authentic",
      "confidence": 85
    }
  },
  "valuation": {
    "estimated_value_low": 0.50,
    "estimated_value_high": 2.00,
    "estimated_value_avg": 1.00,
    "market_demand": "Moderate"
  },
  "valuation_text": "Markdown text with comparisons and pricing notes",
  "valuation_model": "gemini-2.5-flash"
}
```

### Estimate Value

```http
POST /api/ai/estimate-value/{coin_id}
```

**Response:**
```json
{
  "success": true,
  "valuation": {
    "estimated_value_low": 0.50,
    "estimated_value_high": 2.00,
    "estimated_value_avg": 1.00,
    "rarity_score": 3,
    "market_demand": "Moderate",
    "confidence_level": "Medium"
  },
  "formatted_response": "Markdown text with comparisons and pricing notes",
  "model_version": "gemini-2.5-flash"
}
```

### Find Similar Coins

```http
GET /api/ai/similar/{coin_id}?limit=5
```

**Response:**
```json
{
  "success": true,
  "similar_coins": [...],
  "count": 5
}
```

---

## eBay API

### Create Listing

```http
POST /api/ebay/list
```

**Request Body:**
```json
{
  "coin_id": "uuid",
  "listing_title": "1943 Steel Penny - Very Fine Condition",
  "listing_description": "Wartime steel penny in very fine condition...",
  "starting_price": 1.00,
  "buy_it_now_price": 2.00
}
```

**Response:**
```json
{
  "id": "uuid",
  "coin_id": "uuid",
  "ebay_item_id": "1234567890",
  "listing_title": "...",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Listing Status

```http
GET /api/ebay/status/{item_id}
```

**Response:**
```json
{
  "success": true,
  "item_id": "1234567890",
  "status": "Active",
  "current_price": 1.00,
  "quantity_sold": 0,
  "view_count": 15,
  "watchers": 2
}
```

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## Interactive Documentation

For interactive API documentation with the ability to test endpoints, visit:

```
http://localhost:8000/docs
```

This provides a Swagger UI interface for exploring and testing all API endpoints.
