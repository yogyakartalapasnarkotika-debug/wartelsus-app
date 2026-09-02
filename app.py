import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import calendar

# -----------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="KeuanganApp - Lapas Narkotika Yogyakarta",
    page_icon="💼",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. CSS STYLING (ADMINLTE DASHBOARD + A4 PRINT TAJAM)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Source Sans Pro', 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
            background-color: #f4f6f9 !important;
        }

        /* Sembunyikan elemen bawaan Streamlit */
        header, [data-testid="stHeader"], [data-testid="stToolbar"],
        .stAppHeader, #MainMenu, footer {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }

        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Top Navbar AdminLTE */
        .admin-navbar {
            background-color: #3c8dbc;
            color: #ffffff;
            padding: 10px 15px;
            margin: -0.5rem -1rem 15px -1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .admin-navbar-brand { font-size: 20px; font-weight: 700; }
        .admin-navbar-user { font-size: 13px; font-weight: 600; }

        /* Sidebar Styling AdminLTE */
        section[data-testid="stSidebar"] { background-color: #222d32 !important; width: 250px !important; }
        section[data-testid="stSidebar"] * { color: #b8c7ce !important; }
        .user-panel { padding: 15px 10px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #1a2226; }
        .user-avatar { width: 45px; height: 45px; border-radius: 50%; background: #3c8dbc; display: flex; align-items: center; justify-content: center; font-size: 22px; color: #fff; }
        .user-info { font-size: 13px; font-weight: 600; color: #fff !important; }
        .user-status { font-size: 11px; color: #00a65a !important; }

        /* AdminLTE Info Box / Small Box Cards */
        .small-box {
            border-radius: 3px; position: relative; display: block; margin-bottom: 15px;
            box-shadow: 0 1px 1px rgba(0,0,0,0.1); color: #ffffff !important; padding: 12px 15px;
        }
        .small-box-green { background-color: #00a65a !important; }
        .small-box-blue { background-color: #00c0ef !important; }
        .small-box-orange { background-color: #f39c12 !important; }
        .small-box-black { background-color: #222d32 !important; }
        .small-box-red { background-color: #dd4b39 !important; }
        
        .small-box .inner h3 { font-size: 18px; font-weight: bold; margin: 0 0 5px 0; white-space: nowrap; padding: 0; color: #fff !important;}
        .small-box .inner p { font-size: 12px; margin: 0; color: #fff !important; opacity: 0.9; }
        .small-box .icon-bg { position: absolute; top: 10px; right: 10px; z-index: 0; font-size: 40px; color: rgba(0, 0, 0, 0.15); }
        .small-box-footer {
            position: relative; text-align: center; padding: 3px 0; color: rgba(255, 255, 255, 0.8) !important;
            display: block; z-index: 10; background: rgba(0, 0, 0, 0.1); text-decoration: none; font-size: 11px; margin: 8px -15px -12px -15px;
            border-bottom-left-radius: 3px; border-bottom-right-radius: 3px;
        }

        /* Container Card */
        .box-container {
            background: #ffffff; border-top: 3px solid #3c8dbc; border-radius: 3px;
            padding: 15px; margin-bottom: 20px; box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        }
        .box-header { font-size: 16px; font-weight: 600; color: #444; border-bottom: 1px solid #f4f4f4; padding-bottom: 8px; margin-bottom: 12px; }

        /* Hilangkan Tombol Stepper +/- pada Number Input */
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { 
            -webkit-appearance: none; 
            margin: 0; 
        }
        input[type=number] { -moz-appearance: textfield; }

        /* FORMAT CETAK A4 100% PRESISI & TAJAM */
        @media print {
            @page {
                size: A4 portrait;
                margin: 10mm 12mm 10mm 12mm;
            }

            section[data-testid="stSidebar"], 
            header, footer, .admin-navbar,
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

        /* Document Container A4 */
        .pdf-page {
            background: #ffffff; color: #000000; padding: 20px 30px;
            font-family: Arial, Helvetica, sans-serif; font-size: 9pt; line-height: 1.35;
            border: 1px solid #d2d6de; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin: 0 auto 20px auto; max-width: 210mm;
        }
        .pdf-header-code { font-size: 10pt; font-weight: bold; margin-bottom: 8px; }
        .pdf-title { text-align: center; font-weight: bold; font-size: 11pt; text-transform: uppercase; margin-bottom: 12px; line-height: 1.35; }

        .report-table { width: 100%; border-collapse: collapse; font-size: 9pt; color: #000000; table-layout: fixed; }
        .report-table td { padding: 2px 3px; vertical-align: top; }
        .report-table .num-col { width: 4%; text-align: left; }
        .report-table .label-col { width: 56%; }
        .report-table .sep-col { width: 3%; text-align: center; }
        .report-table .currency-col { width: 7%; text-align: left; }
        .report-table .val-col { width: 30%; text-align: right; }

        .text-right { text-align: right !important; }
        .bold { font-weight: bold !important; }
        .indent-1 { padding-left: 18px !important; }

        .ttd-wrapper { margin-top: 25px; width: 100%; display: flex; justify-content: flex-end; }
        .ttd-box { width: 280px; text-align: center; font-size: 9pt; color: #000000; float: right; }
        .page-footer { margin-top: 15px; text-align: right; font-size: 8.5pt; color: #000000; }
    </style>
""", unsafe_allow_html=True)

# Helper Format Angka
def fmt_rupiah(val):
    try:
        return f"Rp. {float(val):,.0f},-".replace(",", ".")
    except:
        return "Rp. 0,-"

def fmt_num(val):
    try:
        return f"{float(val):,.0f}"
    except:
        return "0"

# -----------------------------------------------------------------------------
# 3. DATABASE MANAGEMENT
# -----------------------------------------------------------------------------
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

    # Data Default jika Database Masih Kosong
    c.execute("SELECT COUNT(*) FROM transaksi")
    if c.fetchone()[0] == 0:
        default_tx = [
            ("2026-08-31", "PENDAPATAN", "PENDAPATAN", "PENDAPATAN WARTEL AGUSTUS", 59000000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PULSA PASCA BAYAR", 2960000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "INTERNET", 1005000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "ATK", 0.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PPH 23 (2%)", 1180000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PNBP", 300000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "SERVER", 2243110.0),
            ("2026-08-31", "BIAYA", "LAIN-LAIN", "ANGSURAN PC WARTEL 8", 1000000.0),
            ("2026-08-31", "BIAYA", "LAIN-LAIN", "INSENTIF JAGA KANTIN AGUSTUS 2026", 450000.0),
            ("2026-08-31", "BIAYA", "LAIN-LAIN", "LAIN-LAIN (CHARGER + KABEL TYPE C)", 300000.0)
        ]
        c.executemany("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)", default_tx)
        conn.commit()
    conn.close()

init_db()

# -----------------------------------------------------------------------------
# 4. SIDEBAR & NAVBAR UTAMA
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div class="user-panel">
            <div class="user-avatar">👤</div>
            <div>
                <div class="user-info">Ahmad Jhony</div>
                <div class="user-status">● Online</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="padding: 8px 12px; font-size: 11px; font-weight: bold; color: #4b646f;">MAIN NAVIGATION</div>', unsafe_allow_html=True)
    menu = st.radio("", ["DASHBOARD", "TRANSAKSI POS", "LAPORAN KEUANGAN"], index=0, label_visibility="collapsed")

st.markdown("""
    <div class="admin-navbar no-print">
        <div class="admin-navbar-brand">KeuanganApp</div>
        <div class="admin-navbar-user">Ahmad Jhony - administrator | 🔒 LOGOUT</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. MENU: DASHBOARD (PERSISI DENGAN CONTOH 1 - ADMINLTE)
# -----------------------------------------------------------------------------
if menu == "DASHBOARD":
    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;" class="no-print">
            <span style="font-size:20px; font-weight:600; color:#333;">Dashboard <small style="font-size:12px; color:#777;">Control panel</small></span>
            <span style="font-size:12px; color:#777;">🏠 Home > Dashboard</span>
        </div>
    """, unsafe_allow_html=True)

    conn = sqlite3.connect("wartelsus_pos.db")
    df_all = pd.read_sql_query("SELECT * FROM transaksi", conn)
    conn.close()

    today_str = datetime.now().strftime("%Y-%m-%d")
    month_str = datetime.now().strftime("%Y-%m")
    year_str = datetime.now().strftime("%Y")

    # Perhitungan Metrik AdminLTE
    df_in = df_all[df_all['jenis'] == 'PENDAPATAN']
    df_out = df_all[df_all['jenis'] == 'BIAYA']

    in_today = df_in[df_in['tanggal'] == today_str]['nominal'].sum()
    in_month = df_in[df_in['tanggal'].str.startswith(month_str)]['nominal'].sum()
    in_year = df_in[df_in['tanggal'].str.startswith(year_str)]['nominal'].sum()
    in_total = df_in['nominal'].sum()

    out_today = df_out[df_out['tanggal'] == today_str]['nominal'].sum()
    out_month = df_out[df_out['tanggal'].str.startswith(month_str)]['nominal'].sum()
    out_year = df_out[df_out['tanggal'].str.startswith(year_str)]['nominal'].sum()
    out_total = df_out['nominal'].sum()

    # Baris 1: Pemasukan Cards (Sesuai Warna & Tata Letak Contoh 1)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''
            <div class="small-box small-box-green">
                <div class="inner"><h3>{fmt_rupiah(in_today)}</h3><p>Pemasukan Hari Ini</p></div>
                <div class="icon-bg">📊</div>
                <div class="small-box-footer">More info ➔</div>
            </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''
            <div class="small-box small-box-blue">
                <div class="inner"><h3>{fmt_rupiah(in_month)}</h3><p>Pemasukan Bulan Ini</p></div>
                <div class="icon-bg">📊</div>
                <div class="small-box-footer">More info ➔</div>
            </div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''
            <div class="small-box small-box-orange">
                <div class="inner"><h3>{fmt_rupiah(in_year)}</h3><p>Pemasukan Tahun Ini</p></div>
                <div class="icon-bg">📊</div>
                <div class="small-box-footer">More info ➔</div>
            </div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''
            <div class="small-box small-box-black">
                <div class="inner"><h3>{fmt_rupiah(in_total)}</h3><p>Seluruh Pemasukan</p></div>
                <div class="icon-bg">📊</div>
                <div class="small-box-footer">More info ➔</div>
            </div>''', unsafe_allow_html=True)

    # Baris 2: Pengeluaran Cards (Merah & Gelap)
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(f'''
            <div class="small-box small-box-red">
                <div class="inner"><h3>{fmt_rupiah(out_today)}</h3><p>Pengeluaran Hari Ini</p></div>
                <div class="icon-bg">📉</div>
                <div class="small-box-footer">More info ➔</div>
            </div>''', unsafe_allow_html=True)
    with c6:
        st.markdown(f'''
            <div class="small-box small-box-red">
                <div class="inner"><h3>{fmt_rupiah(out_month)}</h3><p>Pengeluaran Bulan Ini</p></div>
                <div class="icon-bg">📉</div>
                <div class="small-box-footer">More info ➔</div>
            </div>''', unsafe_allow_html=True)
    with c7:
        st.markdown(f'''
            <div class="small-box small-box-red">
                <div class="inner"><h3>{fmt_rupiah(out_year)}</h3><p>Pengeluaran Tahun Ini</p></div>
                <div class="icon-bg">📉</div>
                <div class="small-box-footer">More info ➔</div>
            </div>''', unsafe_allow_html=True)
    with c8:
        st.markdown(f'''
            <div class="small-box small-box-black">
                <div class="inner"><h3>{fmt_rupiah(out_total)}</h3><p>Seluruh Pengeluaran</p></div>
                <div class="icon-bg">📉</div>
                <div class="small-box-footer">More info ➔</div>
            </div>''', unsafe_allow_html=True)

    # Section Grafik & Kalender Samping (Sesuai Gambar 1)
    col_chart, col_cal = st.columns([7, 3])
    with col_chart:
        st.markdown('<div class="box-container"><div class="box-header">Grafik Data Pemasukan & Pengeluaran Per Bulan</div>', unsafe_allow_html=True)
        if not df_all.empty:
            df_chart = df_all.groupby(['jenis'])['nominal'].sum().reset_index()
            fig = px.bar(df_chart, x='jenis', y='nominal', color='jenis',
                         color_discrete_map={'PENDAPATAN': '#00a65a', 'BIAYA': '#dd4b39'},
                         text_auto=True)
            fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data transaksi.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cal:
        st.markdown('<div class="box-container"><div class="box-header" style="background:#00a65a; color:#fff; padding:6px 10px; margin:-15px -15px 10px -15px;">📅 Kalender</div>', unsafe_allow_html=True)
        now = datetime.now()
        cal_html = calendar.HTMLCalendar().formatmonth(now.year, now.month)
        st.markdown(f"<div style='font-size:12px;'>{cal_html}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. MENU: TRANSAKSI POS (LOGIKA PERBAIKAN 5)
# -----------------------------------------------------------------------------
elif menu == "TRANSAKSI POS":
    st.markdown('<div class="box-container"><div class="box-header">Input Transaksi Keuangan</div>', unsafe_allow_html=True)

    # 1. Pilih Jenis Transaksi
    jenis_selected = st.selectbox("Jenis Transaksi", ["PENDAPATAN", "BIAYA"])

    # 2. Dinamis Kategori berdasarkan Jenis Transaksi
    if jenis_selected == "PENDAPATAN":
        kategori_options = ["PENDAPATAN"]
    else:
        kategori_options = ["OPERASIONAL", "LAIN-LAIN"]

    kategori_selected = st.selectbox("Kategori Transaksi", kategori_options)

    # 3. Dropdown Keterangan + Opsi Tambah Baru
    preset_keterangan = [
        "PENDAPATAN WARTEL",
        "PULSA PASCA BAYAR",
        "INTERNET",
        "PNBP",
        "SERVER",
        "ATK",
        "PPH 23 (2%)",
        "ANGSURAN PC WARTEL",
        "INSENTIF JAGA KANTIN",
        "LAIN-LAIN (CHARGER + KABEL TYPE C)",
        "+ Tambah Keterangan Baru..."
    ]

    ket_choice = st.selectbox("Pilih / Tambah Keterangan Transaksi", preset_keterangan)

    if ket_choice == "+ Tambah Keterangan Baru...":
        ket_final = st.text_input("Ketikkan Keterangan Baru:")
    else:
        ket_final = ket_choice

    col_tgl, col_nom = st.columns(2)
    with col_tgl:
        tgl_transaksi = st.date_input("Tanggal Transaksi", datetime.now())
    with col_nom:
        # Menggunakan format bersih tanpa tombol +/- (stepper disembunyikan CSS)
        nominal_val = st.number_input("Nominal (Rp)", min_value=0.0, step=500.0, format="%.0f")

    if st.button("💾 Simpan Transaksi POS", type="primary"):
        if nominal_val > 0 and ket_final.strip() != "":
            conn = sqlite3.connect("wartelsus_pos.db")
            c = conn.cursor()
            c.execute("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)",
                      (tgl_transaksi.strftime('%Y-%m-%d'), jenis_selected, kategori_selected, ket_final, nominal_val))
            conn.commit()
            conn.close()
            st.success("✅ Transaksi berhasil disimpan!")
            st.rerun()
        else:
            st.warning("⚠️ Mohon lengkapi nominal dan keterangan transaksi.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Tabel Riwayat Transaksi
    st.markdown('<div class="box-container"><div class="box-header">Riwayat Transaksi Terdaftar</div>', unsafe_allow_html=True)
    conn = sqlite3.connect("wartelsus_pos.db")
    df_riwayat = pd.read_sql_query("SELECT id, tanggal, jenis, kategori, keterangan, nominal FROM transaksi ORDER BY id DESC", conn)
    conn.close()

    st.dataframe(df_riwayat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. MENU: LAPORAN KEUANGAN (FILTER BULAN BERJALAN & A4 PRESISI TAJAM)
# -----------------------------------------------------------------------------
elif menu == "LAPORAN KEUANGAN":
    st.markdown('<div class="no-print"><div class="box-container"><div class="box-header">Filter Periode Laporan Keuangan</div>', unsafe_allow_html=True)
    
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
        sel_tgl_cetak = st.date_input("TANGGAL DOKUMEN CETAK", datetime(2026, 9, 2))
        
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Filter Database Berdasarkan Bulan Berjalan yang Dipilih
    periode_query = f"{sel_tahun}-{sel_bulan_kode}"
    conn = sqlite3.connect("wartelsus_pos.db")
    df_filtered = pd.read_sql_query("SELECT * FROM transaksi WHERE strftime('%Y-%m', tanggal) = ?", conn, params=(periode_query,))
    conn.close()

    # Kalkulasi Laporan Keuangan Bulan Berjalan
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
    st.button("🖨️ PRINT DOKUMEN LAPORAN A4 (PRESISI 100%)", type="primary", use_container_width=True, 
              on_click=lambda: st.components.v1.html("<script>window.parent.print();</script>", height=0))
    st.markdown('</div>', unsafe_allow_html=True)

    tab_h1, tab_h2 = st.tabs(["📄 Halaman 1 - Laba Rugi", "📄 Halaman 2 - Jasa Video Call"])
    tgl_ttd_str = f"Yogyakarta, {sel_tgl_cetak.strftime('%d')} {sel_bulan_nama.capitalize()} {sel_tgl_cetak.strftime('%Y')}"

    # HALAMAN 1 (PRESISI DENGAN DATA BULAN BERJALAN)
    with tab_h1:
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
                {biaya_rows_h1 if biaya_rows_h1 != '' else '<tr><td>-</td><td colspan="4">Tidak ada data biaya</td></tr>'}
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

    # HALAMAN 2 (100% SESUAI CONTOH FOTO CETAK)
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
