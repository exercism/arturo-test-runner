import typing

import pyparsing

import parsing_common

# specs: [ content ]
specs_block = parsing_common.key("specs:") + parsing_common.regular_block("content")

# dictionary #[ key: value ]
dictionary = parsing_common.array_block("content")

# properties key: value
description_property = parsing_common.key("description:") + parsing_common.multiline_string_or_block("value")
tests_property = parsing_common.key("tests:") + parsing_common.regular_block("value")
assertions_property = parsing_common.key("assertions:") + parsing_common.regular_block("value")

# assertion [ "code" boolean ]
assertion_element = pyparsing.Group(
    pyparsing.Suppress(pyparsing.oneOf("[ {"))
    + (parsing_common.multiline_string_or_block | pyparsing.SkipTo(parsing_common.bool_value).set_parse_action(lambda t: t[0].strip()))("code")
    + parsing_common.bool_value("value")
    + pyparsing.Suppress(pyparsing.oneOf("] }"))
)


def parse_test_results(text: str) -> dict[tuple[str, str], dict[str, typing.Any]]:
    """Parse the test results from the given text."""
    results = {}
    
    specs_found = parsing_common.search_first(specs_block, text)
    if not specs_found:
        return {}
    
    specs = specs_found["content"]
    suites = parsing_common.search_all(dictionary, specs)

    for suite in suites:
        suite_content = suite["content"]
        
        name_found = parsing_common.search_first(description_property, suite_content)
        if not name_found:
            continue
        suite_name = name_found["value"]
        if not isinstance(suite_name, str):
            suite_name = suite_name[0]
        
        tests_found = parsing_common.search_first(tests_property, suite_content)
        if not tests_found:
            continue
        tests_array = tests_found["value"]
        
        for test in parsing_common.search_all(dictionary, tests_array):
            test_content = test["content"]
            
            test_name_found = parsing_common.search_first(description_property, test_content)
            if not test_name_found:
                continue
            test_name = test_name_found["value"]
            if not isinstance(test_name, str):
                test_name = test_name[0]
            
            assertions_found = parsing_common.search_first(assertions_property, test_content)
            if not assertions_found:
                continue
            assertions_block = assertions_found["value"]
            
            assertion_found = parsing_common.search_first(assertion_element, assertions_block)       
            if not assertion_found:
                continue     
            assertion = assertion_found[0]
            passed = assertion["value"]
            output = assertion["code"]
            if not isinstance(output, str):
                output = output[0]
            
            results[(suite_name, test_name)] = {
                "passed": passed,
                "output": output
            }
            
    return results
