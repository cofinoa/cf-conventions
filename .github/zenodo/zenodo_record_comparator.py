#!/usr/bin/env python3
"""
Zenodo Record Comparator

This script compares a local Zenodo record JSON file with a remote Zenodo record fetched from the Zenodo API.
It highlights any differences, with options to exclude specific fields or to include only the sections and items in the local file.

Usage:
  zenodo_record_comparator.py <local_file> <record_id> [--exclude <paths>] [--local-only]
  zenodo_record_comparator.py (-h | --help)

Options:
  <local_file>           Path to the local Zenodo JSON file.
  <record_id>            The Zenodo record ID to fetch.
  --exclude <paths>      Comma-separated list of JSON paths to exclude (e.g., root['metadata']['publication_date'],root['files'][*]['checksum']).
  --local-only           Include only sections and items that exist in the local file for the diff.
  -h --help              Show this help message.

Examples:
  python zenodo_record_comparator.py zenodo.json 123456
  python zenodo_record_comparator.py zenodo.json 123456 --exclude root['metadata']['publication_date'],root['files'][*]['checksum'] --local-only
"""

import json
import requests
from deepdiff import DeepDiff
from docopt import docopt

# Define the Zenodo API URL for record retrieval
ZENODO_API_BASE = "https://zenodo.org/api/records"

def fetch_remote_record(record_id):
  """
  Fetch the JSON metadata of a Zenodo record by its ID.
  """
  url = f"{ZENODO_API_BASE}/{record_id}"
  response = requests.get(url)
  if response.status_code == 200:
    return response.json()
  else:
    raise Exception(f"Failed to fetch record {record_id}: {response.status_code}")

def load_local_record(file_path):
  """
  Load the local Zenodo JSON metadata from a file.
  """
  with open(file_path, 'r') as file:
    return json.load(file)

def compare_records(local_file_path, record_id, exclude_paths=None, local_only=False):
  """
  Compare a local JSON record with a remote Zenodo record.

  Args:
    local_file_path (str): Path to the local Zenodo JSON file.
    record_id (str): Zenodo record ID to fetch.
    exclude_paths (list): List of JSON paths to exclude from the comparison.
    local_only (bool): If True, include only sections and items in the local file for the diff.

  Returns:
    dict: A dictionary of differences found.
  """
  # Load local JSON record
  local_record = load_local_record(local_file_path)

  # Fetch remote Zenodo record
  remote_record = fetch_remote_record(record_id)

  # Compare the two records with exclusions
  differences = DeepDiff(
    local_record,
    remote_record,
    ignore_order=True,
    exclude_paths=exclude_paths,
    view="tree" if local_only else "text"
  )
  return differences

def main():
  """
  Main function to handle CLI input and perform the comparison.
  """
  # Parse command-line arguments using DocOpt
  args = docopt(__doc__)

  local_file_path = args["<local_file>"]
  record_id = args["<record_id>"]
  exclude_paths_input = args.get("--exclude")
  local_only = args.get("--local-only")

  # Process exclude paths if provided
  exclude_paths = exclude_paths_input.split(",") if exclude_paths_input else []

  try:
    # Compare records
    print("Comparing records...")
    differences = compare_records(local_file_path, record_id, exclude_paths=exclude_paths, local_only=local_only)

    # Output results
    if differences:
      print("\nDifferences found between local and remote records:")
      print(json.dumps(differences, indent=2))
    else:
      print("\nNo differences found between local and remote records.")

  except Exception as e:
    print(f"\nAn error occurred: {e}")

# Allow the script to be used as both a CLI and an importable module
if __name__ == "__main__":
  main()
