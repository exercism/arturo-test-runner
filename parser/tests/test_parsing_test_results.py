import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import parsing_test_results


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
        got = parsing_test_results.parse_test_results(result)
        want = {
            ("Exercise Name", "First Test"): {
                "passed": True,
                "output": "expects.be:'true? true"
            }
        }
        self.assertEqual(got, want)

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
        got = parsing_test_results.parse_test_results(result)
        want = {
            ("Exercise Name", "First Test"): {
                "passed": False,
                "output": "expects.be:'false? true"
            }
        }
        self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()
