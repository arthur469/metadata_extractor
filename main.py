from process import process_files_and_save_to_json
from mime_type import save_mime_type_to_json
import os
import datetime

def main():
    """
    Main function that processes files in a directory to extract metadata.
    
    First gets MIME types for all files in the input directory and saves them to a JSON file.
    Then extracts metadata from each file based on its MIME type and saves results to another JSON file.
    """
    save_mime_type_to_json(input_directory, mime_types_json_path)
    process_files_and_save_to_json(mime_types_json_path, metadata_output_path)

if __name__ == '__main__':
    current_directory = os.getcwd()
    temp_directory = os.path.join(current_directory, 'temp')
    input_directory = os.path.join(current_directory, 'files')
    mime_types_json_path = os.path.join(temp_directory, 'mime.json')
    metadata_output_path = os.path.join(
        current_directory,
        "results",
        f"result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    main()