# pymetadata

A Python tool for extracting metadata from various file types.

## Features

- Metadata extraction for the following formats:
  - Images: JPEG (EXIF metadata, comments, headers), PNG, TIFF, HEIC, SVG
  - Documents: PDF (standard metadata and XREF), DOCX, Excel, PowerPoint, ODF, TXT

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/arthur469/pymetadata.git
   cd pymetadata
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install system dependencies:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install libmagic1
     ```
   - On Windows:
     - Download and install the latest version of [python-magic-bin](https://pypi.org/project/python-magic-bin/)

## Usage

1. Place the files you want to analyze in the `files` directory

2. Run the metadata extraction:
   ```bash
   python main.py
   ```

3. The results will be saved in the `results` directory as JSON files

## Output Format

The metadata is extracted and saved in JSON format with the following structure:

- For images (JPEG):
  - EXIF metadata (camera settings, GPS data, timestamps)
  - Comments and descriptions
  - Raw headers
  - Color space information
  - Resolution and dimensions
  - Thumbnail data
  
- For images (PNG):
  - Basic metadata (dimensions, color type, bit depth)
  - Compression info
  - Gamma values
  - Physical pixel dimensions
  - Timestamps
  - Text annotations
  
- For PDF documents:
  - Standard metadata:
    - Title, author, subject, keywords
    - Creator and producer applications
    - Creation and modification dates
    - Encryption status
    - Page count and dimensions
  - XREF metadata:
    - Document structure
    - Font information
    - Image resources
    - Form data
    - Annotations
    - Bookmarks
    - Attachments

## Others 

You can find files examples [here](https://examplefile.com/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
