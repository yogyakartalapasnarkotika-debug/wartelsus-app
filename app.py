import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
from datetime import datetime

# 1. Konfigurasi Halaman & Styling CSS
st.set_page_config(
    page_title="Sistem Laporan Wartelsus KPPK - Lapas Narkotika Yogyakarta",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 24px;
            border-radius: 10px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .main-header h1 { color: white !important; margin: 0; font-size: 26px; font-weight: 700; }
        .main-header p { color: #e0e0e0 !important; margin: 5px 0 0 0; font-size: 15px; }

        @media print {
            section[data-testid="stSidebar"], 
            .stButton, 
            header, 
            footer, 
            .stTabs [role="tablist"],
            .no-print {
                display: none !important;
            }
            .main .block-container {
                padding: 0 !important;
                margin: 0 !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Helper Format Rupiah
def rupiah(val):
    try:
        val = float(val)
        return f"Rp {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "Rp 0,00"

# 2. Inisialisasi Database SQLite
def init_db():
    conn = sqlite3.connect("wartelsus_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS laporan_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periode_bulan TEXT,
            periode_tahun INTEGER,
            tanggal_laporan TEXT,
            total_pendapatan REAL,
            rincian_biaya TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def simpan_laporan(bulan, tahun, tgl, pendapatan, biaya_df):
    conn = sqlite3.connect("wartelsus_data.db")
    c = conn.cursor()
    biaya_json = biaya_df.to_json(orient="records")
    
    c.execute("SELECT id FROM laporan_db WHERE periode_bulan = ? AND periode_tahun = ?", (bulan, tahun))
    existing = c.fetchone()
    
    if existing:
        c.execute("""
            UPDATE laporan_db 
            SET tanggal_laporan = ?, total_pendapatan = ?, rincian_biaya = ?
            WHERE id = ?
        """, (str(tgl), pendapatan, biaya_json, existing[0]))
    else:
        c.execute("""
            INSERT INTO laporan_db (periode_bulan, periode_tahun, tanggal_laporan, total_pendapatan, rincian_biaya)
            VALUES (?, ?, ?, ?, ?)
        """, (bulan, tahun, str(tgl), pendapatan, biaya_json))
        
    conn.commit()
    conn.close()

def get_daftar_periode():
    conn = sqlite3.connect("wartelsus_data.db")
    df = pd.read_sql_query("SELECT id, periode_bulan, periode_tahun FROM laporan_db ORDER BY periode_tahun DESC, id DESC", conn)
    conn.close()
    return df

def load_laporan(laporan_id):
    conn = sqlite3.connect("wartelsus_data.db")
    c = conn.cursor()
    c.execute("SELECT periode_bulan, periode_tahun, tanggal_laporan, total_pendapatan, rincian_biaya FROM laporan_db WHERE id = ?", (laporan_id,))
    data = c.fetchone()
    conn.close()
    if data:
        bulan, tahun, tgl, pendapatan, biaya_json = data
        biaya_df = pd.read_json(biaya_json)
        return bulan, tahun, datetime.strptime(tgl, "%Y-%m-%d").date(), pendapatan, biaya_df
    return None

# 3. Header Aplikasi
st.markdown("""
    <div class="main-header no-print">
        <h1>📊 Sistem Laporan Laba Rugi Wartelsus KPPK</h1>
        <p>Lapas Narkotika Kelas IIA Yogyakarta — Panel Pengelolaan, Arsip & Formulasi Laporan</p>
    </div>
""", unsafe_allow_html=True)

# 4. Sidebar Input & Modul Arsip
with st.sidebar:
    st.header("📌 Menu Aplikasi")
    mode_aplikasi = st.radio("Pilih Mode:", ["Input Laporan Baru", "Lihat Laporan Bulan Lalu (Arsip)"])
    st.markdown("---")

    if mode_aplikasi == "Input Laporan Baru":
        st.subheader("⚙️ Parameter Laporan Baru")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            bulan_list = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
            periode_bulan = st.selectbox("Bulan", bulan_list, index=8)
        with col_p2:
            periode_tahun = st.number_input("Tahun", min_value=2020, max_value=2030, value=2026)

        tanggal_laporan = st.date_input("Tanggal Cetak Laporan")
        total_pendapatan = st.number_input("Total Pendapatan (Rp)", min_value=0.0, value=59000000.0, step=1000000.0, format="%.2f")

        st.markdown("---")
        st.subheader("💡 Input Rincian Biaya Operasional")

        default_biaya = pd.DataFrame([
            {"Nama Biaya": "PULSA PASCA BAYAR", "Nominal (Rp)": 2960000.0},
            {"Nama Biaya": "INTERNET", "Nominal (Rp)": 1005000.0},
            {"Nama Biaya": "PPH 23 (2%)", "Nominal (Rp)": 1180000.0},
            {"Nama Biaya": "PNBP", "Nominal (Rp)": 300000.0},
            {"Nama Biaya": "SERVER", "Nominal (Rp)": 2243110.0},
        ])

        edited_biaya = st.data_editor(
            default_biaya,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Nama Biaya": st.column_config.TextColumn("Komponen Biaya", required=True),
                "Nominal (Rp)": st.column_config.NumberColumn("Nominal (Rp)", min_value=0, format="%.2f", required=True)
            },
            key="biaya_editor"
        )

        if st.button("💾 Simpan Laporan ke Database", type="primary", use_container_width=True):
            simpan_laporan(periode_bulan, periode_tahun, tanggal_laporan, total_pendapatan, edited_biaya)
            st.success(f"Laporan periode {periode_bulan} {periode_tahun} berhasil disimpan!")

    else:
        st.subheader("📁 Pilih Periode Laporan Lalu")
        df_periode = get_daftar_periode()
        
        if df_periode.empty:
            st.warning("Belum ada data laporan tersimpan.")
            periode_bulan, periode_tahun, tanggal_laporan, total_pendapatan = "SEPTEMBER", 2026, datetime.now().date(), 0.0
            edited_biaya = pd.DataFrame(columns=["Nama Biaya", "Nominal (Rp)"])
        else:
            opsi_periode = {f"{row['periode_bulan']} {row['periode_tahun']}": row['id'] for _, row in df_periode.iterrows()}
            pilihan = st.selectbox("Pilih Periode Arsip:", list(opsi_periode.keys()))
            selected_id = opsi_periode[pilihan]
            
            periode_bulan, periode_tahun, tanggal_laporan, total_pendapatan, edited_biaya = load_laporan(selected_id)
            st.info(f"Menampilkan Data Arsip Periode: **{periode_bulan} {periode_tahun}**")

# 5. Kalkulasi Otomatis
total_biaya = edited_biaya["Nominal (Rp)"].sum() if not edited_biaya.empty else 0.0
laba_bersih = total_pendapatan - total_biaya

porsi_lapas = 0.40 * laba_bersih
porsi_kalapas = 0.10 * laba_bersih
porsi_inkopasindo = 0.10 * laba_bersih
porsi_muffaindo = 0.40 * laba_bersih

shu = 0.325 * porsi_lapas
ops = 0.30 * porsi_lapas
staf = 0.035 * porsi_lapas
pengurus = 0.015 * porsi_lapas

primkopasindo = 0.20 * laba_bersih
muffaindo2 = 0.60 * laba_bersih

# 6. Dashboard Ringkasan
st.markdown('<div class="no-print">', unsafe_allow_html=True)
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Total Pendapatan", rupiah(total_pendapatan))
col_m2.metric("Total Biaya Operasional", rupiah(total_biaya))
col_m3.metric("Laba / Pendapatan Bersih", rupiah(laba_bersih))

st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    st.button("🖨️ Cetak / Simpan PDF", on_click=lambda: components.html("<script>window.parent.print();</script>", height=0))
st.markdown('</div>', unsafe_allow_html=True)

# CSS Template HTML Laporan Resmi
html_style = """
<style>
    body { font-family: 'Arial', sans-serif; background-color: transparent; margin: 0; padding: 0; }
    .report-box { border: 2px solid #000; padding: 20px; background-color: #fff; color: #000; }
    .report-title { text-align: center; font-weight: bold; font-size: 16px; text-transform: uppercase; margin-bottom: 20px; line-height: 1.4; }
    .report-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .report-table th, .report-table td { border: 1px solid #000; padding: 6px 10px; color: #000; }
    .text-right { text-align: right; }
    .text-center { text-align: center; }
    .bold { font-weight: bold; }
    .bg-light { background-color: #f2f2f2; }
</style>
"""

# 7. Tab Tampilan Laporan
tab1, tab2 = st.tabs(["📄 Laporan 1 (Wartel Muffaindo)", "📄 Laporan 2 (Jasa Video Call)"])

with tab1:
    biaya_rows_html = ""
    if not edited_biaya.empty:
        for idx, row in edited_biaya.iterrows():
            biaya_rows_html += f"<tr><td class='text-center'>{idx + 1}</td><td>{row['Nama Biaya']}</td><td class='text-right'>{rupiah(row['Nominal (Rp)'])}</td></tr>"
    
    doc1 = f"""
    <!DOCTYPE html>
    <html>
    <head>{html_style}</head>
    <body>
        <div class="report-box">
            <div class="report-title">
                LAPORAN LABA RUGI WARTEL MUFFAINDO<br>
                LAPAS NARKOTIKA KELAS IIA YOGYAKARTA<br>
                PERIODE {periode_bulan} {periode_tahun}
            </div>
            <table class="report-table">
                <tr class="bold bg-light"><td colspan="2">TOTAL PENDAPATAN</td><td class="text-right">{rupiah(total_pendapatan)}</td></tr>
                <tr class="bold"><td colspan="3"><br>BIAYA OPERASIONAL:</td></tr>
                <tr class="bold text-center bg-light"><td style="width: 8%;">NO</td><td>NAMA BIAYA OPERASIONAL</td><td style="width: 35%;">NOMINAL (RP)</td></tr>
                {biaya_rows_html}
                <tr class="bold bg-light"><td colspan="2" class="text-right">TOTAL BIAYA OPERASIONAL</td><td class="text-right">{rupiah(total_biaya)}</td></tr>
                <tr class="bold" style="background-color: #e8f5e9;"><td colspan="2">PENDAPATAN BERSIH</td><td class="text-right">{rupiah(laba_bersih)}</td></tr>
                <tr class="bold"><td colspan="3"><br>PEMBAGIAN HASIL BAGI HASIL:</td></tr>
                <tr><td class="text-center">1</td><td>40% X Pendapatan Bersih (Lapas)</td><td class="text-right">{rupiah(porsi_lapas)}</td></tr>
                <tr><td class="text-center">2</td><td>10% X Pendapatan Bersih (Ka. Lapas)</td><td class="text-right">{rupiah(porsi_kalapas)}</td></tr>
                <tr><td class="text-center">3</td><td>10% X Iuran 10% Untuk Inkopasindo</td><td class="text-right">{rupiah(porsi_inkopasindo)}</td></tr>
                <tr><td class="text-center">4</td><td>40% X Pendapatan Bersih (Muffaindo)</td><td class="text-right">{rupiah(porsi_muffaindo)}</td></tr>
                <tr class="bold"><td colspan="3"><br>PENGELUARAN KANTOR:</td></tr>
                <tr><td class="text-center">1</td><td>SHU Koperasi</td><td class="text-right">{rupiah(shu)}</td></tr>
                <tr><td class="text-center">2</td><td>Operasional Kantor</td><td class="text-right">{rupiah(ops)}</td></tr>
                <tr><td class="text-center">3</td><td>Untuk TU, Binadik, Kamtib, Giatja, Staf KPLP, Rupam 1-4 (10 Bagian)</td><td class="text-right">@ {rupiah(staf)}</td></tr>
                <tr><td class="text-center">4</td><td>Untuk Pengurus (4 Pegawai)</td><td class="text-right">@ {rupiah(pengurus)}</td></tr>
                <tr class="bold bg-light"><td colspan="2" class="text-right">TOTAL PENGELUARAN KANTOR</td><td class="text-right">{rupiah(porsi_lapas)}</td></tr>
            </table>
        </div>
    </body>
    </html>
    """
    components.html(doc1, height=720, scrolling=True)

with tab2:
    doc2 = f"""
    <!DOCTYPE html>
    <html>
    <head>{html_style}</head>
    <body>
        <div class="report-box">
            <div class="report-title">
                LAPORAN LABA RUGI WARTEL MUFFAINDO<br>
                JASA VIDEO CALL LAPAS NARKOTIKA KELAS IIA YOGYAKARTA<br>
                PERIODE {periode_bulan} {periode_tahun}
            </div>
            <table class="report-table">
                <tr class="bold bg-light"><td style="width: 65%;">TOTAL PENDAPATAN</td><td class="text-right">{rupiah(total_pendapatan)}</td></tr>
                <tr class="bold"><td>TOTAL PENGELUARAN OPERASIONAL</td><td class="text-right">{rupiah(total_biaya)}</td></tr>
                <tr class="bold" style="background-color: #e8f5e9;"><td>LABA BERSIH</td><td class="text-right">{rupiah(laba_bersih)}</td></tr>
                <tr class="bold"><td colspan="2"><br>PEMBAGIAN BAGI HASIL:</td></tr>
                <tr><td>Profit Sharing 20% (PRIMKOPASINDO)</td><td class="text-right">{rupiah(primkopasindo)}</td></tr>
                <tr><td>Profit Sharing 10% (PENGAWAS UPT)</td><td class="text-right">{rupiah(porsi_kalapas)}</td></tr>
                <tr><td>Profit Sharing 10% (INKOPASINDO)</td><td class="text-right">{rupiah(porsi_inkopasindo)}</td></tr>
                <tr><td>Profit Sharing 60% (CV. MUFFAINDO)</td><td class="text-right">{rupiah(muffaindo2)}</td></tr>
                <tr class="bold bg-light"><td>TOTAL BAGI HASIL</td><td class="text-right">{rupiah(laba_bersih)}</td></tr>
            </table>
        </div>
    </body>
    </html>
    """
    components.html(doc2, height=450, scrolling=True)
