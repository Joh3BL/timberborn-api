# Creates a fake Flask server to test the API client agains. Runs in github actions.
# Uses GET and POST requests differently than the real Timberborn API server, 
# but it should be good enough for basic testing of the client. It will even enforce
# better practices for the client by using GET and POST requests differently.
from flask import Flask, jsonify
import copy

app = Flask(__name__)

# Example data
default_levers = {
    "lever 1": {"name": "lever 1", "state": True, "springReturn": False},
    "lever 2": {"name": "lever 2", "state": False, "springReturn": False}
}

default_adapters = {
    "adapter 1": {"name": "adapter 1", "state": True},
    "adapter 2": {"name": "adapter 2", "state": False}
}

LEVERS = default_levers.copy()

ADAPTERS = default_adapters.copy()

@app.route("/test/reset", methods=["POST"])
def reset():
    global LEVERS
    global ADAPTERS
    LEVERS = copy.deepcopy(default_levers)
    ADAPTERS = copy.deepcopy(default_adapters)
    return "Reset done", 200

@app.route("/api/levers", methods=["GET"])
def list_levers():
    return jsonify(list(LEVERS.values()))

@app.route("/api/levers/<name>", methods=["GET"])
def get_lever(name):
    lever = LEVERS.get(name)
    if lever:
        return jsonify(lever)
    return "HTTP Lever not found", 404

@app.route("/api/adapters", methods=["GET"])
def list_adapters():
    return jsonify(list(ADAPTERS.values()))

@app.route("/api/adapters/<name>", methods=["GET"])
def get_adapter(name):
    adapter = ADAPTERS.get(name)
    if adapter:
        return jsonify(adapter)
    return "HTTP Adapter not found", 404

@app.route("/api/switch-on/<name>", methods=["POST"])
def switch_on(name):
    lever = LEVERS.get(name)
    if lever:
        lever["state"] = True
        return "OK", 200
    return "HTTP Lever not found", 404

@app.route("/api/switch-off/<name>", methods=["POST"])
def switch_off(name):
    lever = LEVERS.get(name)
    if lever:
        lever["state"] = False
        return "OK", 200
    return "HTTP Lever not found", 404

@app.route("/api/color/<name>/<color>", methods=["POST"])
def set_color(name, color):
    lever = LEVERS.get(name)
    if lever:
        return "OK", 200
    return "HTTP Lever not found", 404

if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")