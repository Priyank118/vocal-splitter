import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import logging

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO)

# Define the upload and output folders
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
MODEL_FOLDER = 'spleeter_models' # New folder for Spleeter's models
# Define the allowed file extensions
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a'}

# --- Flask App Initialization ---
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow requests from our React frontend
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
    # 1. --- File Validation ---
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please upload an audio file."}), 400

    # 2. --- File Saving ---
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

    # 3. --- Audio Splitting with Spleeter ---
    try:
        # ** THE FIX IS HERE **
        # We are telling Spleeter to use a local folder for its models.
        os.environ['SPLEETER_MODEL_PATH'] = MODEL_FOLDER
        create_directory_if_not_exists(MODEL_FOLDER)
        
        create_directory_if_not_exists(OUTPUT_FOLDER)
        
        spleeter_output_dir = os.path.join(OUTPUT_FOLDER)
        command = [
            "spleeter", "separate",
            "-p", "spleeter:2stems",
            "-o", spleeter_output_dir,
            upload_path
        ]
        
        logging.info(f"Running Spleeter command: {' '.join(command)}")
        
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        
        logging.info("Spleeter process finished.")
        logging.info(f"Spleeter stdout: {process.stdout}")
        logging.error(f"Spleeter stderr: {process.stderr}")

        # 4. --- Generate Download Links ---
        output_subfolder_name = os.path.splitext(unique_filename)[0]
        
        vocals_filename = f"{output_subfolder_name}/vocals.wav"
        music_filename = f"{output_subfolder_name}/accompaniment.wav"

        if not os.path.exists(os.path.join(OUTPUT_FOLDER, vocals_filename)) or \
           not os.path.exists(os.path.join(OUTPUT_FOLDER, music_filename)):
            logging.error("Spleeter did not produce the expected output files.")
            return jsonify({"error": "Processing failed. Could not find separated files."}), 500

        return jsonify({
            "vocalsUrl": f"/download/{vocals_filename}",
            "musicUrl": f"/download/{music_filename}"
        })

    except subprocess.CalledProcessError as e:
        logging.error(f"Spleeter execution failed: {e}")
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


# --- Main Execution ---
if __name__ == '__main__':
    create_directory_if_not_exists(UPLOAD_FOLDER)
    create_directory_if_not_exists(OUTPUT_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)
