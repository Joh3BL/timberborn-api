# Basic tests for the Timberborn API client. 
# These tests assume that the Timberborn API server is running and has a known state
# or that the fake server is running with the expected data.

from timberborn_api import TimberbornAPI

api = TimberbornAPI(base_url="http://localhost:8080/api")

def test_list_levers():
    levers = api.list_levers()
    assert "lever 1" in levers
    assert levers["lever 1"]["state"] is True
    assert levers["lever 1"]["springReturn"] is False

def test_get_lever():
    lever = api.get_lever("lever 2")
    assert lever["state"] is False
    assert lever["springReturn"] is False

def test_set_lever():
    api.set_lever("lever 2", True)
    lever = api.get_lever("lever 2")
    assert lever["state"] is True

def test_set_color():
    api.set_color("lever 1", "#FF0000")

def test_list_adapters():
    adapters = api.list_adapters()
    assert "adapter 1" in adapters
    assert adapters["adapter 1"] is True

def test_get_adapter():
    adapter = api.get_adapter("adapter 2")
    assert adapter is False

def run_test(test_func):
    try:
        test_func()
        return True
    except AssertionError as e:
        print(f"{test_func.__name__} failed: {e}")
        return False
    except Exception as e:
        print(f"{test_func.__name__} failed with an unexpected error: {e}")
        return False

if __name__ == "__main__":
    tests = [
        test_list_levers,
        test_get_lever,
        test_set_lever,
        test_set_color,
        test_get_adapter,
        test_list_adapters
    ]
    
    failiures = 0
    for test in tests:
        if not run_test(test):
            failiures += 1
    
    print("\n--- Test Summary ---")
    if failiures == 0:
        print("All basic tests passed!")
    else:
        print(f"{failiures} test(s) failed. Please check the output above for details.")