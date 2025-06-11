# app.py
from flask import Flask, render_template, request, redirect, url_for, send_file, abort, session, flash, jsonify, Response
import os, re, subprocess, tempfile, shutil, urllib.parse, json
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

ALLOWED_EXTENSIONS = {'zip', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}
LOG_FILE = 'logs/activity.log'
TRASH_DIR_NAME = ".trash"

USERS = {
    'Adminuser': {'password': 'Adminonly', 'role': 'admin'},
    'ViewerUser': {'password': 'viewonly', 'role': 'viewer'}
}

# --- Helpers ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Session expired. Please log in again.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') != role:
                flash("Unauthorized access.")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_event(event):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {event}\n")

def move_to_trash(path):
    trash_path = os.path.join(os.path.dirname(path), TRASH_DIR_NAME)
    os.makedirs(trash_path, exist_ok=True)
    trashed_file = os.path.join(trash_path, os.path.basename(path))
    shutil.move(path, trashed_file)
    log_event(f"Moved to trash: {path}")

def get_mountable_devices():
    result = subprocess.run(['lsblk', '-o', 'NAME,MOUNTPOINT,FSTYPE,RM,TYPE', '-nr'], capture_output=True, text=True)
    devices = []
    for line in result.stdout.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 5:
            name, mountpoint, fstype, removable, dev_type = parts
            if fstype in ['ext4', 'ext3', 'ntfs', 'vfat', 'exfat', 'xfs'] and dev_type == 'part':
                if not mountpoint or mountpoint == '-':
                    devices.append((name, fstype, removable == '1'))
    return devices

def mount_device(name):
    dev_path = f"/dev/{name}"
    mount_path = f"/mnt/{name}"
    os.makedirs(mount_path, exist_ok=True)
    try:
        subprocess.run(['sudo', 'mount', dev_path, mount_path], check=True)
        return True, mount_path
    except subprocess.CalledProcessError:
        return False, None

def get_drive_label(device_name):
    try:
        result = subprocess.run(
            ['lsblk', f'/dev/{device_name}', '-o', 'LABEL', '-nr'],
            capture_output=True, text=True
        )
        return result.stdout.strip() or None
    except:
        return None

def list_all_drives():
    result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,RM', '-nr'], capture_output=True, text=True)
    drives = []
    for line in result.stdout.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 6:
            name, size, dev_type, mountpoint, fstype, removable = parts
            drive = {
                'device': f"/dev/{name}",
                'size': size,
                'type': dev_type,
                'mountpoint': mountpoint if mountpoint != '-' else None,
                'fstype': fstype if fstype != '-' else None,
                'removable': removable == '1',
                'label': get_drive_label(name)
            }
            if drive['removable'] and not drive['mountpoint']:
                success, mount_path = mount_device(name)
                if success:
                    drive['mountpoint'] = mount_path
            drives.append(drive)
    return drives

def get_video_metadata(path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', path],
            capture_output=True, text=True
        )
        print("FFPROBE OUTPUT:", result.stdout)  # DEBUG
        return json.loads(result.stdout)
    except Exception as e:
        print("Metadata extraction error:", e)
        return None


# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            session['role'] = USERS[username]['role']
            log_event(f"User '{username}' logged in.")
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_event(f"User '{session['username']}' logged out.")
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def index():
    drives = list_all_drives()
    return render_template('index.html', drives=drives)

@app.route('/mount', methods=['POST'])
@login_required
def mount():
    device = request.form['device']
    name = device.replace('/dev/', '')
    success, mount_path = mount_device(name)
    if success:
        flash(f"Mounted {device} at {mount_path}")
        log_event(f"Mounted device: {device} at {mount_path}")
    else:
        flash(f"Failed to mount {device}")
    return redirect(url_for('index'))

@app.route('/browse')
@login_required
def browse():
    path = request.args.get('path', '/mnt')
    search_query = request.args.get('q', '').lower()
    if not os.path.exists(path):
        flash(f"Invalid path: {path}")
        return redirect(url_for('index'))
    try:
        entries = []
        for f in sorted(os.listdir(path)):
            full_path = os.path.join(path, f)
            if search_query and search_query not in f.lower():
                continue
            encoded_path = urllib.parse.quote(full_path)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else "-"
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
            entries.append((f, encoded_path, is_dir, size, mtime))
        entries.sort(key=lambda x: (not x[2], x[0].lower()))
        return render_template('browse.html', entries=entries, path=path)
    except Exception as e:
        flash(f"Error reading directory: {e}")
        return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    target_path = request.args.get('path', '/mnt')
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('No file selected.')
            return redirect(request.url)

        # Accept all file types, skip extension check
        filename = secure_filename(file.filename)
        os.makedirs(target_path, exist_ok=True)
        save_path = os.path.join(target_path, filename)
        file.save(save_path)

        flash(f"File '{filename}' uploaded successfully.")
        log_event(f"File uploaded: {filename} → {target_path}")
        return redirect(url_for('browse') + f'?path={urllib.parse.quote(target_path)}')

    return render_template('upload.html', path=target_path)


@app.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    base_path = request.form['base_path']
    folder_name = request.form['folder_name']
    new_folder_path = os.path.join(base_path, secure_filename(folder_name))
    try:
        os.makedirs(new_folder_path, exist_ok=True)
        flash(f"Folder '{folder_name}' created successfully.")
        log_event(f"Folder created: {new_folder_path}")
    except Exception as e:
        flash(f"Error creating folder: {e}")
    return redirect(url_for('browse') + f'?path={urllib.parse.quote(base_path)}')

@app.route('/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete():
    path = urllib.parse.unquote(request.form.get('path', ''))
    if not os.path.exists(path):
        flash("Path does not exist.")
        return redirect(url_for('index'))
    try:
        move_to_trash(path)
        flash(f"Moved '{os.path.basename(path)}' to trash.")
    except Exception as e:
        flash(f"Error deleting: {e}")
    return redirect(url_for('browse') + f'?path={urllib.parse.quote(os.path.dirname(path))}')

@app.route('/logs')
@login_required
def view_logs():
    logs_by_date = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            for line in f:
                if line.startswith("["):
                    try:
                        timestamp_str = line[1:20]
                        dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        year, month, day = str(dt.year), dt.strftime('%B'), str(dt.day)
                        logs_by_date[year][month][day].append(line.strip())
                    except:
                        continue
    return render_template("log.html", logs_by_date=dict(logs_by_date))

@app.route('/preview')
@login_required
def preview():
    path = urllib.parse.unquote(request.args.get('path', ''))
    if not os.path.exists(path):
        return abort(404)

    filename = os.path.basename(path)
    ext = filename.rsplit('.', 1)[-1].lower()
    image_types = ['jpg', 'jpeg', 'png', 'gif']
    video_types = ['mp4', 'webm', 'mkv', 'mov', 'avi', 'flv', 'wmv', 'mpeg']

    media_type = 'image' if ext in image_types else 'video' if ext in video_types else None
    metadata = None
    video_stream = None

    if media_type == 'video':
        metadata = get_video_metadata(path)
        if metadata:
            for stream in metadata.get("streams", []):
                if stream.get("codec_type") == "video":
                    video_stream = stream
                    break

    return render_template('preview.html',
                           media_type=media_type,
                           path=path,
                           metadata=metadata,
                           video_stream=video_stream)

    
@app.route('/media')
@login_required
def serve_media():
    path = urllib.parse.unquote(request.args.get('path', ''))
    if not os.path.exists(path):
        return abort(404)

    file_size = os.path.getsize(path)
    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(path, as_attachment=False)

    byte1, byte2 = 0, None
    match = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if match:
        groups = match.groups()
        byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    byte2 = byte2 if byte2 is not None else file_size - 1
    length = byte2 - byte1 + 1

    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    response = Response(data, 206, mimetype="video/mp4", direct_passthrough=True)
    response.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{file_size}')
    response.headers.add('Accept-Ranges', 'bytes')
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
