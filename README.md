# 🗂️ Vaultaris Smart File Manager (Flask App)

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

## 📸 UI Screenshots

**🔐 Login Page**  
![Login](Screenshots/Screenshot%20From%202025-06-11%2022-20-40.png)

**💾 Dashboard - Mounted Devices**  
![Dashboard](Screenshots/Screenshot%20From%202025-06-11%2022-30-32.png)

**🗂 Browse Folders**  
![Browse](Screenshots/Screenshot%20From%202025-06-11%2022-34-46.png)

**📁 Folder Contents**  
![Folder View](Screenshots/Screenshot%20From%202025-06-11%2022-34-55.png)

**📤 Upload File Interface**  
![Upload](Screenshots/Screenshot%20From%202025-06-11%2022-35-05.png)

---

## ✨ Author

**Rajesh Kumar Jogi**  
---

## 🛡 License

MIT License - free to use and modify.
