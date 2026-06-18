from __future__ import annotations

import os
import socket
import secrets
import logging
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    request,
    Response,
    render_template_string,
    send_from_directory,
    abort,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename
from waitress import serve


APP_DIR = Path(__file__).parent.resolve()
UPLOAD_DIR = APP_DIR

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".heic", ".heif",
    ".mov", ".mp4", ".m4v",
    ".avi", ".mkv"
}

MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "4096"))
UPLOAD_PASSWORD = os.environ.get("UPLOAD_PASSWORD", "").strip()
VERBOSE_LOG = os.environ.get("VERBOSE_LOG", "1").strip() == "1"

if not UPLOAD_PASSWORD:
    raise RuntimeError(
        "UPLOAD_PASSWORD ayarlı değil. baslat.bat içinden çalıştırın "
        "veya ortam değişkeni olarak UPLOAD_PASSWORD verin."
    )

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


# -----------------------------
# LOG AYARLARI
# -----------------------------

logging.basicConfig(
    level=logging.INFO if VERBOSE_LOG else logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("iphone-upload")


def log(message: str):
    if VERBOSE_LOG:
        logger.info(message)


HTML = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <title>Güvenli Fotoğraf / Video Upload</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: system-ui, Arial, sans-serif;
            max-width: 900px;
            margin: 24px auto;
            padding: 16px;
            background: #f3f4f6;
            color: #111827;
        }

        .card {
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }

        h1 {
            font-size: 25px;
            margin-top: 0;
            margin-bottom: 8px;
        }

        h2 {
            font-size: 19px;
            margin-top: 0;
        }

        input, button {
            font-size: 16px;
        }

        input[type="file"] {
            width: 100%;
            padding: 16px;
            box-sizing: border-box;
            background: #f9fafb;
            border: 2px dashed #9ca3af;
            border-radius: 12px;
            margin-top: 10px;
        }

        .upload-button {
            width: 100%;
            margin-top: 18px;
            padding: 16px 20px;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            background: #2563eb;
            color: white;
            font-size: 18px;
            font-weight: 700;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
        }

        .upload-button:hover {
            background: #1d4ed8;
        }

        .upload-button:active {
            background: #1e40af;
            transform: scale(0.99);
        }

        .muted {
            color: #4b5563;
            font-size: 14px;
            line-height: 1.5;
        }

        .ok {
            background: #ecfdf5;
            border: 1px solid #86efac;
            color: #14532d;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 12px;
            font-weight: 600;
        }

        .err {
            background: #fef2f2;
            border: 1px solid #fca5a5;
            color: #7f1d1d;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 12px;
            font-weight: 600;
        }

        .file-count {
            margin-top: 12px;
            padding: 12px;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 10px;
            color: #1e3a8a;
            font-weight: 700;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th, td {
            border-bottom: 1px solid #e5e7eb;
            padding: 9px;
            text-align: left;
            font-size: 14px;
        }

        th {
            background: #f9fafb;
        }

        a {
            word-break: break-all;
            color: #2563eb;
            font-weight: 600;
        }

        .status-box {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            padding: 12px;
            border-radius: 10px;
            margin-top: 12px;
        }
    </style>
</head>

<body>
    <div class="card">
        <h1>Güvenli Fotoğraf / Video Upload</h1>
        <p class="muted">
            Kayıt klasörü: {{ upload_dir }}<br>
            Maksimum toplam yükleme: {{ max_mb }} MB<br>
            İzin verilen türler: {{ extensions }}
        </p>

        <div class="status-box">
            <b>Durum:</b> Sunucu çalışıyor.
        </div>
    </div>

    {% if message %}
        <div class="{{ message_class }}">{{ message }}</div>
    {% endif %}

    <div class="card">
        <h2>Dosya Yükle</h2>

        <form method="post" action="/upload" enctype="multipart/form-data">
            <input
                id="fileInput"
                type="file"
                name="files"
                multiple
                accept="image/*,video/*,.jpg,.jpeg,.png,.gif,.webp,.heic,.heif,.mov,.mp4,.m4v,.avi,.mkv"
            >

            <div id="fileCount" class="file-count">
                Henüz dosya seçilmedi.
            </div>

            <button class="upload-button" type="submit">
                SEÇİLENLERİ YÜKLE
            </button>
        </form>

        <p class="muted">
            iPhone’da Fotoğraf Arşivi’ni açıp birden fazla fotoğraf/video seçebilirsin.
            Yükleme başladıktan sonra terminal ekranında hareketleri göreceksin.
        </p>
    </div>

    <div class="card">
        <h2>Klasör İçeriği</h2>

        {% if files %}
            <table>
                <thead>
                    <tr>
                        <th>Dosya</th>
                        <th>Boyut</th>
                        <th>Tarih</th>
                    </tr>
                </thead>

                <tbody>
                    {% for file in files %}
                        <tr>
                            <td>
                                <a href="/files/{{ file.name }}" target="_blank">
                                    {{ file.name }}
                                </a>
                            </td>
                            <td>{{ file.size }}</td>
                            <td>{{ file.modified }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p class="muted">Klasörde henüz dosya yok.</p>
        {% endif %}
    </div>

    <script>
        const fileInput = document.getElementById("fileInput");
        const fileCount = document.getElementById("fileCount");

        fileInput.addEventListener("change", function () {
            const count = fileInput.files.length;

            if (count === 0) {
                fileCount.textContent = "Henüz dosya seçilmedi.";
            } else {
                let totalSize = 0;

                for (const file of fileInput.files) {
                    totalSize += file.size;
                }

                const sizeMb = totalSize / 1024 / 1024;

                fileCount.textContent =
                    count + " dosya seçildi. Yaklaşık toplam boyut: " +
                    sizeMb.toFixed(1) + " MB";
            }
        });
    </script>
</body>
</html>
"""


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr or "unknown"
        auth = request.authorization

        if not auth or not secrets.compare_digest(auth.password, UPLOAD_PASSWORD):
            log(f"Yetkisiz erişim denemesi | IP: {client_ip} | Path: {request.path}")
            return Response(
                "Yetkisiz erişim",
                401,
                {"WWW-Authenticate": 'Basic realm="Upload Area"'},
            )

        return func(*args, **kwargs)

    return wrapper


@app.before_request
def before_request_log():
    client_ip = request.remote_addr or "unknown"
    log(f"İstek geldi | IP: {client_ip} | Method: {request.method} | Path: {request.path}")


@app.after_request
def after_request_log(response):
    client_ip = request.remote_addr or "unknown"
    log(
        f"İstek tamamlandı | IP: {client_ip} | "
        f"Path: {request.path} | Status: {response.status_code}"
    )
    return response


def allowed_file(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def human_size(size_bytes: int) -> str:
    size = float(size_bytes)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024

    return f"{size:.1f} PB"


def safe_unique_filename(original_name: str) -> str:
    safe_name = secure_filename(original_name)

    if not safe_name:
        safe_name = "upload"

    suffix = Path(safe_name).suffix.lower()
    stem = Path(safe_name).stem

    if not suffix:
        suffix = ".bin"

    candidate = f"{stem}{suffix}"
    target = UPLOAD_DIR / candidate

    counter = 1
    while target.exists():
        candidate = f"{stem}_{counter}{suffix}"
        target = UPLOAD_DIR / candidate
        counter += 1

    return candidate


def is_inside_upload_dir(path: Path) -> bool:
    try:
        path.resolve().relative_to(UPLOAD_DIR.resolve())
        return True
    except ValueError:
        return False


def list_uploaded_files():
    hidden_files = {
        "app.py",
        "requirements.txt",
        "baslat.bat",
        "README.txt",
    }

    result = []

    for path in UPLOAD_DIR.iterdir():
        if not path.is_file():
            continue

        if path.name in hidden_files:
            continue

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        stat = path.stat()

        result.append({
            "name": path.name,
            "size": human_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "mtime": stat.st_mtime,
        })

    result.sort(key=lambda x: x["mtime"], reverse=True)

    for item in result:
        item.pop("mtime", None)

    return result


@app.route("/")
@require_auth
def index():
    files = list_uploaded_files()
    log(f"Ana sayfa gösterildi | Listelenen dosya sayısı: {len(files)}")

    message = request.args.get("message", "")
    message_class = request.args.get("message_class", "ok")

    return render_template_string(
        HTML,
        files=files,
        upload_dir=str(UPLOAD_DIR),
        extensions=", ".join(sorted(ALLOWED_EXTENSIONS)),
        max_mb=MAX_UPLOAD_MB,
        message=message,
        message_class=message_class,
    )


@app.route("/upload", methods=["POST"])
@require_auth
def upload():
    client_ip = request.remote_addr or "unknown"
    uploaded_files = request.files.getlist("files")

    log("--------------------------------------------------")
    log(f"UPLOAD BAŞLADI | IP: {client_ip}")
    log(f"Gelen dosya sayısı: {len(uploaded_files)}")

    if not uploaded_files:
        log("Upload iptal: Dosya seçilmedi.")
        return redirect(url_for(
            "index",
            message="Dosya seçilmedi.",
            message_class="err",
        ))

    saved_count = 0
    rejected_files = []
    total_saved_bytes = 0

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        original_name = uploaded_file.filename or ""

        if not original_name:
            log(f"{index}. dosya boş isimli geldi, atlandı.")
            continue

        log(f"{index}. dosya alındı: {original_name}")

        if not allowed_file(original_name):
            log(f"REDDEDİLDİ | İzin verilmeyen tür: {original_name}")
            rejected_files.append(original_name)
            continue

        filename = safe_unique_filename(original_name)
        destination = (UPLOAD_DIR / filename).resolve()

        if not is_inside_upload_dir(destination):
            log(f"GÜVENLİK ENGELİ | Klasör dışına yazma denemesi: {destination}")
            abort(400)

        uploaded_file.save(destination)

        file_size = destination.stat().st_size
        total_saved_bytes += file_size
        saved_count += 1

        log(
            f"KAYDEDİLDİ | {filename} | "
            f"Boyut: {human_size(file_size)} | "
            f"Konum: {destination}"
        )

    log(
        f"UPLOAD BİTTİ | Kaydedilen: {saved_count} | "
        f"Reddedilen: {len(rejected_files)} | "
        f"Toplam: {human_size(total_saved_bytes)}"
    )
    log("--------------------------------------------------")

    if rejected_files:
        message = (
            f"{saved_count} dosya yüklendi. "
            f"{len(rejected_files)} dosya türü nedeniyle reddedildi."
        )

        return redirect(url_for(
            "index",
            message=message,
            message_class="err",
        ))

    return redirect(url_for(
        "index",
        message=f"{saved_count} dosya başarıyla yüklendi. Toplam: {human_size(total_saved_bytes)}",
        message_class="ok",
    ))


@app.route("/files/<path:filename>")
@require_auth
def get_file(filename):
    requested = (UPLOAD_DIR / filename).resolve()

    if not is_inside_upload_dir(requested):
        log(f"GÜVENLİK ENGELİ | Klasör dışı okuma: {requested}")
        abort(403)

    if not requested.exists() or not requested.is_file():
        log(f"Dosya bulunamadı: {requested}")
        abort(404)

    if requested.suffix.lower() not in ALLOWED_EXTENSIONS:
        log(f"Dosya gösterimi reddedildi: {requested}")
        abort(403)

    log(f"Dosya görüntülendi/indirildi: {requested.name}")

    return send_from_directory(
        UPLOAD_DIR,
        requested.name,
        as_attachment=False,
    )


@app.errorhandler(413)
def too_large(_):
    log(f"Yükleme çok büyük. Limit: {MAX_UPLOAD_MB} MB")
    return redirect(url_for(
        "index",
        message=f"Yükleme çok büyük. Limit: {MAX_UPLOAD_MB} MB",
        message_class="err",
    ))


@app.errorhandler(Exception)
def handle_exception(error):
    logger.exception(f"Beklenmeyen hata: {error}")
    return "Sunucuda hata oluştu. Terminal ekranındaki loglara bakın.", 500


def get_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        sock.close()


if __name__ == "__main__":
    ip = get_local_ip()

    print()
    print("==================================================")
    print(" GÜVENLİ IPHONE FOTOĞRAF / VİDEO UPLOAD SUNUCUSU")
    print("==================================================")
    print()
    print(f"Kayıt klasörü: {UPLOAD_DIR}")
    print(f"Maksimum upload: {MAX_UPLOAD_MB} MB")
    print(f"Verbose log: {'AÇIK' if VERBOSE_LOG else 'KAPALI'}")
    print()
    print(f"Bilgisayardan: http://127.0.0.1:5000")
    print(f"iPhone'dan:    http://{ip}:5000")
    print()
    print("Kullanıcı adı boş bırakılabilir.")
    print("Parola: baslat.bat içindeki UPLOAD_PASSWORD değeri.")
    print()
    print("Sunucu hareketleri bu ekranda görünecek.")
    print("Kapatmak için CTRL + C yapın.")
    print("==================================================")
    print()

    serve(app, host="0.0.0.0", port=5000, threads=8)