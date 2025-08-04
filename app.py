from flask_cors import CORS
from flask import Flask, request, jsonify
import shodan
import os

app = Flask(__name__)
CORS(app)
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
api = shodan.Shodan(SHODAN_API_KEY)

@app.route("/ip-info", methods=["GET"])
def ip_info():
    ip = request.args.get("ip")
    try:
        host = api.host(ip)
        return jsonify(host)
    except shodan.APIError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    try:
        results = api.search(query)
        return jsonify(results)
    except shodan.APIError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/openapi.json")
def openapi_spec():
    from flask import send_from_directory
    return send_from_directory('.', 'openapi.json', mimetype='application/json')
# ---------- Brave Search helper & /brave-seed ----------
import requests, socket
from urllib.parse import urlparse

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_URL     = "https://api.search.brave.com/res/v1/web/search"

def brave_web_search(query: str, count: int = 20):
    """Return Brave Search results (title, url, snippet)."""
    hdr = {"X-Subscription-Token": BRAVE_API_KEY,
           "Accept": "application/json"}
    prm = {"q": query, "count": count}
    r = requests.get(BRAVE_URL, headers=hdr, params=prm, timeout=15)
    r.raise_for_status()
    return r.json()["web"]["results"]

@app.route("/brave-seed")
def brave_seed():
    """
    ?q=<search string>&count=20
    → {"ips": ["93.184.216.34", "198.51.100.7", …]}
    """
    q     = request.args.get("q")
    count = int(request.args.get("count", 20))
    if not q:
        return jsonify({"error": "missing q param"}), 400

    hosts = {urlparse(r["url"]).hostname
             for r in brave_web_search(q, count) if r.get("url")}
    ips = []
    for h in hosts:
        try:
            ips.append(socket.gethostbyname(h))
        except Exception:
            pass
    return jsonify({"ips": ips})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
