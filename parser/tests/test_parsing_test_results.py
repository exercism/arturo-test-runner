import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsing_test_results import parse_test_results

class TestResultsParsing(unittest.TestCase):
    def test_parse_test_results_simple_pass(self):
        result = """
specs: [
                #[
                description: "Exercise Name"
                tests: [
                                #[
                                description: "First Test"
                                assertions: [
                                                [
                                                        "expects.be:'true? true"
                                                        true
                                                ]
                                        ]
                                ]
                        ]
                ]
    ]
]
"""
        parsed = parse_test_results(result)
        key = ("Exercise Name", "First Test")
        self.assertIn(key, parsed)
        self.assertTrue(parsed[key]['passed'])
        self.assertEqual(parsed[key]['output'], "expects.be:'true? true")

    def test_parse_test_results_failure_with_message(self):
        result = """
specs: [
                #[
                description: "Exercise Name"
                tests: [
                                #[
                                description: "First Test"
                                assertions: [
                                                [
                                                        "expects.be:'false? true"
                                                        false
                                                ]
                                        ]
                                ]
                        ]
                ]
        ]
        """
        key = ("Exercise Name", "First Test")
        parsed = parse_test_results(result)
        self.assertIn(key, parsed)
        self.assertFalse(parsed[key]['passed'])
        self.assertEqual(parsed[key]['output'], "expects.be:'false? true")

if __name__ == '__main__':
    unittest.main()
