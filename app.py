import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Laporan Wartelsus KPPK", layout="wide", page_icon="📊")

# Header Utama
st.title("📊 Sistem Laporan Laba Rugi Wartelsus KPPK")
st.subheader("Lapas Narkotika Kelas IIA Yogyakarta")
st.markdown("---")

# Sidebar Input Parameter
st.sidebar.header("📝 Input Data Transaksi")

periode_bulan = st.sidebar.text_input("Bulan Laporan", "AGUSTUS")
periode_tahun = st.sidebar.number_input("Tahun Laporan", min_value=2020, max_value=2030, value=2026)
tanggal_laporan = st.sidebar.date_input("Tanggal Laporan")

total_pendapatan = st.sidebar.number_input("Total Pendapatan (Rp)", min_value=0.0, value=59000000.0, step=500000.0)

st.sidebar.subheader("💡 Rincian Biaya Operasional")
pulsa = st.sidebar.number_input("Pulsa Pasca Bayar", min_value=0.0, value=2960000.0)
internet = st.sidebar.number_input("Internet", min_value=0.0, value=1005000.0)
pph = st.sidebar.number_input("PPH 23 (2%)", min_value=0.0, value=1180000.0)
pnbp = st.sidebar.number_input("PNBP", min_value=0.0, value=300000.0)
server = st.sidebar.number_input("Server", min_value=0.0, value=2243110.0)
biaya_lain = st.sidebar.number_input("Biaya Lain-Lain / Ops", min_value=0.0, value=0.0)

# Kalkulasi Otomatis
total_biaya = pulsa + internet + pph + pnbp + server + biaya_lain
laba_bersih = total_pendapatan - total_biaya

# Porsi Laporan 1
porsi_lapas = 0.40 * laba_bersih
porsi_kalapas = 0.10 * laba_bersih
porsi_inkopasindo = 0.10 * laba_bersih
porsi_muffaindo = 0.40 * laba_bersih

shu = 0.325 * porsi_lapas
ops = 0.30 * porsi_lapas
staf = 0.035 * porsi_lapas
pengurus = 0.015 * porsi_lapas

# Porsi Laporan 2
primkopasindo = 0.20 * laba_bersih
muffaindo2 = 0.60 * laba_bersih

def rupiah(val):
    return f"Rp {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# TAMPILAN DASHBOARD
col_a, col_b, col_c = st.columns(3)
col_a.metric("Total Pendapatan", rupiah(total_pendapatan))
col_b.metric("Total Biaya Operasional", rupiah(total_biaya))
col_c.metric("Laba / Pendapatan Bersih", rupiah(laba_bersih))

tab1, tab2 = st.tabs(["📄 Laporan 1 (Wartel Muffaindo)", "📄 Laporan 2 (Jasa Video Call)"])

with tab1:
    st.header(f"LAPORAN LABA RUGI WARTEL MUFFAINDO - PERIODE {periode_bulan.upper()} {periode_tahun}")
    
    st.subheader("1. Rincian Biaya Operasional")
    df_biaya = pd.DataFrame({
        "Komponen Biaya": ["Pulsa Pasca Bayar", "Internet", "PPH 23 (2%)", "PNBP", "Server", "Biaya Lain-Lain", "TOTAL BIAYA OPERASIONAL"],
        "Nominal": [rupiah(pulsa), rupiah(internet), rupiah(pph), rupiah(pnbp), rupiah(server), rupiah(biaya_lain), rupiah(total_biaya)]
    })
    st.table(df_biaya)

    st.subheader("2. Pembagian Hasil Bagi Hasil")
    df_bagihasil1 = pd.DataFrame({
        "Penerima / Komponen": ["40% X Pendapatan Bersih (Lapas)", "10% X Pendapatan Bersih (Ka. Lapas)", "10% X Iuran 10% Untuk Inkopasindo", "40% X Pendapatan Bersih (Muffaindo)"],
        "Jumlah (Rp)": [rupiah(porsi_lapas), rupiah(porsi_kalapas), rupiah(porsi_inkopasindo), rupiah(porsi_muffaindo)]
    })
    st.table(df_bagihasil1)

    st.subheader("3. Pengeluaran Kantor")
    df_kantor = pd.DataFrame({
        "Alokasi Pengeluaran": ["SHU Koperasi", "Operasional Kantor", "Untuk TU, Binadik, Kamtib, Giatja, Staf KPLP, Rupam 1-4 (10 Bagian)", "Untuk Pengurus (4 Pegawai)", "TOTAL PENGELUARAN KANTOR"],
        "Nominal (Rp)": [rupiah(shu), rupiah(ops), f"@ {rupiah(staf)}", f"@ {rupiah(pengurus)}", rupiah(porsi_lapas)]
    })
    st.table(df_kantor)

with tab2:
    st.header(f"LAPORAN LABA RUGI JASA VIDEO CALL - PERIODE {periode_bulan.upper()} {periode_tahun}")
    
    df_lap2 = pd.DataFrame({
        "Keterangan / Komponen Bagi Hasil": [
            "Total Pendapatan",
            "Total Pengeluaran Operasional",
            "LABA BERSIH",
            "Profit Sharing 20% (PRIMKOPASINDO)",
            "Profit Sharing 10% (PENGAWAS UPT)",
            "Profit Sharing 10% (INKOPASINDO)",
            "Profit Sharing 60% (CV. MUFFAINDO)",
            "TOTAL BAGI HASIL"
        ],
        "Nominal (Rp)": [
            rupiah(total_pendapatan),
            rupiah(total_biaya),
            rupiah(laba_bersih),
            rupiah(primkopasindo),
            rupiah(porsi_kalapas),
            rupiah(porsi_inkopasindo),
            rupiah(muffaindo2),
            rupiah(laba_bersih)
        ]
    })
    st.table(df_lap2)
