import os
from werkzeug.utils import secure_filename
import bleach
from flask import current_app

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def save_images(files, animal_id):
    for file in files:
        if file and allowed_file(file.filename):
            fn = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            path = os.path.join(upload_folder, fn)
            file.save(path)
            from models import Photo, db
            db.session.add(Photo(filename=fn, mime_type=file.mimetype, animal_id=animal_id))

def sanitize_markdown(text):
    clean = bleach.clean(text, tags=['p', 'ul', 'li', 'strong', 'em', 'a'], strip=True)
    return clean
