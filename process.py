import json
import logging
from extract import extract_docx_metadata, extract_excel_metadata, extract_ppt_metadata, extract_odf_metadata, extract_pdf_metadata, extract_png_metadata, extract_jpeg_metadata
import os
import datetime

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fonction pour enregistrer les métadonnées extraites dans un fichier JSON
def save_metadata_to_json(metadata_results, output_file):
    """
    Enregistre les métadonnées extraites dans un fichier JSON.
    
    Args:
        metadata_results (dict): Dictionnaire contenant les chemins de fichiers et leurs métadonnées extraites.
        output_file (str): Chemin du fichier JSON où les résultats seront sauvegardés.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(metadata_results, json_file, indent=4, ensure_ascii=False)
        
        logger.info(f"Les métadonnées ont été sauvegardées dans le fichier {output_file}")

    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des métadonnées dans le fichier JSON : {e}")

# Fonction principale pour traiter chaque fichier en fonction du MIME type
def process_file_metadata(file_path, mime_type):
    try:
        if mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # Fichier Word (.docx)
            metadata = extract_docx_metadata(file_path)
        elif mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            # Fichier Excel (.xlsx)
            metadata = extract_excel_metadata(file_path)
        elif mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            # Fichier PowerPoint (.pptx)
            metadata = extract_ppt_metadata(file_path)
        elif mime_type in ['application/vnd.oasis.opendocument.text', 'application/vnd.oasis.opendocument.spreadsheet', 'application/vnd.oasis.opendocument.presentation']:
            # Fichiers OpenOffice (.odt, .ods, .odp)
            metadata = extract_odf_metadata(file_path)
        elif mime_type == 'application/pdf':
            # Fichier PDF
            metadata = extract_pdf_metadata(file_path)
        elif mime_type.startswith('image/png'):
            # Fichier image (JPEG, PNG, etc.)
            metadata = extract_png_metadata(file_path)
        elif mime_type.startswith('image/jpeg'):
            # Fichier image (JPEG, PNG, etc.)
            metadata = extract_jpeg_metadata(file_path)
        else:
            metadata = f"MIME type {mime_type} non pris en charge."

        return metadata

    except Exception as e:
        logger.error(f"Erreur lors du traitement de '{file_path}': {e}")
        return None

# Fonction pour lire le fichier JSON, traiter chaque fichier et sauvegarder les résultats
def process_files_and_save_to_json(json_path, output_json_path):
    def convert_datetime_to_string(data):
        if isinstance(data, dict):
            return {k: convert_datetime_to_string(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_datetime_to_string(v) for v in data]
        elif isinstance(data, datetime.datetime):
            return data.isoformat()
        else:
            return data

    try:
        with open(json_path, 'r') as json_file:
            file_mime_map = json.load(json_file)

        # Dictionnaire pour stocker les résultats des métadonnées
        metadata_results = {}

        # Parcourir chaque fichier dans le fichier JSON
        for file_path, mime_type in file_mime_map.items():
            logger.info(f"Traitement du fichier: {file_path} avec MIME type: {mime_type}")
            metadata = process_file_metadata(file_path, mime_type)

            if metadata:
                metadata = convert_datetime_to_string(metadata)
                metadata_results[file_path] = metadata

        # Sauvegarder les résultats dans le fichier JSON
        save_metadata_to_json(metadata_results, output_json_path)

    except Exception as e:
        logger.error(f"Erreur lors du traitement des fichiers et de la sauvegarde des résultats : {e}")


if __name__ == '__main__':
    # Exemple d'utilisation
    json_input_path = os.path.join(os.getcwd(), 'mime.json')
    output_json_path = os.path.join(os.getcwd(), "results", f"result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    # Appel de la fonction pour traiter les fichiers et sauvegarder les métadonnées
    process_files_and_save_to_json(json_input_path, output_json_path)
