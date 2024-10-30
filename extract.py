"""
Metadata extraction module for various file formats.

This module provides functions to extract metadata from different file types including:
- Images (JPEG, PNG, TIFF, WebP, HEIC)
- Documents (PDF, DOCX, Excel, PowerPoint, ODF)

Each extraction function returns a dictionary containing the metadata.
"""

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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_exif_metadata(file_path):
    """Extract EXIF metadata from an image file."""
    try:
        with open(file_path, 'rb') as image_file:
            tags = exifread.process_file(image_file)
        return {tag: str(tags[tag]) for tag in tags.keys()}
    except Exception as e:
        logger.error(f"Error extracting EXIF metadata for '{file_path}': {e}")
        return None
    
def extract_pdf_metadata(file_path):
    """Extract standard metadata from a PDF file."""
    try:
        pdf_document = pymupdf.open(file_path)
        standard_metadata = pdf_document.metadata
        logger.info("Metadata extracted successfully")
        return {"Standard Metadata": standard_metadata}
    except Exception as e:
        logger.error(f"Error extracting PDF metadata: {e}")
        return None

def extract_pdf_xref(file_path):
    """Extract low-level XREF table metadata from a PDF file."""
    try:
        pdf_document = pymupdf.open(file_path)
        xref_metadata = {}
        logger.info("Extracting XREF:")
        for xref_index in range(1, pdf_document.xref_length()):
            object_type = pdf_document.xref_object(xref_index, compressed=False)
            xref_metadata[f"XREF {xref_index}"] = object_type
        return {"XREF Metadata": xref_metadata}
    except Exception as e:
        logger.error(f"Error extracting PDF XREF: {e}")
        return None

def extract_pdf_full_metadata(file_path):
    """Extract both standard and XREF metadata from a PDF file."""
    try:
        standard_metadata = extract_pdf_metadata(file_path)
        xref_metadata = extract_pdf_xref(file_path)
        full_metadata = {}
        if standard_metadata:
            full_metadata.update(standard_metadata)
        if xref_metadata:
            full_metadata.update(xref_metadata)
        return full_metadata
    except Exception as e:
        logger.error(f"Error extracting full PDF metadata: {e}")
        return None

def extract_jpeg_metadata(file_path):
    """Extract comprehensive metadata from a JPEG file."""
    metadata = {}
    try:
        with Image.open(file_path) as image:
            width, height = image.size
            image_format = image.format
            color_mode = image.mode
            image_info = image.info

            metadata.update({
                'File Name': os.path.basename(file_path),
                'File Size': f"{os.path.getsize(file_path) / 1024:.0f} kB",
                'Format': image_format,
                'Mode': color_mode,
                'Image Width': width,
                'Image Height': height,
                'Image Size': f"{width}x{height}",
                'Megapixels': round((width * height) / 1_000_000, 1),
            })

            if 'jfif_version' in image_info:
                metadata['JFIF Version'] = f"{image_info['jfif_version'][0]}.{image_info['jfif_version'][1]}"
            else:
                metadata['JFIF Version'] = 'Unknown'

            if 'dpi' in image_info:
                metadata['X Resolution'] = float(image_info['dpi'][0])
                metadata['Y Resolution'] = float(image_info['dpi'][1])
                metadata['Resolution Unit'] = 'inches'
            else:
                metadata['X Resolution'] = 'Unknown'
                metadata['Y Resolution'] = 'Unknown'
                metadata['Resolution Unit'] = 'Unknown'

            metadata['ICC Profile'] = 'Present' if 'icc_profile' in image_info else 'Absent'
            metadata['Encoding Process'] = 'Progressive JPEG, Huffman coding' if 'progression' in image_info else 'Baseline DCT, Huffman coding'
            metadata['Bits Per Sample'] = 8
            metadata['Color Components'] = len(image.getbands())

            if 'subsampling' in image_info:
                subsampling = image_info['subsampling']
                metadata['YCbCr Subsampling'] = 'YCbCr4:2:0 (2 2)' if subsampling == (2, 2) else (
                    'YCbCr4:2:2 (2 1)' if subsampling == (2, 1) else 'YCbCr4:4:4 (1 1)'
                )
            else:
                metadata['YCbCr Subsampling'] = 'Unknown'

        with open(file_path, 'rb') as image_file:
            tags = exifread.process_file(image_file)

        exif_metadata = {}
        for tag, value in tags.items():
            if "MakerNote" not in tag and "JPEGThumbnail" not in tag:
                exif_metadata[tag] = str(value)
        
        metadata['EXIF Metadata'] = exif_metadata
        metadata['Raw Header'] = extract_raw_header(file_path)
        metadata['Comment'] = extract_jpeg_comment(file_path) or "None"

    except Exception as e:
        logger.error(f"Error extracting JPEG metadata for '{file_path}': {e}")

    return metadata

def extract_raw_header(file_path):
    """Extract raw header data from a JPEG file."""
    raw_header = []
    try:
        with open(file_path, 'rb') as image_file:
            header_bytes = image_file.read(512)
            raw_header = ' '.join(f'{byte:02X}' for byte in header_bytes)
    except Exception as e:
        logger.error(f"Error extracting raw JPEG headers for '{file_path}': {e}")
    
    return raw_header

def extract_jpeg_comment(file_path):
    """Extract comments from JPEG COM segment."""
    try:
        with open(file_path, 'rb') as image_file:
            while True:
                byte = image_file.read(1)
                if not byte:
                    break
                if byte == b'\xFF':
                    marker = image_file.read(1)
                    if marker == b'\xFE':
                        length = struct.unpack('>H', image_file.read(2))[0]
                        comment = image_file.read(length - 2).decode('utf-8', errors='replace')
                        return comment
                    else:
                        length = struct.unpack('>H', image_file.read(2))[0]
                        image_file.read(length - 2)
    except Exception as e:
        logger.error(f"Error extracting JPEG comments for '{file_path}': {e}")
        return None

def extract_png_metadata(file_path):
    """Extract metadata from a PNG file."""
    metadata = {}
    try:
        with open(file_path, 'rb') as image_file:
            tags = exifread.process_file(image_file, stop_tag="UNDEF", details=False)
        
        if tags:
            exif_metadata = {tag: str(tags[tag]) for tag in tags.keys()}
            metadata['EXIF Metadata'] = exif_metadata
        else:
            metadata['EXIF Metadata'] = "No EXIF metadata found"

        with open(file_path, 'rb') as image_file:
            header = image_file.read(8)
            if header != b'\x89PNG\r\n\x1a\n':
                raise ValueError("Not a valid PNG file.")

            metadata['PNG Signature'] = header.hex().upper()

            while True:
                chunk_header = image_file.read(8)
                if len(chunk_header) < 8:
                    break

                length, chunk_type = struct.unpack('>I4s', chunk_header)
                chunk_data = image_file.read(length)
                image_file.read(4)

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
                    pixels_per_unit_x, pixels_per_unit_y, unit = struct.unpack('>IIB', chunk_data)
                    metadata.update({
                        'Pixels per Unit X': pixels_per_unit_x,
                        'Pixels per Unit Y': pixels_per_unit_y,
                        'Unit': 'Meters' if unit == 1 else 'Unknown'
                    })

    except Exception as e:
        logger.error(f"Error extracting PNG metadata for '{file_path}': {e}")

    return metadata

def extract_tiff_metadata(file_path):
    """Extract metadata from a TIFF file."""
    metadata = {}
    try:
        with Image.open(file_path) as image:
            width, height = image.size
            metadata.update({
                'Format': image.format,
                'Mode': image.mode,
                'Image Width': width,
                'Image Height': height,
                'Image Size': f'{width}x{height}'
            })

        exif_metadata = extract_exif_metadata(file_path)
        metadata['EXIF Metadata'] = exif_metadata if exif_metadata else "None"

    except Exception as e:
        logger.error(f"Error extracting TIFF metadata for '{file_path}': {e}")

    return metadata

def extract_webp_metadata(file_path):
    """Extract metadata from a WebP file."""
    metadata = {}
    try:
        with Image.open(file_path) as image:
            width, height = image.size
            metadata.update({
                'Format': image.format,
                'Mode': image.mode,
                'Image Width': width,
                'Image Height': height,
                'Image Size': f'{width}x{height}'
            })

        exif_metadata = extract_exif_metadata(file_path)
        metadata['EXIF Metadata'] = exif_metadata if exif_metadata else "None"

    except Exception as e:
        logger.error(f"Error extracting WebP metadata for '{file_path}': {e}")

    return metadata

def extract_heic_metadata(file_path):
    """Extract metadata from a HEIC file."""
    metadata = {}
    try:
        with Image.open(file_path) as image:
            width, height = image.size
            metadata.update({
                'Format': image.format,
                'Mode': image.mode,
                'Image Width': width,
                'Image Height': height,
                'Image Size': f'{width}x{height}'
            })

        exif_metadata = extract_exif_metadata(file_path)
        metadata['EXIF Metadata'] = exif_metadata if exif_metadata else "None"

    except Exception as e:
        logger.error(f"Error extracting HEIC metadata for '{file_path}': {e}")

    return metadata

def extract_docx_metadata(file_path):
    """Extract metadata from a DOCX file."""
    try:
        document = Document(file_path)
        core_properties = document.core_properties

        metadata = {
            'Title': core_properties.title,
            'Author': core_properties.author,
            'Subject': core_properties.subject,
            'Keywords': core_properties.keywords,
            'Comments': core_properties.comments,
            'Last Modified By': core_properties.last_modified_by,
            'Revision': core_properties.revision,
            'Created': core_properties.created,
            'Last Modified': core_properties.modified,
        }

        logger.info(f"Docx metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting DOCX metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"
    
def extract_excel_metadata(file_path):
    """Extract metadata from an Excel file."""
    try:
        workbook = load_workbook(file_path)
        properties = workbook.properties

        metadata = {
            'Title': properties.title,
            'Author': properties.creator,
            'Subject': properties.subject,
            'Keywords': properties.keywords,
            'Comments': properties.description,
            'Last Modified By': properties.lastModifiedBy,
            'Revision': properties.revision,
            'Created': properties.created,
            'Last Modified': properties.modified,
        }

        logger.info(f"Excel metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting Excel metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"

def extract_ppt_metadata(file_path):
    """Extract metadata from a PowerPoint file."""
    try:
        presentation = Presentation(file_path)
        properties = presentation.core_properties

        metadata = {
            'Title': properties.title,
            'Author': properties.author,
            'Subject': properties.subject,
            'Keywords': properties.keywords,
            'Comments': properties.comments,
            'Last Modified By': properties.last_modified_by,
            'Revision': properties.revision,
            'Created': properties.created,
            'Last Modified': properties.modified,
        }

        logger.info(f"PPT metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting PPT metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"

def extract_odf_metadata(file_path):
    """Extract metadata from an OpenDocument Format file."""
    try:
        odf_document = load(file_path)
        metadata_info = odf_document.meta

        metadata = {
            'Title': metadata_info.title,
            'Author': metadata_info.initialcreator,
            'Subject': metadata_info.subject,
            'Keywords': metadata_info.keyword,
            'Description': metadata_info.description,
            'Last Modified By': metadata_info.creator,
            'Creation Date': metadata_info.creationdate,
            'Date of Modification': metadata_info.date,
        }

        logger.info(f"ODF metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting ODF metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"

def extract_svg_metadata(file_path):
    """Extract metadata from an SVG file."""
    try:
        from xml.etree import ElementTree as ET
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Get SVG namespace
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        metadata = {
            'Width': root.get('width'),
            'Height': root.get('height'),
            'ViewBox': root.get('viewBox'),
            'Version': root.get('version'),
            'BaseProfile': root.get('baseProfile'),
            'Title': None,
            'Description': None
        }
        
        # Extract title and description if present
        title = root.find('.//svg:title', ns)
        if title is not None:
            metadata['Title'] = title.text
            
        desc = root.find('.//svg:desc', ns)
        if desc is not None:
            metadata['Description'] = desc.text
            
        # Get metadata from metadata tag if present
        metadata_elem = root.find('.//svg:metadata', ns)
        if metadata_elem is not None:
            for child in metadata_elem:
                metadata[child.tag] = child.text
                
        logger.info(f"SVG metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting SVG metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"

def extract_txt_metadata(file_path):
    """Extract metadata from a text file."""
    try:
        metadata = {
            'File Size': os.path.getsize(file_path),
            'Created': datetime.datetime.fromtimestamp(os.path.getctime(file_path)),
            'Modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)),
            'Accessed': datetime.datetime.fromtimestamp(os.path.getatime(file_path)),
            'Line Count': 0,
            'Word Count': 0,
            'Character Count': 0,
            'Encoding': None
        }

        # Detect encoding
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            metadata['Encoding'] = result['encoding']

        # Get content stats
        with open(file_path, 'r', encoding=metadata['Encoding']) as file:
            content = file.read()
            lines = content.splitlines()
            words = content.split()
            
            metadata['Line Count'] = len(lines)
            metadata['Word Count'] = len(words)
            metadata['Character Count'] = len(content)

        logger.info(f"Text file metadata for {file_path}: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting text file metadata for '{file_path}': {e}")
        return f"Error extracting metadata: {e}"

if __name__ == "__main__":
    pdf_file = os.path.join(os.getcwd(), 'files', 'example.pdf')
    extract_pdf_metadata()