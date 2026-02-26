import json
import operator
import pathlib
import re
import sys
import typing

import parsing_test_describes
import parsing_test_results


def build_output(
    test_definitions: list[dict[str, typing.Any]], 
    test_results: dict[str, typing.Any], 
    arturo_output: str
) -> dict[str, typing.Any]:
    """Construct the Exercism v2 JSON output from test definitions, test results, and Arturo output."""
    v2_tests = []
    run_status = "pass"
    
    if test_definitions and not test_results:
        return {
            "version": 2,
            "status": "error",
            "message": normalize_output(arturo_output), 
            "tests": []
        }

    for test in test_definitions:
        suite_name = test["suite"].strip() if test["suite"] else None
        test_name = test["name"].strip()
        test_code = test["code"]
        
        test_obj = {
            "name": test_name,
            "test_code": test_code,
            "status": "pass",
            "message": None
        }
        
        test_key = (suite_name, test_name)
        
        if test_key in test_results:
            result = test_results[test_key]
            passed, output = operator.itemgetter("passed", "output")(result)
            if not passed:
                test_obj["status"] = "fail"
                test_obj["message"] = format_assertion_message(output)
                if run_status != "error":
                    run_status = "fail"
        else:
            # fallback in case things couldn't be matched up for some reason
            test_obj["status"] = "error"
            test_obj["message"] = "An error was encountered parsing this test. Please open a thread on the Exercism forums with the test that failed and your code please."
            if run_status != "error":
                run_status = "fail"
        
        v2_tests.append(test_obj)

    return {
        "version": 2,
        "status": run_status,
        "tests": v2_tests
    }


def format_assertion_message(text: str) -> str:
    """Format a test's assertion result to match the assertion in the test code"""
    func, *args = text.strip().split(' ')
    if not args:
        return text
    return f"expects.be:'{func} @[{' '.join(args)}]"


def normalize_output(text: str) -> str:
    """
    Normalize and sanitize command line output.

    This sanitizes paths, standardizes terminal formatting, fixes macOS exit codes, and truncates to 65535 characters.
    """
    if not text:
        return text
        
    # Regex to sanitize absolute paths to a fixed placeholder
    text = re.sub(r"/[^ \n\"]+/\.arturo/", "~/.arturo/", text)
    
    # Normalize the error header line to fixed width since it can vary on the shell
    text = re.sub(r"╞.*? <script> ══", "╞════════════════════════════════════════════════════ <script> ══", text)
    
    # On macOS, a name error returns an exit code of 127 instead of 1.
    # Other tests are fine cross-platform.
    if sys.platform == "darwin" and "Name Error" in text and "code: 127" in text:
        text = text.replace("code: 127", "code: 1")

    return text[:65535]


def write_output(data: dict[str, typing.Any]) -> None:
    """Write the v2 test results dictionary to JSON."""
    output_file = pathlib.Path("results.json")
    
    # Generate JSON data
    try:
        json_data = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    except (TypeError, ValueError) as e:
        # JSON serialization failure
        json_data = {
            "version": 2,
            "status": "error",
            "message": f"Internal error: Failed to serialize test results ({type(e).__name__}: {e})",
            "tests": []
        }

    # Write data out. If it fails, bail and exit; we can't do anything more if file writing fails.
    try:
        output_file.write_text(json_data)
    except (OSError, IOError) as e:
        sys.exit(1)


def main():
    if len(sys.argv) < 2: 
        print("Usage: python parser.py <test-file.art> [result-file.art] [arturo-output]")
        sys.exit(2)
    
    test_path = pathlib.Path(sys.argv[1])
    if not test_path.exists():
        print(f"ERROR: Source file {test_path} not found.", file=sys.stderr)
        sys.exit(1)
    test_text = test_path.read_text()
    test_definitions = parsing_test_describes.parse_source_file(test_text)

    result_path = pathlib.Path(sys.argv[2])
    if not result_path.exists():
        print(f"ERROR: Result file {result_path} not found.", file=sys.stderr)
        sys.exit(1)
    results_text = result_path.read_text()
    test_results = parsing_test_results.parse_test_results(results_text)
    
    # Capture passed-in Arturo terminal output if there's an error to report
    arturo_output = ""
    if len(sys.argv) >= 4:
        arturo_output = sys.argv[3]
    
    output = build_output(test_definitions, test_results, arturo_output)    
    write_output(output)


if __name__ == "__main__":
    main()
