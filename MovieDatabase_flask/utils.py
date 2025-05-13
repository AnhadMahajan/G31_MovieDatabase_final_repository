from werkzeug.utils import secure_filename
import os
from flask import current_app

def save_file(file):
    if not file:
        return None
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return filename
