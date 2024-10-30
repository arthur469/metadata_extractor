import magic
import os
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_mime_type(file_path):
    """
    Get MIME type for a file or all files in a directory.
    
    Args:
        file_path (str): Path to file or directory to analyze
        
    Returns:
        str|list|None: MIME type string for a file, list of MIME types for a directory,
                      or None if an error occurs
    """
    if not os.path.exists(file_path):
        logger.error(f"The specified path does not exist: {file_path}")
        return None

    try:
        if os.path.isdir(file_path):
            mime_types = []
            for root_dir, _, filenames in os.walk(file_path):
                for filename in filenames:
                    full_file_path = os.path.join(root_dir, filename)
                    try:
                        mime_type = magic.from_file(full_file_path, mime=True)
                        mime_types.append(mime_type)
                    except Exception as e:
                        logger.error(f"Error determining the file type of '{full_file_path}': {e}")
            return mime_types
        
        return magic.from_file(file_path, mime=True)
        
    except Exception as e:
        logger.error(f"Error determining the file type: {e}")
        return None

def save_mime_type_to_json(source_path, output_file_path):
    """
    Save MIME type information to a JSON file.
    
    Args:
        source_path (str): Path to file or directory to analyze
        output_file_path (str): Path where JSON output will be saved
    """
    mime_type_results = get_mime_type(source_path)
    if mime_type_results is None:
        return
        
    if os.path.isdir(source_path):
        mime_type_mapping = {os.path.join(root_dir, filename): mime_type 
                      for root_dir, _, filenames in os.walk(source_path) 
                      for filename, mime_type in zip(filenames, mime_type_results)}
    else:
        mime_type_mapping = {source_path: mime_type_results}
    
    try:
        with open(output_file_path, 'w') as json_file:
            json.dump(mime_type_mapping, json_file, indent=4)
        logger.info(f"Results saved to {output_file_path}")
    except Exception as e:
        logger.error(f"Error saving results to JSON file: {e}")

if __name__ == '__main__':
    current_dir = os.getcwd()
    temp_directory = os.path.join(current_dir, 'temp')
    input_directory = os.path.join(current_dir, 'files')
    output_json_file = os.path.join(temp_directory, 'mime.json')
    save_mime_type_to_json(input_directory, output_json_file)
