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

# Create the output directory if it doesn't exist
mkdir -p "${output_dir}"

echo "${slug}: testing..."

tmp_dir=$(mktemp -d -t "exercism-verify-${slug}-XXXXX")

trap 'rm -rf "$tmp_dir"' EXIT
cp -r "${solution_dir}/." "${tmp_dir}"
cd "${tmp_dir}"

jq -r '.files.test[]' .meta/config.json | while read -r test_file; do
    sed -i 's/test.skip/test/g' "${test_file}"
done

test_output=$(arturo tester.art 2>&1)

# Write the results.json file based on the exit code of the command that was 
# just executed that tested the implementation file
if [ $? -eq 0 ]; then
    jq -n '{version: 1, status: "pass"}' > ${results_file}
else
    jq -n --arg output "${test_output}" '{version: 1, status: "fail", message: $output}' > ${results_file}
fi

echo "${slug}: done"
