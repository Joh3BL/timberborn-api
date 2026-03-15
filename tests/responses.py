import requests
import urllib.parse
from pprint import pprint

BASE_URL = "http://localhost:8080/api"

lever_name = "lever 1"
adapter_name = "adapter 1"

lever_enc = urllib.parse.quote(lever_name)
adapter_enc = urllib.parse.quote(adapter_name)


def call_endpoint(description, url):
    print(f"\n--- {description} ---")
    print(f"GET {url}")

    try:
        r = requests.get(url)
        print("Status:", r.status_code)

        try:
            data = r.json()
            print("JSON response:")
            pprint(data, sort_dicts=False)
        except Exception:
            print("Text response:")
            pprint(r.text)

    except Exception as e:
        print("ERROR:")
        pprint(e)


# Lever endpoints
call_endpoint(
    "List levers",
    f"{BASE_URL}/levers"
)

call_endpoint(
    "Get lever",
    f"{BASE_URL}/levers/{lever_enc}"
)

call_endpoint(
    "Switch ON lever",
    f"{BASE_URL}/switch-on/{lever_enc}"
)

call_endpoint(
    "Switch OFF lever",
    f"{BASE_URL}/switch-off/{lever_enc}"
)

call_endpoint(
    "Set lever color",
    f"{BASE_URL}/color/{lever_enc}/FFFFFF"
)

# Adapter endpoints
call_endpoint(
    "List adapters",
    f"{BASE_URL}/adapters"
)

call_endpoint(
    "Get adapter",
    f"{BASE_URL}/adapters/{adapter_enc}"
)

call_endpoint(
    "Get non-existing lever",
    f"{BASE_URL}/levers/non-existing"
)

call_endpoint(
    "Get non-existing adapter",
    f"{BASE_URL}/adapters/non-existing"
)

call_endpoint(
    "Switch ON non-existing lever",
    f"{BASE_URL}/switch-on/non-existing"
)

call_endpoint(
    "Set color of non-existing lever",
    f"{BASE_URL}/color/non-existing/FFFFFF"
)


print("\nFinished testing all endpoints.")