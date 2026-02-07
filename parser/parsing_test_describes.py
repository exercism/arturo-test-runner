import pyparsing
import textwrap

import parsing_common


describe_keyword = pyparsing.Keyword("describe")
it_keyword = pyparsing.Literal("it.skip") | pyparsing.Keyword("it")

# 'describe' block: describe "Name" [ content ] 
describe_block = describe_keyword + parsing_common.string_value("name") + parsing_common.regular_block("content")

# 'it' block: it "Name" [ code ] (or it.skip)
test_block = it_keyword("type") + parsing_common.string_value("name") + parsing_common.regular_block("code")


item_grammar = describe_block | test_block


def extract_tests(text: str, current_suite: str) -> list[dict[str, object]]:
    """Recursively extract test cases from the contents of a test file."""
    tests = []
    
    for match, start, end in item_grammar.scan_string(text):
        if "content" in match: # Describe block
            suite_name = match["name"]
            content = match["content"]
            
            # Recurse into the describe block, passing it as the new suite
            nested_tests = extract_tests(content, suite_name)
            tests.extend(nested_tests)
        
        elif "code" in match: # Test block
            raw_code = match["code"]
            stripped_code = raw_code.strip("\n") 
            dedented_code = textwrap.dedent(stripped_code).strip()
            
            tests.append({
                "name": match["name"],
                "code": dedented_code,
                "suite": current_suite
            })
            
    return tests


def parse_source_file(source_text: str) -> list[dict[str, object]]:
    """Build a list of test cases from the contents of a test file."""

    return extract_tests(source_text, None)
