import unittest
from timberborn_api import TimberbornAPI
import requests

class TestTimberbornAPI(unittest.TestCase):
    def setUp(self):
        # Start API object after fake server is up
        self.api = TimberbornAPI()
        requests.get("http://localhost:8080/test/reset")  # Reset fake server values, just in case

    def test_list_levers(self):
        levers = self.api.list_levers()
        self.assertIn("lever 1", levers)
        self.assertTrue(levers["lever 1"].state)

    def test_get_lever(self):
        lever = self.api.get_lever("lever 2")
        self.assertFalse(lever.state)

    def test_set_lever(self):
        self.api.set_lever("lever 2", True)
        lever = self.api.get_lever("lever 2")
        self.assertTrue(lever.state)

    def test_set_color(self):
        result = self.api.set_color("lever 1", "#FF0000")
        self.assertTrue(result)

    def test_get_adapter(self):
        adapter = self.api.get_adapter("adapter 2")
        self.assertFalse(adapter.state)

    def test_list_adapters(self):
        adapters = self.api.list_adapters()
        self.assertIn("adapter 2", adapters)
        self.assertFalse(adapters["adapter 2"].state)