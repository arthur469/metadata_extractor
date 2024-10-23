import magic
import os
import logging
import json

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_mime_type(path):
    if not os.path.exists(path):
        logger.error(f"The specified path does not exist: {path}")
        return None

    try:
        if os.path.isdir(path):
            results = []
            for root, _, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(root, file)
                    try:
                        file_type = magic.from_file(full_path, mime=True)
                        results.append(file_type)
                    except Exception as e:
                        logger.error(f"Error determining the file type of '{full_path}': {e}")
            return results
        else:
            # Using the magic library to detect the file type
            file_type = magic.from_file(path, mime=True)
            return file_type
    except Exception as e:
        logger.error(f"Error determining the file type: {e}")
        return None

def save_mime_type_to_json(path, output_file):
    mime_type_result = get_mime_type(path)
    if os.path.isdir(path):
        result_dict = {os.path.join(root, file): mime for root, _, files in os.walk(path) for file, mime in zip(files, mime_type_result)}
    else:
        result_dict = {path: mime_type_result}
    
    try:
        with open(output_file, 'w') as json_file:
            json.dump(result_dict, json_file, indent=4)
        logger.info(f"The results have been saved to the file {output_file}")
    except Exception as e:
        logger.error(f"Error saving the results to the JSON file: {e}")

# Example 
if __name__ == '__main__':
    this_dir = os.getcwd()
    temp_dir = os.path.join(this_dir, 'temp')

    folder_to_process = os.path.join(this_dir, 'files')
    output_json_path = os.path.join(temp_dir, 'mime.json')

    save_mime_type_to_json(folder_to_process, output_json_path)
