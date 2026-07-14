const TUGAS_PIKET = [
  "Menyapu lantai &amp; membuang sampah",
  "Merapikan kabel &amp; Menyapu lantai",
  "Merapikan meja, kursi taruna &amp; mematikan AC/lampu",
  "<code>Danpiket</code> — Lapor ke Ketua Kelas setelah selesai",
];

const KELAS = [
  {
    nama: "III RKS A",
    chatIdEnv: "CHAT_ID_KELAS_1",
    jadwal: {
      Monday: ["Arsa", "Arma", "Dewi", "Nuha"],
      Tuesday: ["Agata", "Fredel", "Dini", "Hanif"],
      Wednesday: ["Sandra", "Basith", "Fadly", "Abdus"],
      Thursday: ["Crypto", "Afiq", "Reo", "Minto"],
      Friday: ["Nathan", "Waldi", "Elvi", "Keyza"],
    },
  },
  {
    nama: "I RSK",
    chatIdEnv: "CHAT_ID_KELAS_2",
    jadwal: {
      Monday: ["Bunga", "Qisya"],
      Tuesday: ["Fasa", "Lasro"],
      Wednesday: ["Naila", "Edmund"],
      Thursday: ["Maretta", "Sausan"],
      Friday: ["Zalia", "Voleta"],
    },
  },
];

const NAMA_HARI = {
  Monday: "Senin",
  Tuesday: "Selasa",
  Wednesday: "Rabu",
  Thursday: "Kamis",
  Friday: "Jumat",
  Saturday: "Sabtu",
  Sunday: "Minggu",
};

function getHariJakarta() {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Jakarta",
    weekday: "long",
  }).format(new Date());
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function buatDaftarTugas(namaPiket, mode) {
  return TUGAS_PIKET.map((tugas, index) => {
    // Jika hanya dua petugas, keempat tugas dibagi bergantian.
    const nama = namaPiket[index % namaPiket.length].toUpperCase();
    const pemisah = mode === "pagi" ? "➜" : "—";

    return `• <b>${escapeHtml(nama)}</b> ${pemisah} ${tugas}`;
  }).join("\n");
}

function buatPesanPagi(hari, namaPiket) {
  const hariIndonesia = NAMA_HARI[hari];

  return [
    "🪭<b>DANPIKET</b>",
    "🧹 <b>REMINDER PIKET KELAS</b>",
    "━━━━━━━━━━━━━━━━━━━━",
    `📅 Hari: <b>${hariIndonesia}</b>`,
    "",
    "👥 Petugas piket hari ini:",
    "",
    buatDaftarTugas(namaPiket, "pagi"),
    "",
    "<i>Mohon piket sebelum pelajaran dimulai.</i> 🙏",
  ].join("\n");
}

function buatPesanSiang(hari, namaPiket) {
  const hariIndonesia = NAMA_HARI[hari];

  // Tugas terakhir dibuat seperti pesan siang pada screenshot.
  const tugasSiang = [
  "Menyapu lantai &amp; membuang sampah",
  "Merapikan kabel &amp; Menyapu lantai",
  "Merapikan meja, kursi taruna &amp; mematikan AC/lampu",
  "Pastikan standar 100% terpenuhi sebelum lapor ke Ketua Kelas.",
];

  const daftarTugas = tugasSiang
    .map((tugas, index) => {
      const nama = namaPiket[index % namaPiket.length].toUpperCase();
      return `• <b>${escapeHtml(nama)}</b> — ${tugas}`;
    })
    .join("\n");

  return [
    "🪭<b>DANPIKET</b>",
    "🧹 <b>REMINDER PIKET KELAS</b>",
    "━━━━━━━━━━━━━━━━━━━━",
    `📅 Hari: <b>${hariIndonesia}</b>`,
    "",
    "👥 Jam kuliah hampir selesai, Ini saatnya:",
    "",
    daftarTugas,
    "",
    "<i>Terima kasih atas kesadaran dan tanggung jawabnya.</i> 🙏",
  ].join("\n");
}

async function kirimTelegram(env, chatId, pesan) {
  const response = await fetch(
    `https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        chat_id: chatId,
        text: pesan,
        parse_mode: "HTML",
        disable_web_page_preview: true,
      }),
    }
  );

  const result = await response.json();

  if (!response.ok || !result.ok) {
    throw new Error(
      `Telegram gagal mengirim ke ${chatId}: ${JSON.stringify(result)}`
    );
  }

  return result;
}

async function kirimReminder(env, mode, hari = getHariJakarta()) {
  if (!KELAS[0].jadwal[hari]) {
    return {
      skipped: true,
      reason: `Tidak ada jadwal piket pada hari ${hari}`,
    };
  }

  const hasil = await Promise.allSettled(
    KELAS.map(async (kelas) => {
      const chatId = env[kelas.chatIdEnv];

      if (!chatId) {
        throw new Error(`Secret ${kelas.chatIdEnv} belum diatur`);
      }

      const namaPiket = kelas.jadwal[hari];

      const pesan =
        mode === "pagi"
          ? buatPesanPagi(hari, namaPiket)
          : buatPesanSiang(hari, namaPiket);

      await kirimTelegram(env, chatId, pesan);

      return {
        kelas: kelas.nama,
        chatId,
      };
    })
  );

  const sukses = hasil
    .filter((item) => item.status === "fulfilled")
    .map((item) => item.value);

  const gagal = hasil
    .filter((item) => item.status === "rejected")
    .map((item) => item.reason?.message || String(item.reason));

  if (gagal.length > 0) {
    throw new Error(gagal.join("\n"));
  }

  return {
    sent: sukses.length,
    kelas: sukses,
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/") {
      return Response.json({
        ok: true,
        service: "piket-bot",
        kelas: KELAS.map((item) => item.nama),
      });
    }

    if (url.pathname === "/test/pagi" || url.pathname === "/test/siang") {
      const authorization = request.headers.get("authorization");

      if (!env.TEST_KEY || authorization !== `Bearer ${env.TEST_KEY}`) {
        return new Response("Unauthorized", { status: 401 });
      }

      const mode = url.pathname.endsWith("/pagi") ? "pagi" : "siang";
      const hari = url.searchParams.get("hari") || getHariJakarta();

      if (!NAMA_HARI[hari]) {
        return Response.json(
          {
            ok: false,
            error:
              "Parameter hari harus Monday, Tuesday, Wednesday, Thursday, atau Friday",
          },
          { status: 400 }
        );
      }

      try {
        const result = await kirimReminder(env, mode, hari);

        return Response.json({
          ok: true,
          mode,
          hari,
          result,
        });
      } catch (error) {
        return Response.json(
          {
            ok: false,
            error: error.message,
          },
          { status: 500 }
        );
      }
    }

    return new Response("Not found", { status: 404 });
  },

  async scheduled(event, env, ctx) {
    // 00:40 UTC = 07:40 WIB
    // 08:15 UTC = 15:15 WIB
    const mode = event.cron === "40 0 * * MON-FRI" ? "pagi" : "siang";

    ctx.waitUntil(kirimReminder(env, mode));
  },
};
