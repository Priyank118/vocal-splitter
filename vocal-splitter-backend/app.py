import os
import uuid
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import logging
from pathlib import Path

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO)

# Define folders
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
MODEL_FOLDER = 'spleeter_models'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a'}

# --- Flask App Initialization ---
# Check if static folder exists (for production with frontend)
static_folder = None
static_url_path = '/'
if os.path.exists('static'):
    static_folder = 'static'
    static_url_path = '/'

app = Flask(__name__, static_folder=static_folder, static_url_path=static_url_path)
CORS(app, resources={r"/*": {"origins": "*"}}) 

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if the file's extension is in the allowed list."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_directory_if_not_exists(directory):
    """Creates a directory if it doesn't already exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

# --- Main Routes ---
@app.route('/upload', methods=['POST'])
def upload_and_split_file():
    """
    Handles file upload, runs Spleeter for source separation,
    and returns download links for the separated tracks.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please upload an audio file."}), 400

    try:
        unique_id = str(uuid.uuid4())
        original_filename = file.filename
        safe_filename = "".join(c for c in original_filename if c.isalnum() or c in ('.', '_', '-')).rstrip()
        unique_filename = f"{unique_id}_{safe_filename}"
        
        create_directory_if_not_exists(UPLOAD_FOLDER)
        upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(upload_path)
        logging.info(f"File saved successfully at {upload_path}")

    except Exception as e:
        logging.error(f"Error saving file: {e}")
        return jsonify({"error": "Failed to save the uploaded file."}), 500

    try:
        # --- THIS IS THE FINAL, MOST ROBUST FIX ---

        # 1. Determine the correct executable name based on the OS.
        spleeter_exe_name = 'spleeter.exe' if sys.platform == "win32" else 'spleeter'
        
        # 2. Construct the full path to the executable within the virtual environment's 'Scripts' folder.
        #    sys.executable points to the python.exe in the venv.
        spleeter_executable_path = os.path.join(os.path.dirname(sys.executable), spleeter_exe_name)

        # 3. Log the path we constructed for debugging.
        logging.info(f"Attempting to use Spleeter executable at: {spleeter_executable_path}")

        # 4. Check if the file actually exists before trying to run it.
        if not os.path.exists(spleeter_executable_path):
            error_msg = f"Spleeter executable not found at the expected path: {spleeter_executable_path}"
            logging.error(error_msg)
            return jsonify({"error": error_msg}), 500

        # Set environment variable for Spleeter models
        os.environ['SPLEETER_MODEL_PATH'] = MODEL_FOLDER
        create_directory_if_not_exists(MODEL_FOLDER)
        create_directory_if_not_exists(OUTPUT_FOLDER)
        
        # 5. Build the command using the full, verified path.
        command = [
            spleeter_executable_path, "separate",
            "-p", "spleeter:2stems",
            "-o", OUTPUT_FOLDER,
            upload_path
        ]
        
        logging.info(f"Running Spleeter command: {' '.join(command)}")
        
        process = subprocess.run(command, check=True, capture_output=True, text=True, shell=False)
        
        logging.info("Spleeter process finished successfully.")
        logging.info(f"Spleeter stdout: {process.stdout}")
        logging.error(f"Spleeter stderr: {process.stderr}")

        output_subfolder_name = os.path.splitext(unique_filename)[0]
        vocals_filename = f"{output_subfolder_name}/vocals.wav"
        music_filename = f"{output_subfolder_name}/accompaniment.wav"

        if not os.path.exists(os.path.join(OUTPUT_FOLDER, vocals_filename)):
            logging.error("Spleeter ran but did not produce the expected output files.")
            return jsonify({"error": "Processing failed after running Spleeter."}), 500

        return jsonify({
            "vocalsUrl": f"/download/{vocals_filename}",
            "musicUrl": f"/download/{music_filename}"
        })

    except subprocess.CalledProcessError as e:
        logging.error(f"Spleeter execution failed with return code {e.returncode}")
        logging.error(f"Spleeter stdout: {e.stdout}")
        logging.error(f"Spleeter stderr: {e.stderr}")
        return jsonify({"error": "An error occurred during audio processing."}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500


@app.route('/download/<path:subpath>')
def download_file(subpath):
    """Serves the separated audio files for download."""
    logging.info(f"Download requested for: {subpath}")
    return send_from_directory(OUTPUT_FOLDER, subpath, as_attachment=True)


if __name__ == '__main__':
    create_directory_if_not_exists(UPLOAD_FOLDER)
    create_directory_if_not_exists(OUTPUT_FOLDER)
    
    # Determine if running in production
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    if is_production:
        # Production: Gunicorn will handle this
        pass
    else:
        # Development: Run Flask dev server
        app.run(host='0.0.0.0', port=5000, debug=True)


# Serve the frontend SPA in production
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    """Serves the frontend for all routes not matching API endpoints."""
    # Only serve frontend files if we're in production (static folder exists)
    if static_folder and os.path.exists('static'):
        # For API routes, let them be handled by their respective endpoints
        if path.startswith('api/') or path in ['upload', 'download']:
            return jsonify({"error": "Not Found"}), 404
        
        # Try to serve the requested file
        if path and os.path.exists(os.path.join('static', path)):
            return send_from_directory('static', path)
        
        # Fallback to index.html for SPA routing
        if os.path.exists('static/index.html'):
            return send_from_directory('static', 'index.html')
    
    return jsonify({"error": "Not Found"}), 404
