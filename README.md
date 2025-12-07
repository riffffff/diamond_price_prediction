# Diamonds — Dokumentasi Menjalankan Aplikasi

Aplikasi ini terdiri dari:
- Backend API (Flask) untuk prediksi harga diamond
- Frontend UI (Streamlit) untuk input data dan menampilkan hasil

## Struktur Proyek
```
Api/
  app.py
  model_utils.py
  requirements.txt
saved_model/
streamlit_app/
  app.py
```

## Prasyarat
- Python 3.10+ terpasang (`python3 --version`)
- Pip terpasang (`python3 -m pip --version`)
- Port kosong: `5000` (API) dan `8501` (Streamlit)

Opsional tapi disarankan: virtual environment (venv)

```bash
# Buat dan aktifkan venv (opsional)
python3 -m venv .venv
source .venv/bin/activate
```

## 1) Instal Dependensi
Instal seluruh paket untuk API dan Streamlit.

```bash
# Dari root repo
python3 -m pip install -r Api/requirements.txt
python3 -m pip install streamlit
```

Catatan: Jika muncul peringatan `InconsistentVersionWarning` (scikit-learn), Anda bisa menyamakan versi saat model dibuat, misal:

```bash
python3 -m pip install "scikit-learn==1.6.1"
```

## 2) Jalankan Backend (Flask API)
Jalankan server Flask pada port 5000.

```bash
cd Api
python3 app.py
```

Jika sukses, endpoint akan tersedia di `http://127.0.0.1:5000/predict`.

### Tes Cepat Endpoint
Gunakan `curl` untuk mencoba prediksi:

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "carat": 1.0,
    "cut": "Premium",
    "color": "D",
    "clarity": "IF",
    "table": 55,
    "x": 6.5,
    "y": 6.5,
    "z": 4.0
  }'
```

Respon contoh:
```json
{
  "input": { ... },
  "predicted_price": 2.99
}
```

## 3) Jalankan Frontend (Streamlit)
Di terminal baru, jalankan UI Streamlit pada port 8501.

```bash
cd streamlit_app
python3 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Buka di browser: `http://localhost:8501`

UI akan mengirim request ke API lokal `http://127.0.0.1:5000/predict`.

## Pengaturan URL API (opsional)
Jika API berjalan di host/port lain, ubah URL pada file berikut:
- `streamlit_app/app.py` → cari baris `requests.post("http://127.0.0.1:5000/predict", ...)` dan sesuaikan.

## Troubleshooting
- "command not found: streamlit"
  - Jalankan dengan modul Python:
    ```bash
    python3 -m streamlit run app.py
    ```
- Peringatan scikit-learn saat load model
  - Samakan versi scikit-learn seperti saat model dipickle, atau retrain/simpan ulang model.
- Port sudah terpakai
  - Ganti port: di `Api/app.py` ubah argumen `port=...`, dan pada Streamlit ganti `--server.port`.
- Tidak ada folder `saved_model` / file `model.pkl`
  - Pastikan model tersimpan di `saved_model/` dengan nama `model.pkl` dan `features.pkl` seperti yang digunakan di `Api/app.py`.

## Ringkas: Perintah Satu Layar
```bash
# 1) Instal
python3 -m pip install -r Api/requirements.txt && python3 -m pip install streamlit

# 2) Jalankan API (terminal 1)
(cd Api && python3 app.py)

# 3) Jalankan UI (terminal 2)
(cd streamlit_app && python3 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0)
```

## Deployment

Proyek ini sudah siap untuk deployment menggunakan Docker dan dapat di-deploy ke berbagai platform cloud.

### File Deployment yang Tersedia
- `Api/Dockerfile` - Container untuk Flask API
- `streamlit_app/Dockerfile` - Container untuk Streamlit UI
- `docker-compose.yml` - Orchestration untuk menjalankan kedua service
- `streamlit_app/requirements.txt` - Dependencies untuk Streamlit
- `Api/requirements.txt` - Dependencies untuk Flask API (sudah termasuk flask-cors)

### Tes Lokal dengan Docker

**Prasyarat:** Docker dan Docker Compose harus terinstal.

```bash
# Dari root repo
docker-compose up --build
```

Akses aplikasi:
- API: `http://localhost:5000`
- UI: `http://localhost:8501`

Untuk stop:
```bash
docker-compose down
```

### Deploy ke Render (Rekomendasi - Free Tier)

1. **Persiapan:**
   - Daftar di [render.com](https://render.com)
   - Push kode ke GitHub repository

2. **Deploy Flask API:**
   - Di Render dashboard, klik "New +" → "Web Service"
   - Connect GitHub repo Anda
   - Settings:
     - Name: `diamond-api` (atau nama lain)
     - Root Directory: `Api`
     - Environment: `Docker`
     - Instance Type: `Free`
   - Klik "Create Web Service"
   - Salin URL API yang diberikan (misal: `https://diamond-api.onrender.com`)

3. **Deploy Streamlit UI:**
   - Klik "New +" → "Web Service" lagi
   - Connect repo yang sama
   - Settings:
     - Name: `diamond-ui`
     - Root Directory: `streamlit_app`
     - Environment: `Docker`
     - Instance Type: `Free`
     - Environment Variables: Tambahkan `API_URL=https://diamond-api.onrender.com/predict`
   - Klik "Create Web Service"
   - Akses URL Streamlit yang diberikan

**Catatan:** Free tier Render akan sleep setelah 15 menit tidak aktif. Request pertama akan lambat saat wake up.

### Deploy ke Railway

1. **Persiapan:**
   - Daftar di [railway.app](https://railway.app)
   - Install Railway CLI (opsional)

2. **Deploy:**
   - Di Railway dashboard, klik "New Project" → "Deploy from GitHub repo"
   - Pilih repository Anda
   - Railway akan auto-detect Dockerfile
   - Buat 2 services:
     - Service 1: Root directory `Api/`, port 5000
     - Service 2: Root directory `streamlit_app/`, port 8501
   - Set environment variable `API_URL` di Streamlit service

3. **Generate Domain:**
   - Klik service → Settings → Generate Domain
   - Update `API_URL` dengan domain API yang sudah dibuat

### Deploy ke Heroku

**Prasyarat:** Heroku CLI terinstal dan sudah login.

```bash
# Deploy API
cd Api
heroku create diamond-api-yourname
heroku container:push web -a diamond-api-yourname
heroku container:release web -a diamond-api-yourname

# Deploy Streamlit
cd ../streamlit_app
heroku create diamond-ui-yourname
heroku config:set API_URL=https://diamond-api-yourname.herokuapp.com/predict -a diamond-ui-yourname
heroku container:push web -a diamond-ui-yourname
heroku container:release web -a diamond-ui-yourname
```

### Deploy ke VPS (DigitalOcean, AWS EC2, dll)

1. **Setup VPS:**
   ```bash
   # Install Docker dan Docker Compose
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **Clone dan Deploy:**
   ```bash
   git clone <your-repo-url>
   cd Diamonds
   sudo docker-compose up -d
   ```

3. **Setup Nginx (opsional untuk custom domain):**
   ```bash
   sudo apt install nginx -y
   # Konfigurasi reverse proxy di /etc/nginx/sites-available/
   ```

4. **SSL dengan Let's Encrypt (opsional):**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d yourdomain.com
   ```

### Environment Variables untuk Production

Saat deploy, pastikan set environment variable berikut:

**Untuk Streamlit service:**
- `API_URL` - URL endpoint API (misal: `https://your-api.com/predict`)
- `STREAMLIT_SERVER_HEADLESS=true` (otomatis di docker-compose)

**Untuk Flask API:**
- `FLASK_ENV=production` (otomatis di docker-compose)

### Troubleshooting Deployment

- **Container gagal start:**
  - Cek logs: `docker-compose logs api` atau `docker-compose logs streamlit`
  - Pastikan semua dependencies ada di requirements.txt

- **Model tidak ditemukan:**
  - Pastikan folder `saved_model/` di-commit ke repo
  - Atau upload model terpisah dan mount sebagai volume

- **CORS error:**
  - flask-cors sudah ditambahkan di `Api/requirements.txt`
  - Pastikan `CORS(app)` ada di `Api/app.py`

- **Streamlit tidak bisa connect ke API:**
  - Cek environment variable `API_URL` sudah benar
  - Untuk docker-compose lokal, gunakan `http://api:5000/predict` (service name)
  - Untuk cloud deployment, gunakan full URL publik

Selesai. Jika butuh, saya bisa menambahkan skrip start otomatis atau Makefile untuk menjalankan keduanya sekaligus.
