import unittest
from timberborn_api import TimberbornAPI
import requests

class TestOOPTimberbornAPI(unittest.TestCase):
    def setUp(self):
        config = TimberbornAPI.Config(start_adapter_server=False)
        self.api = TimberbornAPI(config)
        requests.post("http://localhost:8080/test/reset")  # Reset fake server values

    def test_get_lever_object(self):
        lever = self.api.get_lever("lever 1")
        self.assertIsInstance(lever, TimberbornAPI.Lever)
        self.assertEqual(lever.name, "lever 1")
        self.assertIn("state", dir(lever))
        self.assertIn("spring_return", dir(lever))

    def test_lever_state_methods(self):
        lever = self.api.get_lever("lever 1")
        lever.switch_on()
        self.assertTrue(lever.state)
        lever.switch_off()
        self.assertFalse(lever.state)

        # Test toggle
        lever.toggle()
        self.assertTrue(lever.state)
        lever.toggle()
        self.assertFalse(lever.state)

    def test_lever_set_color(self):
        lever = self.api.get_lever("lever 1")
        result = lever.set_color("#FF0000")
        self.assertTrue(result)
        result2 = lever.set_color("00FF00")
        self.assertTrue(result2)

    def test_lever_str_repr(self):
        lever = self.api.get_lever("lever 1")
        self.assertEqual(str(lever), "lever 1")
        self.assertEqual(repr(lever), "L(lever 1)")

    def test_get_adapter_object(self):
        adapter = self.api.get_adapter("adapter 1")
        self.assertIsInstance(adapter, TimberbornAPI.Adapter)
        self.assertEqual(adapter.name, "adapter 1")
        self.assertIn("state", dir(adapter))

    def test_adapter_str_repr(self):
        adapter = self.api.get_adapter("adapter 1")
        self.assertEqual(str(adapter), "adapter 1")
        self.assertEqual(repr(adapter), "A(adapter 1)")

    def test_L_and_A_helpers(self):
        lever = self.api.L("lever 1")
        adapter = self.api.A("adapter 1")
        self.assertIsInstance(lever, TimberbornAPI.Lever)
        self.assertIsInstance(adapter, TimberbornAPI.Adapter)
        self.assertEqual(lever.name, "lever 1")
        self.assertEqual(adapter.name, "adapter 1")

if __name__ == "__main__":
    unittest.main()