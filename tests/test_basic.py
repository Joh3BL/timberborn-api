import unittest
from timberborn_api import TimberbornAPI
import requests

class TestBasicTimberbornAPI(unittest.TestCase):
    def setUp(self):
        # Start API object after fake server is up
        config = TimberbornAPI.Config(start_adapter_server=False)
        self.api = TimberbornAPI(config)
        # Reset fake server values
        requests.post("http://localhost:8080/test/reset")

    def test_list_levers(self):
        levers = self.api.list_levers()
        self.assertIn("lever 1", levers, "lever 1 should exist in list_levers()")
        self.assertIn("lever 2", levers, "lever 2 should exist in list_levers()")
        # Check their states
        self.assertTrue(levers["lever 1"].state, "lever 1 should start ON")
        self.assertFalse(levers["lever 2"].state, "lever 2 should start OFF")
        # Test cached lever retrieval
        lever1_cached = self.api.get_lever("lever 1")
        self.assertTrue(lever1_cached.state, "Cached lever 1 should match state")

    def test_get_lever(self):
        lever = self.api.get_lever("lever 2")
        self.assertFalse(lever.state, "lever 2 should initially be OFF")
        # Test switching on
        lever.switch_on()
        self.assertTrue(lever.state, "lever 2 should be ON after switch_on()")
        # Test switching off
        lever.switch_off()
        self.assertFalse(lever.state, "lever 2 should be OFF after switch_off()")
        # Test toggle
        lever.toggle()
        self.assertTrue(lever.state, "lever 2 should be ON after toggle()")
        lever.toggle()
        self.assertFalse(lever.state, "lever 2 should be OFF after toggle() again")

    def test_set_lever(self):
        # Set multiple times and verify
        self.api.set_lever("lever 2", True)
        lever = self.api.get_lever("lever 2")
        self.assertTrue(lever.state, "lever 2 should be ON after set_lever(True)")
        self.api.set_lever("lever 2", False)
        lever = self.api.get_lever("lever 2")
        self.assertFalse(lever.state, "lever 2 should be OFF after set_lever(False)")

    def test_set_color(self):
        # Test both formats
        result1 = self.api.set_color("lever 1", "#FF0000")
        result2 = self.api.set_color("lever 1", "00FF00")
        self.assertTrue(result1, "Setting lever 1 color with #RRGGBB should succeed")
        self.assertTrue(result2, "Setting lever 1 color with RRGGBB should succeed")

    def test_get_adapter(self):
        adapter = self.api.get_adapter("adapter 2")
        self.assertFalse(adapter.state, "adapter 2 should initially be OFF")
        adapter_obj = self.api.get_adapter("adapter 1")
        self.assertTrue(adapter_obj.state, "adapter 1 should initially be ON")

    def test_list_adapters(self):
        adapters = self.api.list_adapters()
        self.assertIn("adapter 1", adapters, "adapter 1 should exist in list_adapters()")
        self.assertIn("adapter 2", adapters, "adapter 2 should exist in list_adapters()")
        self.assertTrue(adapters["adapter 1"].state, "adapter 1 should be ON")
        self.assertFalse(adapters["adapter 2"].state, "adapter 2 should be OFF")
        # Test cached adapter retrieval
        adapter2_cached = self.api.get_adapter("adapter 2")
        self.assertFalse(adapter2_cached.state, "Cached adapter 2 state should match")

if __name__ == "__main__":
    unittest.main()