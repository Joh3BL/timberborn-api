import unittest
from timberborn_api import TimberbornAPI

api =  TimberbornAPI()

class TestTimberbornAPI(unittest.TestCase):
    # Test basic functions
    def test_list_levers(self):
        levers = api.list_levers()
        self.assertIn("lever 1", levers)
        self.assertTrue(levers["lever 1"].state)

    def test_get_lever(self):
        lever = api.get_lever("lever 2")
        self.assertFalse(lever.state)

    def test_set_lever(self):
        api.set_lever("lever 2", True)
        lever = api.get_lever("lever 2")
        self.assertTrue(lever.)

    def test_set_color(self):
        result = api.set_color("lever 1", "#FF0000")
        self.assertTrue(result)

    def test_get_adapter(self):
        adapter = api.get_adapter("adapter 2")
        self.assertFalse(adapter.state)

    def test_list_adapters(self):
        adapters = api.list_adapters()
        self.assertIn("adapter 2", adapters)
        self.assertFalse(adapters["adapter 2"].state)

if __name__ == '__main__':
    unittest.main()