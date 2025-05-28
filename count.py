import json
from collections import Counter


def count_lsp_occurrences(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Extract LSP values
    lsp_list = [entry['LSP'] for entry in data if 'LSP' in entry]

    # Count each LSP using Counter
    lsp_counter = Counter(lsp_list)

    print(f"Total unique LSPs: {len(lsp_counter)}")
    print("LSP counts:")
    for lsp, count in lsp_counter.items():
        print(f"- {lsp}: {count}")

    return lsp_counter


# File path
json_path = r"D:\internship\data\PODLinks.json"

# Run the function
count_lsp_occurrences(json_path)
