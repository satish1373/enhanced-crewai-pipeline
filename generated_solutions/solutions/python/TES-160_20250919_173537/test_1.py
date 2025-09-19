# test_solution.py
import unittest
from main import Solution

class TestSolution(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()
    
    def test_process(self):
        result = self.solution.process("test data")
        self.assertEqual(result["status"], "success")
        self.assertIn("timestamp", result)
    
    def test_validate_input_valid(self):
        self.assertTrue(self.solution.validate_input("valid data"))
    
    def test_validate_input_empty(self):
        with self.assertRaises(ValueError):
            self.solution.validate_input("")

if __name__ == "__main__":
    unittest.main()