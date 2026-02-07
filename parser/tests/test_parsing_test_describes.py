import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import parsing_test_describes

class TestParsingDescribes(unittest.TestCase):
    def test_parse_describe_simple_tests(self):
        source = """
describe "Example Suite" [
    it "test 1" [
        expects.be:'true? @[returnsFalse]
    ]

    it.skip "test 2" [
        expects.be:'false? @[returnsTrue]
    ]
]
"""
        result = parsing_test_describes.parse_source_file(source)

        self.assertEqual(len(result), 2)
        
        self.assertEqual(result[0]["suite"], "Example Suite")
        self.assertEqual(result[0]["name"], "test 1")
        self.assertEqual(result[0]["code"], "expects.be:'true? @[returnsFalse]")
        
        self.assertEqual(result[1]["suite"], "Example Suite")
        self.assertEqual(result[1]["name"], "test 2")
        self.assertEqual(result[1]["code"], "expects.be:'false? @[returnsTrue]")

    def test_parse_describe_multiline_test_code(self):
        source = """
describe "Multiline" [
    it "should dedent correctly" [
        r: to :robot @[0 0 "north"]
        do [r\\simulate "R"]
        expects.be:'equal? @[
            [0 0 "east"]
            @[r\\x r\\y r\\direction]
        ]
    ]
]
"""
        result = parsing_test_describes.parse_source_file(source)
        
        self.assertEqual(len(result), 1)
        code = result[0]["code"]
        expected_code = """r: to :robot @[0 0 "north"]
do [r\\simulate "R"]
expects.be:'equal? @[
    [0 0 "east"]
    @[r\\x r\\y r\\direction]
]"""
        self.assertEqual(code, expected_code)

if __name__ == "__main__":
    unittest.main()
