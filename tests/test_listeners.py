import unittest
import time
from timberborn_api import TimberbornAPI
import requests

class TestListenersTimberbornAPI(unittest.TestCase):
    def setUp(self):
        config = TimberbornAPI.Config(start_adapter_server=False)
        self.api = TimberbornAPI(config)
        # Reset fake server before each test
        requests.post("http://localhost:8080/test/reset")

    def test_lever_listener_trigger(self):
        callback_results = []

        def lever_callback(name, current_state, prev_state):
            callback_results.append((name, current_state, prev_state))

        self.api.register_lever_listener("lever 2", lever_callback)

        # Initial state check: lever 2 is OFF
        lever = self.api.get_lever("lever 2")
        self.assertFalse(lever.state, "lever 2 should start OFF")

        # Change state and manually trigger listeners
        lever.switch_on()
        self.api.check_lever_listeners()
        time.sleep(0.1)  # small delay for cache/thread updates

        self.assertTrue(callback_results, "Callback should have been triggered")
        name, current, prev = callback_results[-1]
        self.assertEqual(name, "lever 2")
        self.assertTrue(current, "Current state should be ON")
        self.assertFalse(prev, "Previous state should be OFF")

        # Toggle again and check callback
        lever.toggle()
        self.api.check_lever_listeners()
        time.sleep(0.1)
        name, current, prev = callback_results[-1]
        self.assertFalse(current, "Current state should be OFF after toggle")
        self.assertTrue(prev, "Previous state should be ON after toggle")

    def test_multiple_lever_listeners(self):
        results1, results2 = [], []

        def cb1(name, current, prev):
            results1.append((current, prev))

        def cb2(name, current, prev):
            results2.append((current, prev))

        self.api.register_lever_listener("lever 1", cb1)
        self.api.register_lever_listener("lever 1", cb2)

        lever = self.api.get_lever("lever 1")
        # lever 1 is initially ON
        lever.switch_off()
        self.api.check_lever_listeners()
        time.sleep(0.1)

        # Both callbacks should have fired
        self.assertEqual(results1[-1], (False, True))
        self.assertEqual(results2[-1], (False, True))

    def test_adapter_listener_trigger(self):
        callback_results = []

        def adapter_callback(name, current_state, prev_state):
            callback_results.append((name, current_state, prev_state))

        self.api.register_adapter_listener("adapter 2", adapter_callback)
        # Initially OFF
        adapter = self.api.get_adapter("adapter 2")
        self.assertFalse(adapter.state, "adapter 2 should start OFF")

        # Manually trigger adapter
        self.api._trigger_adapter("adapter 2", True)
        time.sleep(0.1)
        self.assertTrue(callback_results, "Adapter callback should have been triggered")
        name, current, prev = callback_results[-1]
        self.assertEqual(name, "adapter 2")
        self.assertTrue(current, "Current state should be ON")
        self.assertIsNone(prev, "Previous state should be None for first trigger")

        # Trigger again with same state: should not trigger
        length_before = len(callback_results)
        self.api._trigger_adapter("adapter 2", True)
        time.sleep(0.1)
        self.assertEqual(len(callback_results), length_before, "Callback should not fire for same state")

        # Trigger OFF
        self.api._trigger_adapter("adapter 2", False)
        time.sleep(0.1)
        name, current, prev = callback_results[-1]
        self.assertFalse(current, "Current state should be OFF after trigger")
        self.assertTrue(prev, "Previous state should be ON")

    def test_initialize_adapter_prev_states(self):
        results = []

        def cb(name, current, prev):
            results.append((current, prev))

        self.api.register_adapter_listener("adapter 1", cb)
        # Should initialize state to ON and call callback with prev_state=None
        self.api.initialize_adapter_prev_states()
        time.sleep(0.1)
        self.assertTrue(results, "Callback should have fired on initialization")
        self.assertEqual(results[-1], (True, None))

        # Re-initialize: should call callback with updated prev_state
        self.api.initialize_adapter_prev_states()
        time.sleep(0.1)
        self.assertEqual(results[-1], (True, True), "Callback should be called with previous state updated")

if __name__ == "__main__":
    unittest.main()