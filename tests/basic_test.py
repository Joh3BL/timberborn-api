# Basic tests for the Timberborn API client. 
# These tests assume that the Timberborn API server is running and has a known state
# or that the fake server is running with the expected data.

from timberborn_api import TimberbornAPI

api = TimberbornAPI(base_url="http://localhost:8080/api")

def test_list_levers():
    levers = api.list_levers()
    assert "lever 1" in levers
    assert levers["lever 1"]["state"] is True
    print("list_levers passed")

def test_get_lever():
    lever = api.get_lever("lever 2")
    assert lever["state"] is False
    print("get_lever passed")

def test_set_lever():
    api.set_lever("lever 2", True)
    lever = api.get_lever("lever 2")
    assert lever["state"] is True
    print("set_lever passed")

def test_set_color():
    result = api.set_color("lever 1", "#FF0000")
    assert result is True
    lever = api.get_lever("lever 1")
    assert lever.get("color") == "FF0000"
    print("set_color passed")

def test_get_adapter():
    adapter = api.get_adapter("adapter 2")
    assert adapter["state"] is False
    print("get_adapter passed")

if __name__ == "__main__":
    test_list_levers()
    test_get_lever()
    test_set_lever()
    test_set_color()
    test_get_adapter()
    print("All basic tests passed!")