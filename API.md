# gpxplotter API Documentation

## Overview

The gpxplotter API provides a REST endpoint to retrieve route names from GPX files stored in a configured directory.

## Running the API Server

### Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

### Starting the Server

Run the Flask application:

```bash
python app.py
```

By default, the server runs on `http://localhost:5000`.

### Configuration

You can configure the server using environment variables:

- `GPX_DATA_DIR`: Directory containing GPX files (default: `./examples/jupyter`)
- `PORT`: Server port (default: `5000`)
- `FLASK_DEBUG`: Enable debug mode (default: `False`)

Example:

```bash
export GPX_DATA_DIR=/path/to/your/gpx/files
export PORT=8080
export FLASK_DEBUG=True
python app.py
```

## API Endpoints

### GET /

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "gpxplotter API",
  "version": "1.0.0",
  "endpoints": {
    "/": "This information page",
    "/api/health": "Health check endpoint",
    "/api/routes": "GET list of all route names"
  }
}
```

### GET /api/health

Health check endpoint that returns the server status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "gpx_data_dir": "./examples/jupyter",
  "gpx_files_found": 2
}
```

### GET /api/routes

Returns a list of all route names from GPX files in the configured directory.

**Response:**
```json
{
  "routes": [
    {
      "name": "Morning Run",
      "type": "running",
      "file": "example1.gpx"
    },
    {
      "name": "Evening Bike Ride",
      "type": "cycling",
      "file": "example3.gpx"
    }
  ],
  "count": 2
}
```

**Response Fields:**
- `routes`: Array of route objects
  - `name`: The name of the route from the GPX file
  - `type`: The type of activity (if specified in GPX)
  - `file`: The source GPX filename
- `count`: Total number of routes found

**Error Response (500):**
```json
{
  "error": "error message",
  "message": "Failed to retrieve routes"
}
```

## Example Usage

### Using curl

```bash
# Get all routes
curl http://localhost:5000/api/routes

# Health check
curl http://localhost:5000/api/health
```

### Using Python requests

```python
import requests

# Get all routes
response = requests.get('http://localhost:5000/api/routes')
routes = response.json()

print(f"Found {routes['count']} routes:")
for route in routes['routes']:
    print(f"  - {route['name']} ({route['type']}) from {route['file']}")
```

### Using JavaScript fetch

```javascript
// Get all routes
fetch('http://localhost:5000/api/routes')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} routes:`);
    data.routes.forEach(route => {
      console.log(`  - ${route.name} (${route.type}) from ${route.file}`);
    });
  });
```

## Development

### Running in Development Mode

```bash
export FLASK_DEBUG=True
python app.py
```

### Testing with Sample Data

The repository includes sample GPX files in `examples/jupyter/`:
- `example1.gpx`
- `example3.gpx`

These will be used by default when you start the server.
