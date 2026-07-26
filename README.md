# SmartCart AI

SmartCart AI is a lightweight backend for scraping product page details such as title, price, rating, reviews, image, availability, and delivery information.

## Installation

1. Create and activate a Python virtual environment.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the server

Start the FastAPI app with Uvicorn:

```bash
uvicorn backend:app --reload
```

The app will be available at:

- http://127.0.0.1:8000/docs for Swagger UI

## Example API request

```bash
curl -X POST "http://127.0.0.1:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/product"}'
```

## Example response

```json
{
  "title": "Example Product",
  "price": "$19.99",
  "rating": "4.5",
  "reviews": "120",
  "image": "https://example.com/image.jpg",
  "availability": "In stock",
  "delivery": "Free delivery"
}
```
