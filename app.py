from flask import Flask, request, jsonify
import requests
from unalix import unshort_url
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Map Link Locator API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; color: #333; }
            h1 { color: #2c3e50; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            code { color: #c7254e; }
            a { color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>Welcome to Map Link Locator API 🚀</h1>
        <p>This API helps you extract addresses and coordinates from Google Maps links or plain addresses using Nominatim (OpenStreetMap).</p>

        <h2>Endpoints</h2>
        <ul>
            <li>
                <strong>/resolve</strong> (POST) - Extract address and coordinates from a Google Maps link.<br>
                <em>JSON body:</em>
                <pre>{
    "url": "https://maps.app.goo.gl/CRHj8dMu9hKy143aA"
}</pre>
            </li>
            <li>
                <strong>/geocode</strong> (POST) - Get latitude and longitude from a plain address.<br>
                <em>JSON body:</em>
                <pre>{
    "address": "New Delhi, India"
}</pre>
            </li>
        </ul>

        <h2>Example Usage in Postman</h2>
        <p>1. Set method to <code>POST</code></p>
        <p>2. Enter the full URL:</p>
        <pre>https://map-link-locator-backend-1.onrender.com/resolve</pre>
        <p>3. Set Headers: <code>Content-Type: application/json</code></p>
        <p>4. Add JSON body as shown above.</p>

        <h2>Notes</h2>
        <ul>
            <li>Make sure to send POST requests for these endpoints.</li>
            <li>Nominatim requires a <code>User-Agent</code>, handled automatically in the backend.</li>
        </ul>

        <p>Happy geocoding! 🌍</p>
    </body>
    </html>
    """


# Route to resolve Google Maps short links and get address using Nominatim
@app.route("/resolve", methods=["POST"])
def resolve_map_link():
    data = request.json
    short_url = data.get("url")

    if not short_url:
        return jsonify({"error": "No URL provided"}), 400

    # Step 1: Unshorten the URL
    long_url = unshort_url(short_url)

    # Step 2: Extract latitude & longitude from URL
    import re
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", long_url)
    if not match:
        return jsonify({"error": "Coordinates not found in URL"}), 400

    lat, lon = match.groups()

    # Step 3: Call Nominatim reverse geocoding API
    nominatim_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {"User-Agent": "MyApp/1.0"}  # Nominatim requires a User-Agent
    response = requests.get(nominatim_url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch address from Nominatim"}), 500

    address = response.json().get("display_name", "Address not found")

    return jsonify({
        "short_url": short_url,
        "long_url": long_url,
        "latitude": lat,
        "longitude": lon,
        "address": address
    })

@app.route("/geocode", methods=["GET"])
def geocode():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Example: treat url as an address (basic test)
    params = {"q": url, "format": "json"}
    res = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers={"User-Agent": "my-app"})
    data = res.json()

    if not data:
        return jsonify({"error": "Address not found"}), 404

    return jsonify({
        "lat": data[0]["lat"],
        "lon": data[0]["lon"]
    })

if __name__ == "__main__":
    app.run(debug=True)
