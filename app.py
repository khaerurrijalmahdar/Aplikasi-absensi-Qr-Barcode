from flask import Flask, render_template, redirect, url_for
from pyngrok import ngrok
import sqlite3, datetime

app = Flask(__name__)

# ===== Database Setup =====
DB_NAME = "absensi.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS guru (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT,
                    nip TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS absensi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guru_id INTEGER,
                    waktu TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ===== Routes =====
@app.route("/")
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM guru")
    data = c.fetchall()
    conn.close()
    return render_template("admin_dashboard.html", data=data)

@app.route("/guru/<guru_kode>")
def guru_dashboard(guru_kode):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM guru WHERE nip=?", (guru_kode,))
    guru = c.fetchone()
    conn.close()
    if not guru:
        return "Guru tidak ditemukan"
    return render_template("guru_dashboard.html", guru=guru)


@app.route("/absensi/<int:guru_id>")
def absensi(guru_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO absensi (guru_id, waktu) VALUES (?, ?)", (guru_id, waktu))
    conn.commit()
    conn.close()
    return f"✅ Absensi berhasil! Guru ID {guru_id} pada {waktu}"

@app.route("/rekap")
def rekap():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT guru.nama, guru.nip, absensi.waktu
                 FROM absensi 
                 JOIN guru ON absensi.guru_id = guru.id
                 ORDER BY absensi.waktu DESC''')
    data = c.fetchall()
    conn.close()
    return render_template("rekap.html", data=data)

# ===== Run Flask + Ngrok =====
if __name__ == "__main__":
    port = 5000
    public_url = ngrok.connect(port).public_url
    print("🚀 Ngrok Tunnel URL:", public_url)
    app.run(port=port)
