import pyparsing

from parsing_common import (
    regular_block, array_block, string_value, bool_value, key,
    search_first, search_all
)

# specs: [ content ]
specs_block = key("specs:") + regular_block("content")

# dictionary #[ key: value ]
dictionary = array_block("content")

# properties key: value
description_property = key("description:") + string_value("value")
tests_property = key("tests:") + regular_block("value")
assertions_property = key("assertions:") + regular_block("value")

# assertion [ "code" boolean ]
assertion_element = pyparsing.Group(pyparsing.Suppress("[") + string_value("code") + bool_value("value") + pyparsing.Suppress("]"))


def parse_test_results(text: str) -> dict[tuple[str, str], dict[str, object]]:
    results = {}
    
    specs_found = search_first(specs_block, text)
    if not specs_found:
        return {}
    
    specs = specs_found["content"]
    suites = search_all(dictionary, specs)

    for suite in suites:
        suite_content = suite["content"]
        
        name_found = search_first(description_property, suite_content)
        if not name_found:
            continue
        suite_name = name_found["value"].strip()
        
        tests_found = search_first(tests_property, suite_content)
        if not tests_found:
            continue
        tests_array = tests_found["value"]
        
        for test in search_all(dictionary, tests_array):
            test_content = test["content"]
            
            test_name_found = search_first(description_property, test_content)
            if not test_name_found:
                continue
            test_name = test_name_found["value"].strip()
            
            assertions_found = search_first(assertions_property, test_content)
            if not assertions_found:
                continue
            assertions_block = assertions_found["value"]
            
            assertion_found = search_first(assertion_element, assertions_block)       
            if not assertion_found:
                continue     
            assertion = assertion_found[0]
            passed = assertion["value"]
            output = assertion["code"].strip()
            
            results[(suite_name, test_name)] = {
                "passed": passed,
                "output": output
            }
            
    return results
