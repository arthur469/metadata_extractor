from process import process_files_and_save_to_json
from mime_type import save_mime_type_to_json
import os
import datetime

def main():
    save_mime_type_to_json(folder_to_process, json_input_path)
    process_files_and_save_to_json(json_input_path, output_json_path)

if __name__ == '__main__':
     # Exemple d'utilisation
    this_dir = os.getcwd()
    temp_dir = os.path.join(this_dir, 'temp')

    folder_to_process = os.path.join(this_dir, 'files')
    json_input_path = os.path.join(temp_dir, 'mime.json')
    output_json_path = os.path.join(this_dir, "results", f"result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    main()