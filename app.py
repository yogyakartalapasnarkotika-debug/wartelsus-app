import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="WARTELSUS KPPK - LAPAS NARKOTIKA YOGYAKARTA",
    page_icon="🏢",
    layout="wide"
)

# 2. CSS Kustom Presisi Cetak A4 & UI Streamlit
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif !important;
            background-color: #f4f6f9 !important;
        }

        /* Sembunyikan Header Native Streamlit */
        header, [data-testid="stHeader"], [data-testid="stToolbar"],
        .stAppHeader, #MainMenu, footer {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }

        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        /* Top Navbar */
        .top-navbar {
            background-color: #1e88e5;
            color: #ffffff;
            padding: 12px 20px;
            margin-left: -1.5rem;
            margin-right: -1.5rem;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .top-navbar-title { font-size: 18px; font-weight: 600; color: #ffffff; }

        .breadcrumb-container {
            font-size: 13px; color: #6c757d; margin-bottom: 15px; font-weight: 500;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] { background-color: #2c323f !important; width: 260px !important; }
        section[data-testid="stSidebar"] * { color: #c2c7d0 !important; }
        .sidebar-brand { padding: 15px; border-bottom: 1px solid #3f4756; display: flex; align-items: center; gap: 10px; }
        .sidebar-brand-title { font-size: 16px; font-weight: 700; color: #ffffff !important; }

        /* Metric Cards */
        .card-stat { border-radius: 8px; color: #ffffff; padding: 15px 18px; position: relative; margin-bottom: 15px; }
        .card-stat-blue { background: linear-gradient(135deg, #2196f3, #1e88e5); }
        .card-stat-green { background: linear-gradient(135deg, #4caf50, #43a047); }
        .card-stat-red { background: linear-gradient(135deg, #f44336, #e53935); }
        .card-val { font-size: 22px; font-weight: 700; }
        .card-lbl { font-size: 12px; opacity: 0.9; }

        .content-card {
            background-color: #ffffff; border-radius: 8px; padding: 20px;
            border: 1px solid #e2e8f0; margin-bottom: 20px;
        }
        .content-card-title {
            font-size: 15px; font-weight: 600; color: #2c323f;
            margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;
        }

        /* ATURAN CETAK A4 PRESISI (REVISI TERAKHIR) */
        @media print {
            @page {
                size: A4 portrait;
                margin: 12mm 15mm 12mm 15mm;
            }

            section[data-testid="stSidebar"], 
            header, footer, .top-navbar, .breadcrumb-container,
            .stButton, .no-print, [data-testid="stTabs"],
            div[data-testid="stVerticalBlock"] > div:has(.no-print) {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
            }

            body, html, .main, .block-container, [data-testid="stAppViewContainer"] {
                background: #ffffff !important;
                color: #000000 !important;
                padding: 0 !important;
                margin: 0 !important;
                width: 100% !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }

            .pdf-page {
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
                box-shadow: none !important;
                width: 100% !important;
                background: #ffffff !important;
            }
        }

        /* Wadah Dokumen Laporan */
        .pdf-page {
            background: #ffffff;
            color: #000000;
            padding: 25px 35px;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 9pt;
            line-height: 1.35;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin: 0 auto 20px auto;
            max-width: 210mm;
        }

        .pdf-header-code { font-size: 10pt; font-weight: bold; margin-bottom: 10px; }
        .pdf-title {
            text-align: center; font-weight: bold; font-size: 11pt;
            text-transform: uppercase; margin-bottom: 15px; line-height: 1.35;
        }

        .report-table {
            width: 100%; border-collapse: collapse; font-size: 9pt;
            color: #000000; table-layout: fixed;
        }
        .report-table td { padding: 2px 3px; vertical-align: top; }
        .report-table .num-col { width: 4%; text-align: left; }
        .report-table .label-col { width: 56%; }
        .report-table .sep-col { width: 3%; text-align: center; }
        .report-table .currency-col { width: 7%; text-align: left; }
        .report-table .val-col { width: 30%; text-align: right; }

        .text-right { text-align: right !important; }
        .bold { font-weight: bold !important; }
        .indent-1 { padding-left: 18px !important; }

        .ttd-wrapper { margin-top: 30px; width: 100%; display: flex; justify-content: flex-end; }
        .ttd-box { width: 280px; text-align: center; font-size: 9pt; color: #000000; float: right; }
        .page-footer { margin-top: 20px; text-align: right; font-size: 8.5pt; color: #000000; }
    </style>
""", unsafe_allow_html=True)

# Helper Format Angka dengan Koma Sesuai Contoh Foto 3
def fmt_num(val):
    try:
        return f"{float(val):,.0f}"
    except:
        return "0"

# Inisialisasi Database
def init_db():
    conn = sqlite3.connect("wartelsus_pos.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            jenis TEXT,
            kategori TEXT,
            keterangan TEXT,
            nominal REAL
        )
    """)
    conn.commit()

    c.execute("SELECT COUNT(*) FROM transaksi")
    if c.fetchone()[0] == 0:
        default_tx = [
            ("2026-08-31", "PENDAPATAN", "PENDAPATAN WARTEL", "PENDAPATAN WARTEL AGUSTUS", 59000000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PULSA PASCA BAYAR", 2960000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "INTERNET", 1005000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "ATK", 0.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PPH 23 (2%)", 1180000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PNBP s.d JULI 2027", 300000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "SERVER", 2243110.0),
            ("2026-08-31", "BIAYA", "LAIN-LAIN", "ANGSURAN PC WARTEL 8", 1000000.0),
            ("2026-08-31", "BIAYA", "LAIN-LAIN", "INSENTIF JAGA KANTIN AGUSTUS 2026", 450000.0),
            ("2026-08-31", "BIAYA", "LAIN-LAIN", "LAIN-LAIN (CHARGER + KABEL TYPE C)", 300000.0)
        ]
        c.executemany("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)", default_tx)
        conn.commit()
    conn.close()

init_db()

# Navigation Sidebar
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div style="font-size: 22px;">🏢</div>
            <div>
                <div class="sidebar-brand-title">WARTELSUS POS</div>
                <div style="font-size: 11px; color: #9aa0ac;">Lapas Narkotika Yogyakarta</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    menu = st.radio("NAVIGATION", ["Dashboard", "Transaksi POS", "Laporan Keuangan"], index=2)

st.markdown("""
    <div class="top-navbar no-print">
        <div class="top-navbar-title">APLIKASI KEUANGAN WARTELSUS & POS</div>
        <div style="font-size: 12px; opacity: 0.9;">Tahun Anggaran 2026</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. DASHBOARD
# -----------------------------------------------------------------------------
if menu == "Dashboard":
    st.markdown('<div class="breadcrumb-container no-print">Home » Dashboard Utama</div>', unsafe_allow_html=True)

    conn = sqlite3.connect("wartelsus_pos.db")
    df_all = pd.read_sql_query("SELECT * FROM transaksi", conn)
    conn.close()

    tot_in = df_all[df_all['jenis'] == 'PENDAPATAN']['nominal'].sum()
    tot_out = df_all[df_all['jenis'] == 'BIAYA']['nominal'].sum()
    laba = tot_in - tot_out

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="card-stat card-stat-blue"><div class="card-lbl">TOTAL PENDAPATAN</div><div class="card-val">Rp {fmt_num(tot_in)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="card-stat card-stat-red"><div class="card-lbl">TOTAL BIAYA OPERASIONAL</div><div class="card-val">Rp {fmt_num(tot_out)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card-stat card-stat-green"><div class="card-lbl">LABA BERSIH (NET)</div><div class="card-val">Rp {fmt_num(laba)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="content-card-title">Ringkasan Grafik Keuangan</div>', unsafe_allow_html=True)
    if not df_all.empty:
        df_chart = df_all.groupby('jenis')['nominal'].sum().reset_index()
        fig = px.bar(df_chart, x='jenis', y='nominal', color='jenis', title="Pendapatan vs Pengeluaran", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data transaksi.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. TRANSAKSI POS
# -----------------------------------------------------------------------------
elif menu == "Transaksi POS":
    st.markdown('<div class="breadcrumb-container no-print">Home » Transaksi POS & Input Data</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="content-card-title">Tambah Transaksi Baru</div>', unsafe_allow_html=True)
    
    with st.form("form_tx", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            tgl = st.date_input("Tanggal Transaksi", datetime.now())
            jenis = st.selectbox("Jenis Transaksi", ["PENDAPATAN", "BIAYA"])
            kategori = st.selectbox("Kategori", ["OPERASIONAL", "LAIN-LAIN", "PENDAPATAN WARTEL"])
        with f2:
            ket = st.text_input("Keterangan", placeholder="Detail nama pengeluaran/pendapatan")
            nominal = st.number_input("Nominal (Rp)", min_value=0.0, step=1000.0)

        btn_simpan = st.form_submit_button("💾 Simpan Transaksi", type="primary")

        if btn_simpan:
            if nominal > 0 and ket.strip() != "":
                conn = sqlite3.connect("wartelsus_pos.db")
                c = conn.cursor()
                c.execute("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)",
                          (tgl.strftime('%Y-%m-%d'), jenis, kategori, ket, nominal))
                conn.commit()
                conn.close()
                st.success("Transaksi berhasil disimpan!")
                st.rerun()
            else:
                st.warning("Mohon isi keterangan dan nominal dengan benar.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="content-card-title">Riwayat Transaksi Terbaru</div>', unsafe_allow_html=True)
    conn = sqlite3.connect("wartelsus_pos.db")
    df_tx = pd.read_sql_query("SELECT id, tanggal, jenis, kategori, keterangan, nominal FROM transaksi ORDER BY id DESC", conn)
    conn.close()

    st.dataframe(df_tx, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. LAPORAN KEUANGAN (REVISI TERAKHIR SESUAI CONTOH GAMBAR 3)
# -----------------------------------------------------------------------------
elif menu == "Laporan Keuangan":
    st.markdown('<div class="breadcrumb-container no-print">Home » Cetak Laporan Fisik A4</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="no-print"><div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">Filter Periode Laporan Cetak</div>', unsafe_allow_html=True)
        
        c_f1, c_f2, c_f3 = st.columns([3, 3, 4])
        bulan_dict = {
            "JANUARI": "01", "FEBRUARI": "02", "MARET": "03", "APRIL": "04",
            "MEI": "05", "JUNI": "06", "JULI": "07", "AGUSTUS": "08",
            "SEPTEMBER": "09", "OKTOBER": "10", "NOVEMBER": "11", "DESEMBER": "12"
        }

        with c_f1:
            sel_bulan_nama = st.selectbox("BULAN LAPORAN", list(bulan_dict.keys()), index=7)
            sel_bulan_kode = bulan_dict[sel_bulan_nama]
        with c_f2:
            sel_tahun = st.number_input("TAHUN LAPORAN", value=2026, min_value=2020, max_value=2030)
        with c_f3:
            sel_tgl_cetak = st.date_input("TANGGAL CETAK", datetime(2026, 9, 2))
            
        st.markdown('</div></div>', unsafe_allow_html=True)

    periode_query = f"{sel_tahun}-{sel_bulan_kode}"
    conn = sqlite3.connect("wartelsus_pos.db")
    df_filtered = pd.read_sql_query("SELECT * FROM transaksi WHERE strftime('%Y-%m', tanggal) = ?", conn, params=(periode_query,))
    conn.close()

    pendapatan_tot = df_filtered[df_filtered['jenis'] == 'PENDAPATAN']['nominal'].sum()
    df_biaya_all = df_filtered[df_filtered['jenis'] == 'BIAYA']
    biaya_tot = df_biaya_all['nominal'].sum()
    laba_bersih = pendapatan_tot - biaya_tot

    porsi_lapas = 0.40 * laba_bersih
    porsi_kalapas = 0.10 * laba_bersih
    porsi_inkopasindo = 0.10 * laba_bersih
    porsi_muffaindo = 0.40 * laba_bersih

    shu = 0.325 * porsi_lapas
    ops = 0.30 * porsi_lapas
    porsi_bagian = 0.035 * porsi_lapas
    porsi_pengurus = 0.015 * porsi_lapas

    primkopasindo = 0.20 * laba_bersih
    muffaindo2 = 0.60 * laba_bersih

    st.markdown('<div class="no-print" style="margin-bottom:15px;">', unsafe_allow_html=True)
    st.button("🖨️ CETAK / PRINT DOKUMEN LAPORAN A4", type="primary", use_container_width=True, 
              on_click=lambda: st.components.v1.html("<script>window.parent.print();</script>", height=0))
    st.markdown('</div>', unsafe_allow_html=True)

    tab_h1, tab_h2 = st.tabs(["📄 Halaman 1 - Laba Rugi", "📄 Halaman 2 - Jasa Video Call"])
    tgl_ttd_str = f"Yogyakarta, {sel_tgl_cetak.strftime('%d')} {sel_bulan_nama.capitalize()} {sel_tgl_cetak.strftime('%Y')}"

    # HALAMAN 1 (PRESISI DENGAN PISAHAN SUB-KATEGORI)
    with tab_h1:
        # Pisahkan item Operasional & Lain-Lain secara terstruktur
        df_ops_items = df_biaya_all[df_biaya_all['kategori'] != 'LAIN-LAIN'].to_dict('records')
        df_lain_items = df_biaya_all[df_biaya_all['kategori'] == 'LAIN-LAIN'].to_dict('records')

        biaya_rows_h1 = ""
        idx_count = 1
        for b in df_ops_items:
            biaya_rows_h1 += f"""
            <tr>
                <td class="num-col">{idx_count}</td>
                <td class="label-col">{b['keterangan']}</td>
                <td class="sep-col">:</td>
                <td class="currency-col">Rp</td>
                <td class="val-col">{fmt_num(b['nominal'])}</td>
            </tr>"""
            idx_count += 1

        for b in df_lain_items:
            biaya_rows_h1 += f"""
            <tr>
                <td class="num-col">{idx_count}</td>
                <td class="label-col">{b['keterangan']}</td>
                <td class="sep-col">:</td>
                <td class="currency-col">Rp</td>
                <td class="val-col">{fmt_num(b['nominal'])}</td>
            </tr>"""
            idx_count += 1

        html_h1 = f"""
        <div class="pdf-page">
            <div class="pdf-header-code">1 WARTEL SUS</div>
            <div class="pdf-title">
                LAPORAN LABA RUGI WARTEL MUFFAINDO<br>
                LAPAS NARKOTIKA KELAS IIA YOGYAKARTA<br>
                PERIODE {sel_bulan_nama} {sel_tahun}
            </div>

            <table class="report-table">
                <tr class="bold">
                    <td colspan="2" class="label-col">TOTAL PENDAPATAN</td>
                    <td class="sep-col">:</td>
                    <td class="currency-col">Rp</td>
                    <td class="val-col">{fmt_num(pendapatan_tot)}</td>
                </tr>
                <tr><td colspan="5" style="height:6px;"></td></tr>
                <tr class="bold"><td colspan="5">BIAYA OPERASIONAL:</td></tr>
                {biaya_rows_h1}
                <tr class="bold">
                    <td colspan="2">TOTAL BIAYA OPERASIONAL</td>
                    <td class="sep-col">:</td>
                    <td class="currency-col">Rp</td>
                    <td class="val-col">{fmt_num(biaya_tot)}</td>
                </tr>
                <tr><td colspan="5" style="height:6px;"></td></tr>
                <tr class="bold">
                    <td colspan="2">PENDAPATAN BERSIH</td>
                    <td class="sep-col">:</td>
                    <td class="currency-col">Rp</td>
                    <td class="val-col">{fmt_num(laba_bersih)}</td>
                </tr>
                <tr><td colspan="5" style="height:8px;"></td></tr>
                <tr class="bold"><td colspan="5">PEMBAGIAN HASIL BAGI HASIL:</td></tr>
                <tr><td class="num-col">1</td><td class="label-col">40% X PENDAPATAN BERSIH (LAPAS)</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_lapas)}</td></tr>
                <tr><td class="num-col">2</td><td class="label-col">10% X PENDAPATAN BERSIH (Ka.LAPAS)</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_kalapas)}</td></tr>
                <tr><td class="num-col">3</td><td class="label-col">10% X IURAN 10% UNTUK INKOPASINDO</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_inkopasindo)}</td></tr>
                <tr><td class="num-col">4</td><td class="label-col">40% X PENDAPATAN BERSIH (MUFAINDO)</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_muffaindo)}</td></tr>
                <tr class="bold"><td></td><td>TOTAL BAGI HASIL</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(laba_bersih)}</td></tr>
                <tr><td colspan="5" style="height:8px;"></td></tr>
                <tr class="bold"><td colspan="5">PENGELUARAN KANTOR:</td></tr>
                <tr><td class="num-col">1</td><td class="label-col">SHU KOPERASI</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(shu)}</td></tr>
                <tr><td class="num-col">2</td><td class="label-col">OPERASIONAL KANTOR</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(ops)}</td></tr>
                <tr><td class="num-col">3</td><td>UNTUK TU</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td class="num-col">4</td><td>UNTUK BINADIK</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td class="num-col">5</td><td>UNTUK KAMTIB</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td class="num-col">6</td><td>UNTUK GIATJA</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td class="num-col">7</td><td>UNTUK STAF KPLP</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td class="num-col">8</td><td colspan="4">UNTUK 4 (Empat) RUPAM</td></tr>
                <tr><td></td><td class="indent-1">RUPAM 1</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td></td><td class="indent-1">RUPAM 2</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td></td><td class="indent-1">RUPAM 3</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td></td><td class="indent-1">RUPAM 4</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_bagian)}</td></tr>
                <tr><td class="num-col">9</td><td colspan="4">UNTUK PENGURUS: 4 Pegawai</td></tr>
                <tr><td></td><td class="indent-1">AGUS YULIANTO</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_pengurus)}</td></tr>
                <tr><td></td><td class="indent-1">KPLP</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_pengurus)}</td></tr>
                <tr><td></td><td class="indent-1">KPLP</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_pengurus)}</td></tr>
                <tr><td></td><td class="indent-1">KPLP</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_pengurus)}</td></tr>
                <tr class="bold"><td colspan="2">TOTAL PENGELUARAN KANTOR</td><td class="sep-col">:</td><td class="currency-col">Rp</td><td class="val-col">{fmt_num(porsi_lapas)}</td></tr>
            </table>

            <div class="page-footer">Hal 1</div>
        </div>"""
        st.markdown(html_h1, unsafe_allow_html=True)

    # HALAMAN 2 (100% PERSISI SESUAI FOTO FILE TERAKHIR / KE-3)
    with tab_h2:
        df_ops_h2 = df_biaya_all[df_biaya_all['kategori'] != 'LAIN-LAIN'].to_dict('records')
        df_lain_h2 = df_biaya_all[df_biaya_all['kategori'] == 'LAIN-LAIN'].to_dict('records')

        rows_ops_h2 = ""
        for b in df_ops_h2:
            rows_ops_h2 += f"<tr><td style='width: 60%;'>{b['keterangan']}</td><td style='width: 10%;'>Rp</td><td class='text-right'>{fmt_num(b['nominal'])}</td></tr>"

        rows_lain_h2 = ""
        for b in df_lain_h2:
            rows_lain_h2 += f"<tr><td style='width: 60%;'>{b['keterangan']}</td><td style='width: 10%;'>Rp</td><td class='text-right'>{fmt_num(b['nominal'])}</td></tr>"

        html_h2 = f"""
        <div class="pdf-page">
            <table class="report-table" style="margin-bottom: 12px;">
                <tr><td style="width: 22%;">NAMA WARTEL</td><td style="width:3%;">:</td><td>WARTEL LAPAS NARKOTIKA KELAS IIA YOGYAKARTA</td></tr>
                <tr><td>ALAMAT</td><td>:</td><td>JL KALIURANG KM 17 PAKEMBINANGUN PAKEM SLEMAN YOGYAKARTA</td></tr>
                <tr><td>PERIODE PEMAKAIAN</td><td>:</td><td>{sel_bulan_nama} {sel_tahun}</td></tr>
            </table>

            <div class="pdf-title" style="margin-bottom: 15px;">
                LAPORAN LABA RUGI WARTEL MUFFAINDO<br>
                JASA VIDIO CALL LAPAS NARKOTIKA KELAS IIA YOGYAKARTA
            </div>

            <table class="report-table">
                <tr>
                    <td style="width: 50%; vertical-align: top; padding-right: 15px;">
                        <div class="bold">PENDAPATAN 1:</div>
                        <table class="report-table">
                            <tr><td style="width: 40%;">KBU 1</td><td style="width: 10%;">Rp</td><td class="text-right">0</td></tr>
                            <tr><td>KBU 2</td><td>Rp</td><td class="text-right">0</td></tr>
                            <tr><td>KBU 3</td><td>Rp</td><td class="text-right">0</td></tr>
                            <tr class="bold"><td>TOTAL</td><td>Rp</td><td class="text-right">{fmt_num(pendapatan_tot)}</td></tr>
                        </table>
                    </td>
                    <td style="width: 50%; vertical-align: top; padding-left: 15px;">
                        <div class="bold">PENDAPATAN II:</div>
                        <table class="report-table">
                            <tr><td style="width: 40%;">KBU 4</td><td style="width: 10%;">Rp</td><td class="text-right">0</td></tr>
                            <tr><td>KBU 5</td><td>Rp</td><td class="text-right">0</td></tr>
                            <tr><td>KBU 6</td><td>Rp</td><td class="text-right">0</td></tr>
                            <tr class="bold"><td>TOTAL</td><td>Rp</td><td class="text-right">0</td></tr>
                        </table>
                    </td>
                </tr>
            </table>

            <br>
            <table class="report-table">
                <tr class="bold">
                    <td style="width: 50%; vertical-align: top; padding-right: 15px;">PENGELUARAN:</td>
                    <td style="width: 50%; vertical-align: top; padding-left: 15px;">&nbsp;</td>
                </tr>
                <tr>
                    <td style="vertical-align: top; padding-right: 15px;">
                        <table class="report-table">
                            <tr><td style="width: 50%;">PENDAPATAN I</td><td style="width: 10%;">Rp</td><td class="text-right">{fmt_num(pendapatan_tot)}</td></tr>
                            <tr><td>PENDAPATAN II</td><td>Rp</td><td class="text-right">0</td></tr>
                            <tr class="bold"><td>TOTAL PENDAPATAN</td><td>Rp</td><td class="text-right">{fmt_num(pendapatan_tot)}</td></tr>
                        </table>
                    </td>
                    <td style="vertical-align: top; padding-left: 15px;">
                        <table class="report-table">
                            {rows_ops_h2}
                            <tr class="bold"><td colspan="3" style="padding-top:4px;">LAIN-LAIN:</td></tr>
                            {rows_lain_h2}
                            <tr class="bold"><td style="padding-top:6px;">TOTAL PENGELUARAN</td><td style="padding-top:6px;">Rp</td><td class="text-right" style="padding-top:6px;">{fmt_num(biaya_tot)}</td></tr>
                        </table>
                    </td>
                </tr>
            </table>

            <br>
            <table class="report-table">
                <tr class="bold">
                    <td style="width: 28%;">TOTAL PENGELUARAN</td>
                    <td style="width: 3%;">:</td>
                    <td style="width: 5%;">Rp</td>
                    <td class="text-right" style="width: 20%;">{fmt_num(biaya_tot)}</td>
                    <td style="width: 44%;"></td>
                </tr>
                <tr class="bold">
                    <td>LABA BERSIH</td>
                    <td>:</td>
                    <td>Rp</td>
                    <td class="text-right">{fmt_num(laba_bersih)}</td>
                    <td></td>
                </tr>
            </table>

            <br>
            <div class="bold" style="margin-bottom: 5px;">PEMBAGIAN BAGI HASIL:</div>
            <table class="report-table">
                <tr>
                    <td style="width: 20%;">PROFIT SHRING</td>
                    <td style="width: 8%;">20%</td>
                    <td style="width: 3%;">X</td>
                    <td style="width: 18%;">{fmt_num(laba_bersih)}</td>
                    <td class="text-right">{fmt_num(primkopasindo)} (PRIMKOPASINDO)</td>
                </tr>
                <tr>
                    <td>PROFIT SHRING</td>
                    <td>10%</td>
                    <td>X</td>
                    <td>{fmt_num(laba_bersih)}</td>
                    <td class="text-right">{fmt_num(porsi_kalapas)} (PENGAWAS UPT)</td>
                </tr>
                <tr>
                    <td>PROFIT SHRING</td>
                    <td>10%</td>
                    <td>X</td>
                    <td>{fmt_num(laba_bersih)}</td>
                    <td class="text-right">{fmt_num(porsi_inkopasindo)} (INKOPASINDO)</td>
                </tr>
                <tr>
                    <td>PROFIT SHRING</td>
                    <td>60%</td>
                    <td>X</td>
                    <td>{fmt_num(laba_bersih)}</td>
                    <td class="text-right">{fmt_num(muffaindo2)} (CV. MUFFAINDO)</td>
                </tr>
                <tr class="bold">
                    <td colspan="3"></td>
                    <td>TOTAL</td>
                    <td class="text-right">{fmt_num(laba_bersih)}</td>
                </tr>
            </table>

            <div class="ttd-wrapper">
                <div class="ttd-box">
                    <div>{tgl_ttd_str}</div>
                    <div>Penanggungjawab</div>
                    <div class="bold" style="margin-top:2px;">KETUA KOPERASI</div>
                    <br><br><br>
                    <div class="bold" style="text-decoration: underline;">DANANG ANDRIYANTO</div>
                </div>
            </div>

            <div style="clear:both;"></div>
            <div class="page-footer">Hal. 2</div>
        </div>"""
        st.markdown(html_h2, unsafe_allow_html=True)
