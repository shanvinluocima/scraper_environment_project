import difflib
import os

# Define the two files to compare
file1 = 'scraper_environment_project/data/html/reafie.html'
file2 = 'scraper_environment_project/data/html/RAMHHS_20250625_102350.html'
output_diff="scraper_environment_project/data/diff_output.txt"

# Read the files
with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='latin-1') as f2:
    file1_lines = f1.readlines()
    file2_lines = f2.readlines()

# Generate the diff
diff = difflib.unified_diff(
    file1_lines, file2_lines,
    fromfile=file1,
    tofile=file2,
    lineterm=''
)
with open(output_diff, 'w', encoding='utf-8') as out:
    out.write("\n".join(diff))

# Print the results
print("\n".join(diff))
