# Creates a fake Flask server to test the API client agains. Runs in github actions
from flask import Flask, jsonify

app = Flask(__name__)

# Example data
LEVERS = {
    "lever 1": {"name": "lever 1", "state": True, "springReturn": False},
    "lever 2": {"name": "lever 2", "state": False, "springReturn": False}
}

ADAPTERS = {
    "adapter 1": {"name": "adapter 1", "state": True},
    "adapter 2": {"name": "adapter 2", "state": False}
}

@app.route("/api/levers", methods=["GET", "POST"])
def list_levers():
    return jsonify(list(LEVERS.values()))

@app.route("/api/levers/<name>", methods=["GET", "POST"])
def get_lever(name):
    lever = LEVERS.get(name)
    if lever:
        return jsonify(lever)
    return "HTTP Lever not found", 404

@app.route("/api/adapters", methods=["GET", "POST"])
def list_adapters():
    return jsonify(list(ADAPTERS.values()))

@app.route("/api/adapters/<name>", methods=["GET", "POST"])
def get_adapter(name):
    adapter = ADAPTERS.get(name)
    if adapter:
        return jsonify(adapter)
    return "HTTP Adapter not found", 404

@app.route("/api/switch-on/<name>", methods=["GET", "POST"])
def switch_on(name):
    lever = LEVERS.get(name)
    if lever:
        lever["state"] = True
        return "OK", 200
    return "HTTP Lever not found", 404

@app.route("/api/switch-off/<name>", methods=["GET", "POST"])
def switch_off(name):
    lever = LEVERS.get(name)
    if lever:
        lever["state"] = False
        return "OK", 200
    return "HTTP Lever not found", 404

@app.route("/api/color/<name>/<color>", methods=["GET", "POST"])
def set_color(name, _):
    lever = LEVERS.get(name)
    if lever:
        return "OK", 200
    return "HTTP Lever not found", 404

if __name__ == "__main__":
    app.run(port=8080)