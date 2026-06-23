import os
import time
from datetime import datetime
import requests
import schedule

# ============================================================
# KONFIGURASI
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

TUGAS_PIKET = [
    "Menyapu lantai & membuang sampah",
    "Merapikan kabel & Menyapu lantai",  # Tugas kedua sesuai kodemu
    "Merapikan meja, kursi taruna & mematikan AC/lampu",
]

JADWAL_PIKET = {
    "Monday": ["ARSA", "ARMA", "DEWI", "NUHA"],
    "Tuesday": ["AGATA", "FREDEL", "DINI", "HANIF"],
    "Wednesday": ["SANDRA", "BASITH", "FADLY", "ABDUS"],
    "Thursday": ["CRYPTO", "AFIQ", "REO", "MINTO"],
    "Friday": ["NATHAN", "WALDI", "ELVI", "KEYZA"],
}

HARI_ID = {
    "Monday": "Senin",
    "Tuesday": "Selasa",
    "Wednesday": "Rabu",
    "Thursday": "Kamis",
    "Friday": "Jumat",
    "Saturday": "Sabtu",
    "Sunday": "Minggu",
}

# ============================================================
# FORMAT PESAN
# ============================================================

def format_pagi(hari_id: str, petugas: list) -> str:
    """Pagi: identity anchor + implementation intention."""
    baris = []
    for i, nama in enumerate(petugas):
        if i < len(TUGAS_PIKET):
            baris.append(f"• *{nama.upper()}* ➔ {TUGAS_PIKET[i]}")
        else:
            # MEMBAGI JADI 2 BARIS: Menggunakan \n dan spasi tak terlihat agar sejajar bawahnya
            baris.append(
                f"• *{nama.upper()}* ➔ Danpiket — Lapor ke Ketua Kelas setelah selesai\n"
            )
    daftar = "\n".join(baris)

    return (
        f"🧹 *REMINDER PIKET KELAS*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📅 Hari: *{hari_id}*\n\n"
        f"👥 Petugas piket hari ini:\n\n"
        f"{daftar}\n\n"
        f"_Mohon piket sebelum pelajaran dimulai. 🙏_"
    )

def format_siang(hari_id: str, petugas: list) -> str:
    anggota  = petugas[:-1]
    DANPIKET = petugas[-1].upper()

    baris_anggota = "\n".join(
        f"• *{nama.upper()}* — {tugas}"
        for nama, tugas in zip(anggota, TUGAS_PIKET)
    )

    return (
        f"🧹 *REMINDER PIKET KELAS*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📅 Hari: *{hari_id}*\n\n"
        f"👥 Jam kuliah hampir selesai, Ini saatnya:\n\n"
        f"{baris_anggota}\n"
        f"• *{DANPIKET}* — Pastikan standar 100% terpenuhi sebelum lapor ke Ketua Kelas.\n\n"
        f"_Terima kasih atas kesadaran dan tanggung jawabnya. 🙏_"
    )

# ============================================================
# FUNGSI UTAMA
# ============================================================

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def kirim_pesan(teks: str):
    if not BOT_TOKEN or not CHAT_ID:
        print(f"[{now()}] ERROR: BOT_TOKEN atau CHAT_ID tidak ditemukan di environment.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": teks, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if data.get("ok"):
            print(f"[{now()}] Pesan berhasil dikirim.")
        else:
            print(f"[{now()}] ERROR API: {data.get('description')}")
    except requests.exceptions.RequestException as e:
        print(f"[{now()}] Koneksi gagal: {e}")

def kirim_reminder_piket(mode: str):
    # Mengambil hari dari server (Railway menggunakan UTC)
    # Karena 00:40 UTC dan 08:15 UTC tidak menyeberang hari dari WIB, harinya tetap akurat.
    hari_en = datetime.now().strftime("%A")
    hari_id = HARI_ID.get(hari_en, hari_en)

    if hari_en not in JADWAL_PIKET:
        print(f"[{now()}] {hari_id} — tidak ada jadwal piket.")
        return

    petugas = JADWAL_PIKET[hari_en]

    if mode == "siang":
        pesan = format_siang(hari_id, petugas)
    else:
        pesan = format_pagi(hari_id, petugas)

    print(f"[{now()}] Mengeksekusi mode {mode} untuk {hari_id}...")
    kirim_pesan(pesan)

# Wrapper function untuk scheduler
def job_pagi():
    kirim_reminder_piket("pagi")

def job_siang():
    kirim_reminder_piket("siang")

# ============================================================
# ENTRY POINT (DAEMON/ALWAYS-ON)
# ============================================================

if __name__ == "__main__":
    print(f"[{now()}] Sistem bot diinisialisasi (Mode Always-On).")
    
    # Jadwal Pagi: 07:40 WIB = 00:40 UTC
    jadwal_pagi_utc = "00:40"
    for hari in [schedule.every().monday, schedule.every().tuesday, 
                 schedule.every().wednesday, schedule.every().thursday, 
                 schedule.every().friday]:
        hari.at(jadwal_pagi_utc).do(job_pagi)

    # Jadwal Siang: 15:15 WIB = 08:15 UTC
    jadwal_siang_utc = "08:15"
    for hari in [schedule.every().monday, schedule.every().tuesday, 
                 schedule.every().wednesday, schedule.every().thursday, 
                 schedule.every().friday]:
        hari.at(jadwal_siang_utc).do(job_siang)

    print(f"[{now()}] Jadwal diaktifkan. Pagi: {jadwal_pagi_utc} UTC, Siang: {jadwal_siang_utc} UTC.")
    
    # Looping abadi agar container tidak mati
    while True:
        schedule.run_pending()
        time.sleep(1)
