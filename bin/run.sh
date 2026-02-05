#!/usr/bin/env sh

# Synopsis:
# Run the test runner on a solution.

# Arguments:
# $1: exercise slug
# $2: path to solution folder
# $3: path to output directory

# Output:
# Writes the test results to a results.json file in the passed-in output directory.
# The test results are formatted according to the specifications at https://github.com/exercism/docs/blob/main/building/tooling/test-runners/interface.md

# Example:
# ./bin/run.sh two-fer path/to/solution/folder/ path/to/output/directory/

# If any required arguments is missing, print the usage and exit
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "usage: ./bin/run.sh exercise-slug path/to/solution/folder/ path/to/output/directory/"
    exit 1
fi

slug="$1"
solution_dir=$(realpath "${2%/}")
output_dir=$(realpath "${3%/}")
results_file="${output_dir}/results.json"
bin_dir=$(realpath "${0%/*}")
parser_dir="${bin_dir}/../parser"

mkdir -p "${output_dir}"

echo "${slug}: testing..."

tmp_dir=$(mktemp -d -t "exercism-verify-${slug}-XXXXX")

trap 'rm -rf "$tmp_dir"' EXIT
cp -r "${solution_dir}/." "${tmp_dir}"
cp "${parser_dir}/"*.py "${tmp_dir}/"
cd "${tmp_dir}"

test_file="tests/test-${slug}.art"
sed -i '' -E 's/(test|it).skip/\1/g' "${test_file}"

test_output=$(arturo tester.art 2>&1)
test_filename=$(basename "${test_file}")
result_art_file=".unitt/tests/${test_filename}"

python3 parser.py "${test_file}" "${result_art_file}" "${test_output}"

if [ -f results.json ]; then
    cp results.json "${output_dir}/"
else
    echo "${slug}: Error in parsing results."
    exit 1
fi
