import os
import sys
import unittest

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
        got = parsing_test_describes.parse_source_file(source)
        want = [
            {
                "suite": "Example Suite",
                "name": "test 1",
                "code": "expects.be:'true? @[returnsFalse]"
            },
            {
                "suite": "Example Suite",
                "name": "test 2",
                "code": "expects.be:'false? @[returnsTrue]"
            }
        ]
        self.assertEqual(got, want)

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
        got = parsing_test_describes.parse_source_file(source)
        want = [
            {
                "suite": "Multiline",
                "name": "should dedent correctly",
                "code": """r: to :robot @[0 0 "north"]
do [r\\simulate "R"]
expects.be:'equal? @[
    [0 0 "east"]
    @[r\\x r\\y r\\direction]
]"""
            }
        ]
        self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()
