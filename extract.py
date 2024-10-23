import pymupdf 
from PIL import Image
import exifread
import logging
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from odf.opendocument import load
import os
import struct

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_pdf_metadata(file_path):
    try:
        doc = pymupdf.open(file_path)

        # Extract standard metadata
        standard_metadata = doc.metadata
        
        # Log standard metadata
        logger.info("Metadata extracted successfully")

        # Return metadata as a dictionary (JSON-like structure)
        return {
            "Standard Metadata": standard_metadata
        }

    except Exception as e:
        logger.error(f"Error extracting PDF metadata: {e}")
        return None

def extract_pdf_xref(file_path):
    try:
        doc = pymupdf.open(file_path)
        xref_metadata = {}

        # Extract low-level metadata from the XREF table
        logger.info("Extracting XREF:")
        for xref in range(1, doc.xref_length()):  # Iterate through all objects in the XREF table
            obj_type = doc.xref_object(xref, compressed=False)
            xref_metadata[f"XREF {xref}"] = obj_type

        return {
            "XREF Metadata": xref_metadata
        }

    except Exception as e:
        logger.error(f"Error extracting PDF XREF: {e}")
        return None

def extract_pdf_full_metadata(file_path):
    try:
        # Extract both standard metadata and XREF metadata
        metadata = extract_pdf_metadata(file_path)
        xref_data = extract_pdf_xref(file_path)

        # Combine both sets of metadata into one dictionary
        full_metadata = {}
        if metadata:
            full_metadata.update(metadata)
        if xref_data:
            full_metadata.update(xref_data)

        return full_metadata

    except Exception as e:
        logger.error(f"Error extracting full PDF metadata: {e}")
        return None

def extract_jpeg_metadata(file_path):
    metadata = {}
    try:
        # Extraction des informations de base avec Pillow
        with Image.open(file_path) as img:
            width, height = img.size
            format_image = img.format
            mode = img.mode
            info = img.info  # Contient des informations additionnelles, comme le profil ICC, JFIF, etc.
            
            # Ajout des informations de base
            metadata.update({
                'File Name': os.path.basename(file_path),
                'File Size': f"{os.path.getsize(file_path) / 1024:.0f} kB",  # Convertir la taille en Ko
                'Format': format_image,
                'Mode': mode,
                'Image Width': width,
                'Image Height': height,
                'Image Size': f"{width}x{height}",
                'Megapixels': round((width * height) / 1_000_000, 1),
            })

            # Vérification des informations spécifiques JFIF (Joint Photographic Experts Group)
            if 'jfif_version' in info:
                metadata['JFIF Version'] = f"{info['jfif_version'][0]}.{info['jfif_version'][1]}"
            else:
                metadata['JFIF Version'] = 'Unknown'

            # Résolution de l'image (unités et valeurs)
            if 'dpi' in info:
                metadata['X Resolution'] = info['dpi'][0]
                metadata['Y Resolution'] = info['dpi'][1]
                metadata['Resolution Unit'] = 'inches'
            else:
                metadata['X Resolution'] = 'Unknown'
                metadata['Y Resolution'] = 'Unknown'
                metadata['Resolution Unit'] = 'Unknown'

            # Ajout du profil ICC (si disponible)
            if 'icc_profile' in info:
                metadata['ICC Profile'] = 'Present'
            else:
                metadata['ICC Profile'] = 'Absent'

            # Lecture des informations de compression
            if 'progression' in info:
                metadata['Encoding Process'] = 'Progressive JPEG, Huffman coding'
            else:
                metadata['Encoding Process'] = 'Baseline DCT, Huffman coding'

            # Bits par échantillon
            metadata['Bits Per Sample'] = 8  # Les JPEG utilisent typiquement 8 bits par composant

            # Composants de couleur (RGB = 3, CMYK = 4, etc.)
            metadata['Color Components'] = len(img.getbands())

            # YCbCr Subsampling (extrait du JFIF ou supposé être le standard 4:2:0)
            if 'subsampling' in info:
                subsampling = info['subsampling']
                if subsampling == (2, 2):
                    metadata['YCbCr Subsampling'] = 'YCbCr4:2:0 (2 2)'
                elif subsampling == (2, 1):
                    metadata['YCbCr Subsampling'] = 'YCbCr4:2:2 (2 1)'
                else:
                    metadata['YCbCr Subsampling'] = 'YCbCr4:4:4 (1 1)'
            else:
                metadata['YCbCr Subsampling'] = 'Unknown'

        # Lecture des métadonnées EXIF
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f)

        exif_metadata = {tag: str(tags[tag]) for tag in tags.keys()}
        metadata['EXIF Metadata'] = exif_metadata

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des métadonnées JPEG pour '{file_path}': {e}")
    
    return metadata

def extract_png_metadata(file_path):
    metadata = {}
    try:
        with open(file_path, 'rb') as f:
            # Lecture du fichier binaire PNG
            header = f.read(8)  # Signature PNG
            if header != b'\x89PNG\r\n\x1a\n':
                raise ValueError("Ce fichier n'est pas un fichier PNG valide.")

            metadata['PNG Signature'] = header.hex().upper()

            # Boucle sur les chunks PNG
            while True:
                chunk_header = f.read(8)  # 4 octets pour la longueur et 4 octets pour le type de chunk
                if len(chunk_header) < 8:
                    break

                length, chunk_type = struct.unpack('>I4s', chunk_header)
                chunk_data = f.read(length)
                f.read(4)  # CRC (ignorer)

                # Extraction des métadonnées dans le chunk IHDR
                if chunk_type == b'IHDR':
                    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack('>IIBBBBB', chunk_data)
                    metadata.update({
                        'Width': width,
                        'Height': height,
                        'Bit Depth': bit_depth,
                        'Color Type': color_type,
                        'Compression': compression,
                        'Filter': filter_method,
                        'Interlace': interlace
                    })
                elif chunk_type == b'pHYs':
                    ppux, ppuy, unit = struct.unpack('>IIB', chunk_data)
                    metadata.update({
                        'Pixels per Unit X': ppux,
                        'Pixels per Unit Y': ppuy,
                        'Unit': 'Meters' if unit == 1 else 'Unknown'
                    })

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des métadonnées PNG pour '{file_path}': {e}")

    return metadata

def extract_docx_metadata(file_path):
    try:
        # Ouverture du document .docx
        doc = Document(file_path)
        core_props = doc.core_properties

        # Extraction des métadonnées principales
        metadata = {
            'Title': core_props.title,
            'Author': core_props.author,
            'Subject': core_props.subject,
            'Keywords': core_props.keywords,
            'Comments': core_props.comments,
            'Last Modified By': core_props.last_modified_by,
            'Revision': core_props.revision,
            'Created': core_props.created,
            'Last Modified': core_props.modified,
        }

        logger.info(f"Docx metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting DOCX metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"
    
def extract_excel_metadata(file_path):
    try:
        # Chargement du fichier Excel
        workbook = load_workbook(file_path)
        props = workbook.properties

        # Extraction des métadonnées principales
        metadata = {
            'Title': props.title,
            'Author': props.creator,
            'Subject': props.subject,
            'Keywords': props.keywords,
            'Comments': props.description,
            'Last Modified By': props.lastModifiedBy,
            'Revision': props.revision,
            'Created': props.created,
            'Last Modified': props.modified,
        }

        logger.info(f"Excel metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting Excel metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"

def extract_ppt_metadata(file_path):
    try:
        # Chargement du fichier PowerPoint
        presentation = Presentation(file_path)
        props = presentation.core_properties

        # Extraction des métadonnées principales
        metadata = {
            'Title': props.title,
            'Author': props.author,
            'Subject': props.subject,
            'Keywords': props.keywords,
            'Comments': props.comments,
            'Last Modified By': props.last_modified_by,
            'Revision': props.revision,
            'Created': props.created,
            'Last Modified': props.modified,
        }

        logger.info(f"PPT metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting PPT metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"

def extract_odf_metadata(file_path):
    try:
        # Chargement du fichier OpenOffice (ODF)
        odf_file = load(file_path)
        meta = odf_file.meta

        # Extraction des métadonnées principales
        metadata = {
            'Title': meta.title,
            'Author': meta.initialcreator,
            'Subject': meta.subject,
            'Keywords': meta.keyword,
            'Description': meta.description,
            'Last Modified By': meta.creator,
            'Creation Date': meta.creationdate,
            'Date of Modification': meta.date,
        }

        logger.info(f"ODF metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting ODF metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"


if __name__ == "__main__":
    # Exemple
    pdf_file = os.path.join(os.getcwd(), 'files', 'example.pdf')
    extract_pdf_metadata()