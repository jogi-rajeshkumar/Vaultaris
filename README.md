# 🗂️ Vaultaris USB File Manager (Flask App)

Vaultaris is a secure and responsive Flask web application that allows users to:
- Detect, mount, browse, upload, download, preview, and delete files on removable USB drives
- View system activity logs
- Support both image and video previews with metadata
- Provide admin/viewer login-based access control

> Designed for Raspberry Pi, Linux-based workstations, or kiosks managing local drives.

---

## 🚀 Features

✅ USB device auto-mounting  
✅ Browse files/folders with a clean UI  
✅ Upload new files via drag & drop or file picker  
✅ Image and video previews with metadata  
✅ Create folders, delete files (admin only)  
✅ Responsive layout for mobile/tablet use  
✅ System log viewer (date-grouped entries)

---

## 📁 Project Structure

```
vaultaris/
├── templates/
│   ├── login.html
│   ├── index.html
│   ├── browse.html
│   ├── upload.html
│   ├── log.html
│   └── preview.html
├── static/           # (Optional if needed later)
├── logs/
│   └── activity.log
├── app.py
├── requirements.txt
└── README.md
```

---

## 🔐 Users & Roles

| Username         | Password     | Role    |
|------------------|--------------|---------|
| Adminuser        | Adminonly    | admin   |
| ViewerUser       | viewonly     | viewer  |

- `admin`: full access including delete
- `viewer`: view and upload only

---

## ⚙️ Requirements

**Python packages:**

```
Flask==2.3.3
Werkzeug==2.3.7
gunicorn==21.2.0
```

**System packages (Linux):**

```bash
sudo apt install ffmpeg util-linux
```

- `ffmpeg` – for video metadata (`ffprobe`)
- `util-linux` – for USB mount tools (`lsblk`, `mount`, `umount`)

---

## 🧪 Setup & Run

### 1. Clone this repository

```bash
git clone https://github.com/yourname/vaultaris.git
cd vaultaris
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Flask app

```bash
python app.py
```

The app will be available at:

```
http://localhost:5000
```
---



## 🔄 Routes Overview

| URL                  | Method | Description                  |
|-----------------------|--------|------------------------------|
| `/`                  | GET/POST | Login page                  |
| `/dashboard`         | GET    | Dashboard with drives       |
| `/mount`             | POST   | Mount a device              |
| `/browse?path=...`   | GET    | Browse files                |
| `/upload?path=...`   | GET/POST | Upload file to folder     |
| `/create_folder`     | POST   | Create a new folder         |
| `/delete`            | POST   | Move file to `.trash`       |
| `/logs`              | GET    | View structured logs        |
| `/preview?path=...`  | GET    | Preview image or video      |
| `/media?path=...`    | GET    | Serve media with byte range |

---

## 📦 Deployment with Gunicorn

For production deployment (optional):

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 👨‍💻 Developer Notes

- Logs are stored in: `logs/activity.log`
- Trashed files are moved to `.trash/` in the same directory
- Previews support: JPG, PNG, MP4, WebM, MKV, etc.

---

## ✨ Author

**Rajesh Kumar Jogi**  
---

## 🛡 License

MIT License - free to use and modify.
