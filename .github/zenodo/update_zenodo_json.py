import os
import json
import shutil
import hashlib

def calculate_md5(file_path):
    """Calculate MD5 checksum for a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def list_files_in_dir(dir_path):
    """List all PDF and HTML files in the directory and generate metadata."""
    files_metadata = []
    for file in os.listdir(dir_path):
        full_path = os.path.join(dir_path, file)
        if os.path.isfile(full_path) and (file.endswith(".pdf") or file.endswith(".html")):
            relative_path = os.path.relpath(full_path, dir_path)  # File relative to zenodo.json's directory
            size = os.path.getsize(full_path)
            checksum = calculate_md5(full_path)
            files_metadata.append({"filename": relative_path, "size": size, "checksum": f"md5:{checksum}"})
    return files_metadata

def update_zenodo_json(dir_path, template_path):
    """Update or create zenodo.json in the specified directory."""
    zenodo_json_path = os.path.join(dir_path, "zenodo.json")
    version = os.path.basename(dir_path)

    if not os.path.exists(zenodo_json_path):
        # If zenodo.json does not exist, copy from template
        shutil.copy(template_path, zenodo_json_path)

    # Load zenodo.json
    try:
        with open(zenodo_json_path, "r") as file:
            zenodo_data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON in {zenodo_json_path}: {e}")
        return

    # Update version
    zenodo_data["metadata"]["version"] = version

    # Update related_identifiers URLs
    if "related_identifiers" in zenodo_data["metadata"]:
        for identifier in zenodo_data["metadata"]["related_identifiers"]:
            if "identifier" in identifier and "cf-conventions" in identifier["identifier"]:
                identifier["identifier"] = identifier["identifier"].replace(
                    "cf-conventions-1.X", f"cf-conventions-{version}"
                ).replace(
                    "requirements-recommendations-1.X", f"requirements-recommendations-{version}"
                )

    # Update files section
    files_metadata = list_files_in_dir(dir_path)
    if not files_metadata:
        print(f"No PDF or HTML files found in {dir_path}, skipping files update.")
    zenodo_data["files"] = files_metadata

    # Save updated zenodo.json
    try:
        with open(zenodo_json_path, "w") as file:
            json.dump(zenodo_data, file, indent=4)
    except IOError as e:
        print(f"Error writing JSON to {zenodo_json_path}: {e}")
        return
    print(f"Updated zenodo.json in {dir_path}")

def process_directories_from_list(directories, template_path):
    """Process a list of directories."""
    for dir_path in directories:
        if os.path.exists(dir_path):
            print(f"Processing directory: {dir_path}")
            update_zenodo_json(dir_path, template_path)
        else:
            print(f"Directory {dir_path} does not exist, skipping.")

if __name__ == "__main__":
    # Example list of directories
    directories = [
        '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '1.10', '1.11',
    ]

    # Adjust base directory if needed
    base_directory = './publish'  # Adjust this as necessary
    directories = [os.path.join(base_directory, dir_name) for dir_name in directories]

    # Template path
    template_file = os.path.join(base_directory, "../../.zenodo.json")

    if not os.path.exists(template_file):
        print(f"Template file {template_file} does not exist. Ensure it is in the correct relative location.")
    else:
        process_directories_from_list(directories, template_file)
