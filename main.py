import json
import os

from AgenticManager import AgenticManager
from FileExtracter import FileExtracter


DEMO_INPUT_DIR = "demo_input"  # Change this to your desired input directory


def main():
    file_manager = FileExtracter()
    agent_manager = AgenticManager()

    directory = os.path.abspath(DEMO_INPUT_DIR)

    print(f"\nSelected directory: {directory}")

    if not os.path.isdir(directory):
        print("That directory does not exist.")
        return

    files = file_manager.get_files(directory)
    print(f"Found {len(files)} supported file(s).")

    if not files:
        return

    print("\nFiles discovered:")
    for file_path in files:
        print(f"- {os.path.abspath(file_path)}")

    metadata_dir = os.path.join(directory, "_metadata")
    os.makedirs(metadata_dir, exist_ok=True)

    processed_files = []

    for file_path in files:
        print(f"\nProcessing: {file_path}")

        text = file_manager.extract_text(file_path)
        if not text.strip():
            print("Skipping file because no text could be extracted.")
            continue

        print("Extracting metadata with AI...")
        metadata = agent_manager.json_creator(text)

        metadata_file_name = f"{os.path.splitext(os.path.basename(file_path))[0]}_metadata.json"
        metadata_path = os.path.join(metadata_dir, metadata_file_name)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        destination_folder = agent_manager.determine_destination(metadata)
        print(f"Destination folder: {os.path.abspath(destination_folder)}")

        new_file_path = agent_manager.place_file(file_path, metadata_path)
        print(f"Moved file to: {os.path.abspath(new_file_path)}")

        processed_files.append((file_path, new_file_path))

    print("\nProcessing complete.")
    print("Final file locations:")
    for original_path, new_path in processed_files:
        print(f"- {os.path.abspath(original_path)} -> {os.path.abspath(new_path)}")


if __name__ == "__main__":
    main()
