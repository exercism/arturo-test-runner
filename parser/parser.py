import re
import sys
import json
from pathlib import Path

import parsing_test_describes
import parsing_test_results

def main():
    if len(sys.argv) < 2: 
        print("Usage: python parser.py <test-file.art> [result-file.art] [arturo-output]")
        return
    
    test_path = Path(sys.argv[1])
    
    try:
        with open(test_path, "r", encoding="utf-8") as f:
            test_text = f.read()
        test_definitions = parsing_test_describes.parse_source_file(test_text)
    except FileNotFoundError:
        print(f"ERROR: Source file {test_path} not found.", file=sys.stderr)
        sys.exit(1)

    result_path = Path(sys.argv[2])
    
    results_text = ""
    if result_path and result_path.exists():
        with open(result_path, "r", encoding="utf-8") as f:
            results_text = f.read()
    
    test_results = parsing_test_results.parse_test_results(results_text)
    
    # Capture passed-in Arturo terminal output if there's an error to report
    arturo_output = ""
    if len(sys.argv) >= 4:
        arturo_output = sys.argv[3]
    
    output = build_output(test_definitions, test_results, arturo_output)
    
    write_output(output)


def build_output(
    test_definitions: list[dict[str, object]], 
    test_results: dict, 
    arturo_output: str
) -> dict[str, object]:
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
            if not result["passed"]:
                update_test_as_failed(test_obj, result["output"], test_code)
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


def update_test_as_failed(test_obj: dict[str, object], assertion: str, test_code: str):
    test_obj["status"] = "fail"
    
    msg = assertion
    if not assertion.startswith("expects.be:") and test_code.startswith("expects.be:"):
        msg = f"expects.be:'{assertion}"  
    test_obj["message"] = normalize_output(msg)


def normalize_output(text: str) -> str:
    """
    Normalize and sanitize command line output.

    This sanitizes paths, standardizes terminal formatting, and fixes macOS exit codes.
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

    return text


def write_output(data: dict[str, object]):
    """Write the v2 test results dictionary to JSON."""
    output_file = Path("results.json")
    
    fallback_data = None
    try:
        json_data = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        output_file.write_text(json_data, encoding="utf-8")
    except (TypeError, ValueError) as e:
        # JSON serialization failure
        fallback_data = {
            "version": 2,
            "status": "error",
            "message": f"Internal error: Failed to serialize test results ({type(e).__name__}: {e})",
            "tests": []
        }
    except (OSError, IOError) as e:
        # File write failure
        fallback_data = {
            "version": 2,
            "status": "error",
            "message": f"Internal error: Failed to write results file ({type(e).__name__}: {e})",
            "tests": []
        }
    except Exception as e:
        fallback_data = {
            "version": 2,
            "status": "error",
            "message": f"Internal error: Unexpected failure ({type(e).__name__}: {e})",
            "tests": []
        }
    
    if fallback_data:
        try:
            json_data = json.dumps(fallback_data, indent=2, ensure_ascii=False) + "\n"
            output_file.write_text(json_data, encoding="utf-8")
        except Exception:
            # At this point, the shell script can handle the results.json file not being written
            sys.exit(1)

if __name__ == "__main__":
    main()
