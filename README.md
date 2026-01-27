# Notion to Word Converter

A Flask web application that converts Notion-exported markdown files to beautifully formatted Word documents (.docx). Supports batch conversion, preserves formatting, and handles images including those with URL-encoded paths (e.g., Chinese characters).

## Features

### Core Functionality
- 📤 Upload Notion export zip files through web interface
- 🔄 Convert multiple markdown files at once (batch processing)
- 📦 Download all converted documents as a single zip file
- 🌐 Handles URL-encoded filenames (supports Chinese, Japanese, Korean, and other Unicode characters)
- 🖼️ Automatic image extraction and embedding

### Formatting Support
- **Headings**: H1-H6 with proper hierarchy
- **Text Styling**: Bold, italic, inline code
- **Lists**: Bulleted and numbered lists with nested support
- **Tables**: Full table support with header formatting
- **Code Blocks**: Syntax-preserved code blocks with monospace font
- **Links**: Hyperlinks with URL display
- **Images**: Embedded images with automatic sizing (max 6 inches width)
- **Blockquotes**: Indented quote blocks
- **Horizontal Rules**: Section dividers

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository:
```bash
git clone <repository-url>
cd notion_tools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies
The following packages will be installed:
- `Flask==3.0.0` - Web framework
- `python-docx==1.1.0` - Word document generation
- `markdown2==2.4.12` - Markdown parsing
- `Pillow==10.2.0` - Image processing
- `html5lib==1.1` - HTML parsing
- `BeautifulSoup4==4.12.3` - HTML/XML parsing
- `gunicorn==21.2.0` - Production WSGI server
- `requests==2.31.0` - HTTP library

## Usage

### Docker Deployment (Recommended for Production)

**Quick start with Docker Compose:**
```bash
# Start the application
docker-compose up -d

# Access at http://localhost:5000

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

**Or using Docker CLI:**
```bash
# Build the image
docker build -t notion-to-word-converter .

# Run the container
docker run -d -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/output:/app/output \
  -e SECRET_KEY=your-secret-key \
  notion-to-word-converter
```

📖 **See [DOCKER.md](DOCKER.md) for complete Docker deployment guide**

### Web Interface (Local Development)

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload and convert:
   - Click the upload area or drag and drop your Notion export .zip file
   - Click "Convert to Word" button
   - Wait for processing (progress indicator will show)
   - Download the converted documents as a zip file

### Command Line Usage

You can also use the converter directly from Python:

```python
from converter import convert_markdown_to_docx

# Convert a single markdown file
convert_markdown_to_docx(
    md_file_path='path/to/file.md',
    output_path='path/to/output.docx',
    images_dir='path/to/images'  # Optional: directory containing images
)
```

### API Endpoint

The application exposes a REST API endpoint:

**POST** `/convert`
- Content-Type: `multipart/form-data`
- Parameter: `file` (zip file)
- Returns: ZIP file containing converted .docx files

## Exporting from Notion

### Step-by-Step Guide

1. **Open Notion** and navigate to the page(s) you want to export
2. **Click the "..." menu** (three dots) in the top-right corner
3. **Select "Export"**
4. **Choose export settings:**
   - Format: **"Markdown & CSV"** (required)
   - Include content: Choose "Everything" or specific pages
   - Include subpages: Enable if you want nested pages
5. **Click "Export"** and download the zip file
6. **Upload the zip file** to this converter

### Important Notes
- ✅ Use "Markdown & CSV" format (not HTML or PDF)
- ✅ Keep the zip file structure intact (don't extract and re-zip)
- ✅ Images will be automatically included in the export
- ✅ Supports exports with Chinese, Japanese, Korean, and other Unicode filenames

## Project Structure

```
notion_tools/
├── app.py              # Flask application
├── converter.py        # Markdown to Word conversion logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Web interface
├── uploads/           # Temporary storage (auto-created)
├── output/            # Generated files (auto-created)
└── test_data/         # Test files and examples
```

## Testing

### Test Files
Test files are provided in the `test_data/` directory:
- `test.md` - Sample markdown with various formatting
- `test2.md` - Additional test file
- `notion_export_test.zip` - Sample Notion export
- `ExportBlock-*.zip` - Real Notion export with Chinese characters

### Running Tests

**Test the standalone converter:**
```bash
python -c "from converter import convert_markdown_to_docx; \
convert_markdown_to_docx('test_data/test.md', 'test_output.docx')"
```

**Test the web application:**
```bash
# 1. Start the server
python app.py

# 2. Open http://localhost:5000 in your browser
# 3. Upload test_data/notion_export_test.zip
# 4. Verify the conversion completes successfully
```

**Test with Chinese characters:**
```bash
# Upload test_data/ExportBlock-66be433a-e3a6-4999-b173-2685a0080949-Part-1.zip
# This tests URL-encoded path handling
```

## Configuration

### Application Settings

Edit `app.py` to customize:

```python
# Maximum upload file size
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Secret key (change for production!)
app.secret_key = 'your-secret-key-here'

# Server configuration
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Image Settings

Edit `converter.py` to adjust image sizing:

```python
# In _add_image_to_paragraph function
run.add_picture(image_path, width=Inches(6))  # Change width as needed
```

### Network Access
- Default: Server runs on `0.0.0.0:5000` (accessible from network)
- Local only: Change to `127.0.0.1:5000` in `app.py`
- Custom port: Modify the `port` parameter

## Notes

### Important Information
- 🗑️ Temporary files are automatically cleaned up after conversion
- 🖼️ Images must be included in the uploaded zip file with correct relative paths
- 🎨 The converter preserves Notion's formatting as closely as possible
- 🔒 For production deployment, **change the `secret_key`** in `app.py`
- 🌐 URL-encoded filenames (Chinese, Japanese, Korean, etc.) are automatically decoded
- 📦 The converter handles nested folder structures from Notion exports

### Technical Details
- **Markdown Parser**: Uses `markdown2` with support for tables, code blocks, and task lists
- **HTML Processing**: BeautifulSoup4 for robust HTML parsing
- **Image Handling**: Automatic URL decoding via `urllib.parse.unquote`
- **Word Generation**: python-docx for .docx file creation
- **File Cleanup**: Automatic cleanup of temporary files after 1 hour

### Limitations
- Maximum file size: 100MB (configurable)
- Only .zip files are accepted
- Markdown must be valid (follows CommonMark spec)
- Some advanced Notion features (databases, embeds) may not convert perfectly
- Image width is fixed at 6 inches (configurable in code)

## Troubleshooting

### Common Issues

**❌ "No markdown files found in the uploaded zip"**
- ✅ Ensure your Notion export is in "Markdown & CSV" format (not HTML)
- ✅ Check that .md files are present in the zip (don't extract and re-zip)
- ✅ Verify the zip file isn't corrupted

**❌ "Image not found" messages in output**
- ✅ Verify images are included in the Notion export
- ✅ Check that image paths in markdown match the zip structure
- ✅ For URL-encoded paths (Chinese characters), ensure you're using the latest version with URL decoding support

**❌ Images with Chinese/Unicode filenames not loading**
- ✅ This is now fixed! The converter automatically handles URL-encoded paths
- ✅ Update to the latest version if you're still experiencing issues

**❌ Conversion errors or crashes**
- ✅ Check the terminal/console for specific error messages
- ✅ Verify the markdown syntax is valid
- ✅ Try with a smaller file first to isolate the issue
- ✅ Check that all dependencies are installed correctly

**❌ "File too large" error**
- ✅ Default limit is 100MB
- ✅ Increase `MAX_CONTENT_LENGTH` in `app.py` if needed
- ✅ Consider splitting large exports into smaller chunks

**❌ Server won't start**
- ✅ Check if port 5000 is already in use
- ✅ Try a different port: `app.run(port=5001)`
- ✅ Verify all dependencies are installed: `pip install -r requirements.txt`

### Getting Help

If you encounter issues:
1. Check the error message in the web interface
2. Look at the terminal/console output for detailed errors
3. Verify your Notion export format is correct
4. Try with the provided test files first

## License

MIT License - feel free to use and modify as needed.

## Recent Updates

### v1.1.0 (Latest)
- ✨ Added support for URL-encoded filenames (Chinese, Japanese, Korean, etc.)
- 🐛 Fixed "Image not found" errors for files with Unicode characters
- 🔧 Improved image path handling with automatic URL decoding
- 📝 Enhanced documentation

### v1.0.0
- 🎉 Initial release
- ✅ Basic markdown to Word conversion
- ✅ Web interface with drag-and-drop upload
- ✅ Batch processing support
- ✅ Image embedding

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd notion_tools

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python app.py
```

## Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [python-docx](https://python-docx.readthedocs.io/) - Word document generation
- [markdown2](https://github.com/trentm/python-markdown2) - Markdown parsing
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the Troubleshooting section above
- Review the test files for examples