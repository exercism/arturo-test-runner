import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import parser


class TestResultsParser(unittest.TestCase):
    def test_report_single_test_success(self):
        expected_tests = [{
            "suite": "Exercise Name",
            "name": "First Test Passing",
            "code": "expects.be:'true? @[true]"
        }]
        parsed_results = {("Exercise Name", "First Test Passing"): {"passed": True, "output": None}}
        
        got = parser.build_output(expected_tests, parsed_results, None)
        want = {
            "version": 2,
            "status": "pass",
            "tests": [
                {
                    "name": "First Test Passing",
                    "status": "pass",
                    "test_code": "expects.be:'true? @[true]",
                    "message": None
                }
            ]
        }
        self.assertEqual(got, want)

    def test_report_failure_if_a_test_fails(self):
        expected_tests = [{
            "suite": "Exercise Name",
            "name": "First Test Failing",
            "code": "expects.be:'true? @[false]"
        }]
        parsed_results = {
            ("Exercise Name", "First Test Failing"): {"passed": False, "output": "expects.be:'true? @[false]"}
        }
        
        got = parser.build_output(expected_tests, parsed_results, None)
        want = {
            "version": 2,
            "status": "fail",
            "tests": [
                {
                    "name": "First Test Failing",
                    "status": "fail",
                    "test_code": "expects.be:'true? @[false]",
                    "message": "expects.be:'true? @[false]"
                }
            ]
        }
        self.assertEqual(got, want)

    def test_report_error_for_empty_parsed_results(self):
        expected_tests = [{
            "suite": "Exercise Name",
            "name": "First Test",
            "code": "code1"
        }]
        parsed_results = {} 
        
        got = parser.build_output(expected_tests, parsed_results, "An error was encountered running the tests.")
        want = {
            "version": 2,
            "status": "error",
            "message": "An error was encountered running the tests.",
            "tests": []
        }
        self.assertEqual(got, want)

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
        
        got = parser.build_output(expected_tests, parsed_results, None)
        want = {
            "version": 2,
            "status": "fail",
            "tests": [
                {
                    "name": "First Test Passing",
                    "status": "pass",
                    "test_code": "code1",
                    "message": None
                },
                {
                    "name": "Second Test Failing",
                    "status": "fail",
                    "test_code": "code2",
                    "message": "code2"
                },
                {
                    "name": "Third Test Missing",
                    "status": "error",
                    "test_code": "code3",
                    "message": "An error was encountered parsing this test. Please open a thread on the Exercism forums with the test that failed and your code please."
                }
            ]
        }
        self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()
