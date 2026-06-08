import os
import sys
from datetime import datetime
import requests

# ============================================================
# KONFIGURASI
# ============================================================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

TUGAS_PIKET = [
    "Menyapu lantai & membuang sampah",
    "Merapikan lemari & Menyapu lantai",  # Tugas kedua sesuai kodemu
    "Merapikan kursi taruna & mematikan AC/lampu",
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
                f"• *{nama.upper()}* ➔ Danpiket — Menghapus papan tulis & merapikan meja dosen\n"
                f"                         Lapor ke Ketua Kelas setelah selesai"
            )
    daftar = "\n".join(baris)

    return (
        f"🧹 *REMINDER PIKET KELAS — {hari_id.upper()}*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Hari ini, kebersihan ruang kelas adalah tanggung jawab:\n\n"
        f"{daftar}\n\n"
        f"_Taruna yang namanya diatas menentukan ke still-an kelas ini 🙏_"
    )


def format_siang(hari_id: str, petugas: list) -> str:
    """Siang: execution trigger + accountability activation."""
    anggota = [nama.upper() for nama in petugas[:-1]]
    DANPIKET = petugas[-1].upper()
    anggota_str = ", ".join(anggota)

    return (
        f"🪭 *EKSEKUSI PIKET — {hari_id.upper()}*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Jam kuliah hampir selesai. Ini saatnya:\n\n"
        f"• *{anggota_str}* — Laksanakan tugas masing-masing sekarang.\n"
        f"• *{DANPIKET}* — Pastikan standar 100% terpenuhi sebelum lapor ke Ketua Kelas.\n\n"
        f"_Terima kasih atas kesadaran dan tanggung jawabnya 🙏🙏_"
    )


# ============================================================
# FUNGSI UTAMA
# ============================================================


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def kirim_pesan(teks: str):
    url = f"https://api.telegram.org/bot8484920881:AAHWDpT1ezHuDHos8mt_ZYmIvkSPXML0MiA/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": teks, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if data.get("ok"):
            print(f"[{now()}] Pesan berhasil dikirim.")
        else:
            print(f"[{now()}] ERROR: {data.get('description')}")
    except requests.exceptions.RequestException as e:
        print(f"[{now()}] Koneksi gagal: {e}")


def kirim_reminder_piket(mode: str):
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

    kirim_pesan(pesan)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Ambil argumen: python piket_bot.py pagi  ATAU  python piket_bot.py siang
    mode = sys.argv[1] if len(sys.argv) > 1 else "pagi"
    print(f"[{now()}] Mode: {mode}")
    kirim_reminder_piket(mode)
