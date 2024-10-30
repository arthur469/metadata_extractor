import json
import logging
from extract import *
import os
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_metadata_to_json(metadata_results, output_file):
    """
    Save extracted metadata to a JSON file.
    
    Args:
        metadata_results (dict): Dictionary containing file paths and their extracted metadata
        output_file (str): Path to the JSON file where results will be saved
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(metadata_results, json_file, indent=4, ensure_ascii=False)
        logger.info(f"Metadata saved to file {output_file}")
    except Exception as e:
        logger.error(f"Error saving metadata to JSON file: {e}")

def process_file_metadata(file_path, mime_type):
    """
    Process file metadata based on MIME type or file extension.
    
    Args:
        file_path (str): Path to the file to process
        mime_type (str): MIME type of the file
        
    Returns:
        dict: Extracted metadata or error message if file type not supported
    """
    try:
        mime_type_extractors = {
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': extract_docx_metadata,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': extract_excel_metadata,
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': extract_ppt_metadata,
            'application/pdf': extract_pdf_full_metadata,
            'image/png': extract_png_metadata,
            'image/jpeg': extract_jpeg_metadata, 
            'image/tiff': extract_tiff_metadata,
            'image/webp': extract_webp_metadata,
            'image/heic': extract_heic_metadata,
            'image/heif': extract_heic_metadata,
            'image/svg+xml': extract_svg_metadata,
        }

        extension_extractors = {
            '.docx': extract_docx_metadata,
            '.xlsx': extract_excel_metadata,
            '.pptx': extract_ppt_metadata,
            '.pdf': extract_pdf_metadata,
            '.png': extract_png_metadata,
            '.jpg': extract_jpeg_metadata,
            '.jpeg': extract_jpeg_metadata,
            '.tiff': extract_tiff_metadata,
            '.tif': extract_tiff_metadata,
            '.webp': extract_webp_metadata,
            '.heic': extract_heic_metadata,
            '.heif': extract_heic_metadata,
            '.svg': extract_svg_metadata,
            '.txt': extract_txt_metadata
        }

        if mime_type in mime_type_extractors:
            return mime_type_extractors[mime_type](file_path)
            
        if mime_type in ['application/vnd.oasis.opendocument.text', 
                        'application/vnd.oasis.opendocument.spreadsheet',
                        'application/vnd.oasis.opendocument.presentation']:
            return extract_odf_metadata(file_path)

        if mime_type == 'text/plain':
            _, file_extension = os.path.splitext(file_path.lower())
            if file_extension in extension_extractors:
                return extension_extractors[file_extension](file_path)
            return f"Extension {file_extension} not supported for MIME type {mime_type}"

        return f"MIME type {mime_type} not supported"

    except Exception as e:
        logger.error(f"Error processing '{file_path}': {e}")
        return None

def process_files_and_save_to_json(input_json_path, output_json_path):
    """
    Read JSON file containing file paths and MIME types, process each file and save results.
    
    Args:
        input_json_path (str): Path to input JSON file containing file paths and MIME types
        output_json_path (str): Path where output JSON with metadata will be saved
    """
    def convert_datetime_to_string(data):
        """Convert datetime objects to ISO format strings in nested data structures"""
        if isinstance(data, dict):
            return {k: convert_datetime_to_string(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_datetime_to_string(v) for v in data]
        elif isinstance(data, datetime.datetime):
            return data.isoformat()
        return data

    try:
        with open(input_json_path, 'r') as json_file:
            file_mime_mapping = json.load(json_file)

        metadata_results = {}
        for file_path, mime_type in file_mime_mapping.items():
            logger.info(f"Processing file: {file_path} with MIME type: {mime_type}")
            metadata = process_file_metadata(file_path, mime_type)
            if metadata:
                metadata_results[file_path] = convert_datetime_to_string(metadata)

        save_metadata_to_json(metadata_results, output_json_path)

    except Exception as e:
        logger.error(f"Error processing files and saving results: {e}")

if __name__ == '__main__':
    input_json_path = os.path.join(os.getcwd(), 'mime.json')
    output_json_path = os.path.join(os.getcwd(), "results", f"result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    process_files_and_save_to_json(input_json_path, output_json_path)
