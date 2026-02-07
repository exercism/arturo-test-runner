import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import build_output

class TestResultsParser(unittest.TestCase):
    def test_report_single_test_success(self):
        expected_tests = [{
            "suite": "Exercise Name",
            "name": "First Test Passing",
            "code": "expects.be:'true? @[true]"
        }]
        parsed_results = {("Exercise Name", "First Test Passing"): {"passed": True, "output": None}}
        
        output = build_output(expected_tests, parsed_results, None)
        
        self.assertEqual(output["status"], "pass")
        self.assertEqual(len(output["tests"]), 1)
        self.assertEqual(output["tests"][0]["status"], "pass")

    def test_report_failure_if_a_test_fails(self):
        expected_tests = [{
            "suite": "Exercise Name",
            "name": "First Test Failing",
            "code": "expects.be:'true? @[false]"
        }]
        parsed_results = {
            ("Exercise Name", "First Test Failing"): {"passed": False, "output": "expects.be:'true? @[false]"}
        }
        
        output = build_output(expected_tests, parsed_results, None)
        
        self.assertEqual(output["status"], "fail")
        self.assertEqual(output["tests"][0]["status"], "fail")
        self.assertEqual(output["tests"][0]["message"], "expects.be:'true? @[false]")

    def test_report_error_for_empty_parsed_results(self):
        expected_tests = [{
            "suite": "Exercise Name",
            "name": "First Test",
            "code": "code1"
        }]
        parsed_results = {} 
        
        output = build_output(expected_tests, parsed_results, "An error was encountered running the tests.")
        
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["message"], "An error was encountered running the tests.")
        self.assertEqual(len(output["tests"]), 0)

    def test_report_failure_if_missing_subsequent_test(self):
        expected_tests = [
            {"suite": "Exercise Name", "name": "First Test Passing", "code": "code1"},
            {"suite": "Exercise Name", "name": "Second Test Failing", "code": "code2"},
            {"suite": "Exercise Name", "name": "Third Test Missing", "code": "code3"}
        ]
        parsed_results = {
            ("Exercise Name", "First Test Passing"): {"passed": True, "output": None},
            ("Exercise Name", "Second Test Failing"): {"passed": False, "output": "code2"},
        }
        
        output = build_output(expected_tests, parsed_results, None)
        
        self.assertEqual(output["tests"][0]["status"], "pass")
        self.assertEqual(output["tests"][1]["status"], "fail")
        self.assertEqual(output["tests"][2]["status"], "error") 
        self.assertEqual(output["tests"][2]["message"], "An error was encountered parsing this test. Please open a thread on the Exercism forums with the test that failed and your code please.") 


if __name__ == "__main__":
    unittest.main()
