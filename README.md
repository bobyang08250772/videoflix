

# Videoflix Project 

VideoFlix is a Netflix-inspired video streaming platform that delivers high-quality video content with adaptive streaming using HLS (HTTP Live Streaming). Built with Django on the backend and Angular on the frontend, it supports user authentication using DRF-JWT-AUTHENTICATION, dynamic video resolution switching, and efficient content delivery via segmented streaming.

---

# Features
🔐 Authentication System
Secure login, registration, and token-based authentication using JWT with refresh/access tokens.

🎞️ HLS Video Streaming
Adaptive streaming based on internet speed and resolution preference (e.g., 1080p, 720p, 480p).

📂 Segmented Streaming Support
Videos are split into .ts segments and served efficiently using HLS standards.

🧾 Playlist Indexing
Dynamically generated .m3u8 playlists for each resolution level.

🎛️ Admin Video Management
Upload and manage videos through Django admin or custom endpoints.

---

## 📦 Prerequisites

- Python 3.13+
- pip installed
- (Optional but recommended) Python virtual environment (`venv`)

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/bobyang08250772/videoflix_backend.git
```

### 2. Frontend
Notice Frontend and Backend should be runing seperately.
Go to frontend folder, open index.html in Live Server, making sue using 127.0.0.1 instead of localhost to access due to cross-origin issues.

### 3. Backend

```bash
cd backend
```

### 3.1.Make sure docker is installed 
```bash
docker-compose up --build
```


