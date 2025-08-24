from flask import Flask, request, jsonify
import requests
from unalix import unshort_url

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the Map Link Locator API 🚀",
        "usage": {
            "/extract-address": "POST request with JSON { 'url': '<your-map-link>' } to extract address from a Google Maps link.",
            "/geocode": "POST request with JSON { 'address': '<your-address>' } to get latitude & longitude using Nominatim."
        },
        "example_requests": {
            "extract_address": {
                "method": "POST",
                "url": "/extract-address",
                "body": {"url": "https://maps.app.goo.gl/3hdtkUmC98GErN2k6"}
            },
            "geocode": {
                "method": "POST",
                "url": "/geocode",
                "body": {"address": "New Delhi, India"}
            }
        }
    })

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
