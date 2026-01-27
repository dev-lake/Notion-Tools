import os
import uuid
import zipfile
import shutil
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from converter import convert_markdown_to_docx

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Use env var in production

# Configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', 'output')
ALLOWED_EXTENSIONS = {'zip'}
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # 100MB default

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure directories exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_temp_files(temp_dir):
    """Remove temporary directory and its contents."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@app.route('/')
def index():
    # Get download file from session if it exists
    download_file = session.pop('download_file', None)
    return render_template('index.html', download_file=download_file)


@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    # Check if filename is empty
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    # Validate file type
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a .zip file', 'error')
        return redirect(url_for('index'))

    try:
        # Generate unique ID for this upload
        upload_id = str(uuid.uuid4())

        # Save uploaded file
        filename = secure_filename(file.filename)
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{upload_id}_{filename}')
        file.save(zip_path)
        print(f"[DEBUG] Saved uploaded file to: {zip_path}")

        # Create temp directory for extraction
        extract_dir = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
        os.makedirs(extract_dir, exist_ok=True)

        # Extract zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"[DEBUG] Extracted zip to: {extract_dir}")

        # Check for nested zip files (common in Notion exports)
        nested_zips = list(Path(extract_dir).rglob('*.zip'))
        if nested_zips:
            print(f"[DEBUG] Found {len(nested_zips)} nested zip files, extracting them...")
            for nested_zip in nested_zips:
                nested_extract_dir = nested_zip.parent / nested_zip.stem
                nested_extract_dir.mkdir(exist_ok=True)
                try:
                    with zipfile.ZipFile(nested_zip, 'r') as nested_ref:
                        nested_ref.extractall(nested_extract_dir)
                    print(f"[DEBUG] Extracted nested zip: {nested_zip.name}")
                except Exception as e:
                    print(f"[DEBUG] Failed to extract nested zip {nested_zip.name}: {e}")

        # Find all markdown files
        md_files = list(Path(extract_dir).rglob('*.md'))
        print(f"[DEBUG] Found {len(md_files)} markdown files: {[str(f) for f in md_files]}")

        if not md_files:
            print("[DEBUG] No markdown files found in zip")
            flash('No markdown files found in the zip archive', 'error')
            cleanup_temp_files(extract_dir)
            os.remove(zip_path)
            return redirect(url_for('index'))

        # Create output directory for this upload
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], upload_id)
        os.makedirs(output_dir, exist_ok=True)

        # Convert each markdown file
        converted_files = []
        for md_file in md_files:
            try:
                # Generate output filename
                docx_filename = md_file.stem + '.docx'
                output_path = os.path.join(output_dir, docx_filename)

                # Get the directory containing the markdown file (for image references)
                images_dir = md_file.parent

                # Convert to Word
                convert_markdown_to_docx(str(md_file), output_path, str(images_dir))
                converted_files.append(docx_filename)
                print(f"[DEBUG] Successfully converted: {md_file.name}")
            except Exception as e:
                print(f"[DEBUG] Error converting {md_file.name}: {str(e)}")
                flash(f'Error converting {md_file.name}: {str(e)}', 'warning')

        # Create a zip file with all converted documents
        output_zip_name = f'{upload_id}_converted.zip'
        output_zip_path = os.path.join(app.config['OUTPUT_FOLDER'], output_zip_name)
        print(f"[DEBUG] Creating output zip: {output_zip_path}")

        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for docx_file in converted_files:
                file_path = os.path.join(output_dir, docx_file)
                zipf.write(file_path, docx_file)
        print(f"[DEBUG] Created zip with {len(converted_files)} files")

        # Cleanup temporary files
        cleanup_temp_files(extract_dir)
        cleanup_temp_files(output_dir)
        os.remove(zip_path)

        # Success message
        flash(f'Successfully converted {len(converted_files)} markdown file(s) to Word documents', 'success')
        print(f"[DEBUG] Conversion complete, redirecting with download_file={output_zip_name}")

        # Store download file in session and redirect (Post/Redirect/Get pattern)
        session['download_file'] = output_zip_name
        return redirect(url_for('index'))

    except zipfile.BadZipFile:
        print("[DEBUG] BadZipFile exception")
        flash('Invalid zip file', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"[DEBUG] Unexpected exception: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    """Serve the generated zip file for download."""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
        if not os.path.exists(file_path):
            flash('File not found', 'error')
            return redirect(url_for('index'))

        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

        # Schedule file deletion after download (in a production app, use a background task)
        # For now, we'll leave the file for manual cleanup
        return response
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    # Get configuration from environment variables
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    port = int(os.environ.get('PORT', 5000))

    # Run Flask
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=port,
        use_reloader=debug_mode,
        reloader_type='stat' if debug_mode else None
    )
