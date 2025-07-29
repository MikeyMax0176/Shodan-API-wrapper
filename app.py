from flask import Flask, request, jsonify
import shodan
import os

app = Flask(__name__)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
