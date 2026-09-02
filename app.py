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

# 2. Inject CSS Kustom (Fix Filter Leak & Cetak Jelas/Tajam)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif !important;
            background-color: #f4f6f9 !important;
        }

        /* ----------------------------------------------------
           1. HILANGKAN TOP HEADER STREAMLIT
           ---------------------------------------------------- */
        header, 
        [data-testid="stHeader"], 
        [data-testid="stToolbar"],
        .stAppHeader,
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }

        .main .block-container {
            padding-top: 0rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        /* ----------------------------------------------------
           2. TOP NAVBAR & BREADCRUMB
           ---------------------------------------------------- */
        .top-navbar {
            background-color: #1e88e5;
            color: #ffffff;
            padding: 14px 25px;
            margin-left: -1.5rem;
            margin-right: -1.5rem;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .top-navbar-title {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
        }

        .breadcrumb-container {
            font-size: 13px;
            color: #6c757d;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .breadcrumb-container a {
            color: #1e88e5;
            text-decoration: none;
        }

        /* ----------------------------------------------------
           3. SIDEBAR STYLING
           ---------------------------------------------------- */
        section[data-testid="stSidebar"] {
            background-color: #2c323f !important;
            width: 260px !important;
        }
        section[data-testid="stSidebar"] * {
            color: #c2c7d0 !important;
        }
        
        .sidebar-brand {
            padding: 18px 15px;
            border-bottom: 1px solid #3f4756;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .sidebar-brand-title {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff !important;
            line-height: 1.2;
        }
        .sidebar-brand-sub {
            font-size: 11px;
            color: #9aa0ac !important;
            margin-top: 4px;
        }

        section[data-testid="stSidebar"] .stRadio > div {
            gap: 6px !important;
            padding-top: 15px;
        }
        section[data-testid="stSidebar"] .stRadio label {
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 10px 16px !important;
            border-radius: 6px !important;
            background-color: transparent !important;
            border: none !important;
            color: #c2c7d0 !important;
            cursor: pointer !important;
            transition: all 0.2s;
            display: flex;
            align-items: center;
        }
        section[data-testid="stSidebar"] .stRadio label:hover {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stRadio div[aria-checked="true"] label {
            background-color: #1e88e5 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 6px rgba(30, 136, 229, 0.4);
        }

        /* ----------------------------------------------------
           4. METRIC CARDS
           ---------------------------------------------------- */
        .card-stat {
            border-radius: 8px;
            color: #ffffff;
            padding: 18px 20px;
            position: relative;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
            margin-bottom: 15px;
        }
        .card-stat-blue { background: linear-gradient(135deg, #2196f3, #1e88e5); }
        .card-stat-green { background: linear-gradient(135deg, #4caf50, #43a047); }
        .card-stat-orange { background: linear-gradient(135deg, #ff9800, #fb8c00); }
        .card-stat-red { background: linear-gradient(135deg, #f44336, #e53935); }

        .card-val {
            font-size: 24px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 4px;
        }
        .card-lbl {
            font-size: 13px;
            font-weight: 400;
            opacity: 0.9;
        }
        .card-icon {
            position: absolute;
            right: 18px;
            top: 20px;
            font-size: 32px;
            opacity: 0.3;
        }
        .card-footer-info {
            margin-top: 12px;
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            font-size: 11px;
            opacity: 0.85;
            display: flex;
            justify-content: space-between;
        }

        /* ----------------------------------------------------
           5. CONTAINER UTAMA
           ---------------------------------------------------- */
        .content-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            margin-bottom: 20px;
        }
        .content-card-title {
            font-size: 16px;
            font-weight: 600;
            color: #2c323f;
            margin-bottom: 15px;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 10px;
        }

        /* ----------------------------------------------------
           6. PERBAIKAN TOTAL MODE CETAK / PRINT (JELAS & TAJAM)
           ---------------------------------------------------- */
        @media print {
            @page {
                size: A4 portrait;
                margin: 8mm;
            }

            /* Sembunyikan SEMUA elemen UI web dan elemen input */
            section[data-testid="stSidebar"], 
            .stButton, 
            header, 
            footer, 
            .top-navbar,
            .breadcrumb-container,
            .stTabs [role="tablist"],
            .no-print,
            [data-testid="stVerticalBlock"] > div:has(div[data-testid="stForm"]),
            div[element-id*="filter"],
            div[data-testid="stSelectbox"],
            div[data-testid="stNumberInput"],
            div[data-testid="stDateInput"],
            .stMarkdown:has(.no-print) {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }

            body, html, .main, .block-container {
                background: #ffffff !important;
                color: #000000 !important;
                padding: 0 !important;
                margin: 0 !important;
                width: 100% !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }

            /* Memaksa Teks dan Tabel Tajam (Hitam Pekat & Tidak Buram) */
            .pdf-page { 
                border: none !important; 
                padding: 0 !important; 
                box-shadow: none !important;
                width: 100% !important;
                background: #ffffff !important;
                color: #000000 !important;
                font-family: 'Arial', sans-serif !important;
                -webkit-font-smoothing: antialiased;
            }

            .pdf-title, .pdf-table, .pdf-table td, .pdf-table th, .ttd-container {
                color: #000000 !important;
                text-shadow: none !important;
                filter: none !important;
            }

            .pdf-table td, .pdf-table th {
                border-color: #000000 !important;
            }
        }

        .pdf-page {
            background: #ffffff;
            color: #000000;
            padding: 25px;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 10pt;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .pdf-title {
            text-align: center;
            font-weight: bold;
            font-size: 11pt;
            text-transform: uppercase;
            margin-bottom: 18px;
            line-height: 1.4;
            color: #000000;
        }
        .pdf-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 9.5pt;
            color: #000000;
        }
        .pdf-table td, .pdf-table th {
            padding: 4px 6px;
            vertical-align: top;
        }
        .text-right { text-align: right; }
        .bold { font-weight: bold; }
        
        .ttd-container {
            margin-top: 30px;
            float: right;
            width: 280px;
            text-align: center;
            font-size: 10pt;
            color: #000000;
        }
    </style>
""", unsafe_allow_html=True)

# Helper Formatting
def fmt_rupiah(val):
    try:
        val = float(val)
        return f"Rp {val:,.0f}".replace(",", ".")
    except:
        return "Rp 0"

def fmt_num(val):
    try:
        return f"{float(val):,.0f}".replace(",", ".")
    except:
        return "0"

def parse_rupiah(val_str):
    try:
        clean = str(val_str).replace("Rp", "").replace(".", "").replace(" ", "").strip()
        return float(clean)
    except:
        return 0.0

# Database Management
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
            ("2026-08-31", "BIAYA", "TAGIHAN TELEPON/PULSA", "PULSA PASCA BAYAR", 2960000.0),
            ("2026-08-31", "BIAYA", "TAGIHAN INTERNET", "INTERNET", 1005000.0),
            ("2026-08-31", "BIAYA", "ATK & PERLENGKAPAN", "ATK", 0.0),
            ("2026-08-31", "BIAYA", "PAJAK & PERIZINAN", "PPH 23 (2%)", 1180000.0),
            ("2026-08-31", "BIAYA", "PAJAK & PERIZINAN", "PNBP s.d JULI 2027", 300000.0),
            ("2026-08-31", "BIAYA", "PEMELIHARAAN SERVER", "SERVER", 2243110.0),
            ("2026-08-31", "BIAYA", "ANGSURAN PERALATAN", "ANGSURAN PC WARTEL 8", 1000000.0),
            ("2026-08-31", "BIAYA", "INSENTIF & GAJI", "INSENTIF JAGA KANTIN AGUSTUS 2026", 450000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL LAIN-LAIN", "LAIN-LAIN (CHARGER + KABEL TYPE C)", 300000.0)
        ]
        c.executemany("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)", default_tx)
        conn.commit()
    conn.close()

init_db()

# Sidebar Layout
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div style="font-size: 26px;">🏢</div>
            <div>
                <div class="sidebar-brand-title">WARTELSUS POS</div>
                <div class="sidebar-brand-sub">Lapas Narkotika Yogyakarta</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "NAVIGATION",
        [" Dashboard", " Transaksi POS", " Laporan Keuangan"],
        index=2
    )

# Top Bar Header
st.markdown("""
    <div class="top-navbar no-print">
        <div class="top-navbar-title">APLIKASI KEUANGAN WARTELSUS & POS</div>
        <div style="font-size: 13px; opacity: 0.9;">Tahun Anggaran 2026</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU 1: DASHBOARD
# -----------------------------------------------------------------------------
if "Dashboard" in menu:
    st.markdown("""
        <div class="breadcrumb-container">
            Home » <a href="#">Dashboard Utama</a>
        </div>
    """, unsafe_allow_html=True)

    conn = sqlite3.connect("wartelsus_pos.db")
    df_tx = pd.read_sql_query("SELECT * FROM transaksi ORDER BY tanggal ASC", conn)
    conn.close()

    if not df_tx.empty:
        tot_pendapatan = df_tx[df_tx['jenis'] == 'PENDAPATAN']['nominal'].sum()
        tot_biaya = df_tx[df_tx['jenis'] == 'BIAYA']['nominal'].sum()
        laba_bersih = tot_pendapatan - tot_biaya
        tot_transaksi = len(df_tx)

        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown(f"""
                <div class="card-stat card-stat-blue">
                    <div class="card-icon">💰</div>
                    <div class="card-val">{fmt_rupiah(tot_pendapatan)}</div>
                    <div class="card-lbl">Total Pendapatan</div>
                    <div class="card-footer-info"><span>Akumulasi Masuk</span><span>2026</span></div>
                </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
                <div class="card-stat card-stat-red">
                    <div class="card-icon">💸</div>
                    <div class="card-val">{fmt_rupiah(tot_biaya)}</div>
                    <div class="card-lbl">Total Biaya Operasional</div>
                    <div class="card-footer-info"><span>Akumulasi Keluar</span><span>2026</span></div>
                </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
                <div class="card-stat card-stat-green">
                    <div class="card-icon">📈</div>
                    <div class="card-val">{fmt_rupiah(laba_bersih)}</div>
                    <div class="card-lbl">Laba Bersih</div>
                    <div class="card-footer-info"><span>Hasil Surplus</span><span>2026</span></div>
                </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
                <div class="card-stat card-stat-orange">
                    <div class="card-icon">🧾</div>
                    <div class="card-val">{tot_transaksi}</div>
                    <div class="card-lbl">Total Transaksi</div>
                    <div class="card-footer-info"><span>Item Recorded</span><span>2026</span></div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_g1, col_g2 = st.columns([6, 4])
        
        with col_g1:
            st.markdown("""
                <div class="content-card">
                    <div class="content-card-title">📊 Perbandingan Pendapatan vs Biaya</div>
            """, unsafe_allow_html=True)
            
            df_tx['tanggal_dt'] = pd.to_datetime(df_tx['tanggal'])
            df_tx['bulan_tahun'] = df_tx['tanggal_dt'].dt.strftime('%b %Y')
            df_grouped = df_tx.groupby(['bulan_tahun', 'jenis'], sort=False)['nominal'].sum().reset_index()

            fig = px.bar(
                df_grouped, x='bulan_tahun', y='nominal', color='jenis',
                barmode='group',
                labels={'bulan_tahun': 'Bulan', 'nominal': 'Rupiah', 'jenis': 'Jenis'},
                color_discrete_map={'PENDAPATAN': '#4caf50', 'BIAYA': '#f44336'}
            )
            fig.update_layout(
                template="plotly_white", 
                height=320,
                font=dict(family="Poppins", size=12),
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(title_text='', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_g2:
            st.markdown("""
                <div class="content-card">
                    <div class="content-card-title">🍰 Rincian Biaya Operasional</div>
            """, unsafe_allow_html=True)
            
            df_biaya = df_tx[df_tx['jenis'] == 'BIAYA']
            if not df_biaya.empty:
                fig_pie = px.pie(
                    df_biaya, values='nominal', names='kategori',
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_pie.update_layout(
                    template="plotly_white",
                    height=320,
                    font=dict(family="Poppins", size=11),
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU 2: TRANSAKSI
# -----------------------------------------------------------------------------
elif "Transaksi" in menu:
    st.markdown("""
        <div class="breadcrumb-container">
            Home » <a href="#">Kelola Transaksi POS</a>
        </div>
    """, unsafe_allow_html=True)

    tab_in1, tab_in2 = st.tabs(["➕ Input Transaksi Baru", "📋 Daftar Record Transaksi"])

    opsi_kategori_default = [
        "TAGIHAN INTERNET",
        "TAGIHAN LISTRIK",
        "TAGIHAN TELEPON/PULSA",
        "PENDAPATAN WARTEL",
        "ATK & PERLENGKAPAN",
        "PAJAK & PERIZINAN",
        "PEMELIHARAAN SERVER",
        "ANGSURAN PERALATAN",
        "INSENTIF & GAJI",
        "OPERASIONAL LAIN-LAIN",
        "➕ TAMBAH KATEGORI BARU..."
    ]

    with tab_in1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">Form Input Transaksi Kasir / Operasional</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            tgl_input = st.date_input("Tanggal Transaksi", datetime.now())
            jenis_input = st.selectbox("Jenis Transaksi", ["BIAYA", "PENDAPATAN"])
            
            kat_selected = st.selectbox("Kategori Transaksi", opsi_kategori_default)
            if kat_selected == "➕ TAMBAH KATEGORI BARU...":
                kategori_input = st.text_input("Tuliskan Kategori Baru:", placeholder="Contoh: PERBAIKAN AC").upper()
            else:
                kategori_input = kat_selected

        with c2:
            ket_input = st.text_input("Keterangan Rincian / Detail", placeholder="Contoh: Pembayaran Internet IndiHome Bulan Agustus")
            nom_raw = st.text_input("Nominal Transaksi (Rp)", value="0")
            nom_float = parse_rupiah(nom_raw)
            st.markdown(f"Format Nominal: **{fmt_rupiah(nom_float)}**")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 SIMPAN TRANSAKSI", type="primary", use_container_width=True):
            if nom_float <= 0 and jenis_input == "PENDAPATAN":
                st.error("Nominal pendapatan harus lebih dari 0!")
            elif ket_input.strip() == "":
                st.error("Keterangan detail transaksi harus diisi!")
            elif kategori_input.strip() == "":
                st.error("Kategori transaksi harus ditentukan!")
            else:
                conn = sqlite3.connect("wartelsus_pos.db")
                c = conn.cursor()
                c.execute("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)",
                          (str(tgl_input), jenis_input, kategori_input.upper(), ket_input.upper(), nom_float))
                conn.commit()
                conn.close()
                st.success(f"Transaksi '{ket_input.upper()}' sebesar {fmt_rupiah(nom_float)} berhasil disimpan!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_in2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">Riwayat Database Transaksi</div>', unsafe_allow_html=True)
        
        conn = sqlite3.connect("wartelsus_pos.db")
        df_edit = pd.read_sql_query("SELECT * FROM transaksi ORDER BY tanggal DESC, id DESC", conn)
        conn.close()

        if not df_edit.empty:
            for idx, row in df_edit.iterrows():
                c_tgl, c_jns, c_kat, c_ket, c_nom, c_act = st.columns([1.5, 1.5, 2.5, 3.5, 2, 1])
                c_tgl.write(f"**{row['tanggal']}**")
                c_jns.write(f"`{row['jenis']}`")
                c_kat.write(row['kategori'])
                c_ket.write(row['keterangan'])
                c_nom.write(fmt_rupiah(row['nominal']))
                if c_act.button("🗑️", key=f"del_tx_{row['id']}"):
                    conn = sqlite3.connect("wartelsus_pos.db")
                    c = conn.cursor()
                    c.execute("DELETE FROM transaksi WHERE id = ?", (row['id'],))
                    conn.commit()
                    conn.close()
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU 3: LAPORAN (FILTER DISMBUNYIKAN 100% SAAT CETAK)
# -----------------------------------------------------------------------------
elif "Laporan" in menu:
    st.markdown("""
        <div class="breadcrumb-container no-print">
            Home » <a href="#">Cetak Laporan Fisik A4</a>
        </div>
    """, unsafe_allow_html=True)

    # PEMBUNGKUS FILTER DALAM CONTAINER NATIVE STREAMLIT (+ CLASS NO-PRINT)
    filter_box = st.container()
    with filter_box:
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">Filter Periode Laporan Cetak</div>', unsafe_allow_html=True)
        
        col_l1, col_l2, col_l3 = st.columns([3, 3, 4])
        
        bulan_dict = {
            "JANUARI": "01", "FEBRUARI": "02", "MARET": "03", "APRIL": "04",
            "MEI": "05", "JUNI": "06", "JULI": "07", "AGUSTUS": "08",
            "SEPTEMBER": "09", "OKTOBER": "10", "NOVEMBER": "11", "DESEMBER": "12"
        }

        with col_l1:
            sel_bulan_nama = st.selectbox("BULAN LAPORAN", list(bulan_dict.keys()), index=7, key="f_bulan")
            sel_bulan_kode = bulan_dict[sel_bulan_nama]
        with col_l2:
            sel_tahun = st.number_input("TAHUN LAPORAN", value=2026, min_value=2020, max_value=2030, key="f_tahun")
        with col_l3:
            sel_tgl_cetak = st.date_input("TANGGAL CETAK", datetime(2026, 9, 2), key="f_tgl_cetak")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Query Filter Database
    periode_query = f"{sel_tahun}-{sel_bulan_kode}"
    conn = sqlite3.connect("wartelsus_pos.db")
    df_filtered = pd.read_sql_query(
        "SELECT * FROM transaksi WHERE strftime('%Y-%m', tanggal) = ?", 
        conn, 
        params=(periode_query,)
    )
    conn.close()

    # Kalkulasi Laporan
    pendapatan_tot = df_filtered[df_filtered['jenis'] == 'PENDAPATAN']['nominal'].sum()
    df_biaya_list = df_filtered[df_filtered['jenis'] == 'BIAYA'].to_dict('records')
    biaya_tot = sum([b['nominal'] for b in df_biaya_list])
    laba_bersih = pendapatan_tot - biaya_tot

    # Formulasi Pembagian Hal 1
    porsi_lapas = 0.40 * laba_bersih
    porsi_kalapas = 0.10 * laba_bersih
    porsi_inkopasindo = 0.10 * laba_bersih
    porsi_muffaindo = 0.40 * laba_bersih

    shu = 0.325 * porsi_lapas
    ops = 0.30 * porsi_lapas
    porsi_bagian = 0.035 * porsi_lapas
    porsi_pengurus = 0.015 * porsi_lapas

    # Formulasi Pembagian Hal 2
    primkopasindo = 0.20 * laba_bersih
    muffaindo2 = 0.60 * laba_bersih

    # Tombol Cetak A4
    st.markdown('<div class="no-print" style="margin-bottom:20px;">', unsafe_allow_html=True)
    if df_filtered.empty:
        st.warning(f"⚠️ Tidak ada record transaksi pada **{sel_bulan_nama} {sel_tahun}**.")
    
    st.button("🖨️ CETAK / PRINT DOKUMEN LAPORAN A4", type="primary", use_container_width=True, on_click=lambda: st.components.v1.html("<script>window.parent.print();</script>", height=0))
    st.markdown('</div>', unsafe_allow_html=True)

    tab_h1, tab_h2 = st.tabs(["📄 Halaman 1 - Laba Rugi", "📄 Halaman 2 - Jasa Video Call"])

    tgl_ttd_str = f"Yogyakarta, {sel_tgl_cetak.strftime('%d')} {sel_bulan_nama.capitalize()} {sel_tgl_cetak.strftime('%Y')}"

    # HALAMAN 1
    with tab_h1:
        biaya_rows_h1 = ""
        for idx, b in enumerate(df_biaya_list):
            biaya_rows_h1 += f"""<tr>
<td style="width:5%;">{idx+1}</td>
<td>{b['keterangan']}</td>
<td style="width:3%;">:</td>
<td style="width:5%;">Rp</td>
<td class="text-right" style="width:20%;">{fmt_num(b['nominal'])}</td>
</tr>"""

        if not df_biaya_list:
            biaya_rows_h1 = "<tr><td colspan='5' style='text-align:center;'>- Tidak ada data biaya operasional -</td></tr>"

        html_h1 = f"""<div class="pdf-page">
<div style="font-size: 9pt;" class="bold">1 WARTEL SUS</div>
<div class="pdf-title">
LAPORAN LABA RUGI WARTEL MUFFAINDO<br>
LAPAS NARKOTIKA KELAS IIA YOGYAKARTA<br>
PERIODE {sel_bulan_nama} {sel_tahun}
</div>

<table class="pdf-table">
<tr class="bold">
<td colspan="2">TOTAL PENDAPATAN</td>
<td style="width:3%;">:</td>
<td style="width:5%;">Rp</td>
<td class="text-right" style="width:20%;">{fmt_num(pendapatan_tot)}</td>
</tr>
<tr><td colspan="5">&nbsp;</td></tr>
<tr class="bold">
<td colspan="5">BIAYA OPRASIONAL:</td>
</tr>
{biaya_rows_h1}
<tr class="bold">
<td colspan="2">TOTAL BIAYA OPERASIONAL</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(biaya_tot)}</td>
</tr>
<tr><td colspan="5">&nbsp;</td></tr>
<tr class="bold">
<td colspan="2">PENDAPATAN BERSIH</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(laba_bersih)}</td>
</tr>
<tr><td colspan="5">&nbsp;</td></tr>
<tr class="bold">
<td colspan="5">PEMBAGIAN HASIL BAGI HASIL:</td>
</tr>
<tr>
<td style="width:5%;">1</td>
<td>40% X PENDAPATAN BERSIH (LAPAS)</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(porsi_lapas)}</td>
</tr>
<tr>
<td>2</td>
<td>10% X PENDAPATAN BERSIH (Ka.LAPAS)</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(porsi_kalapas)}</td>
</tr>
<tr>
<td>3</td>
<td>10% X IURAN 10% UNTUK INKOPASINDO</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(porsi_inkopasindo)}</td>
</tr>
<tr>
<td>4</td>
<td>40% X PENDAPATAN BERSIH (MUFAINDO)</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(porsi_muffaindo)}</td>
</tr>
<tr class="bold">
<td></td>
<td>TOTAL BAGI HASIL</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(laba_bersih)}</td>
</tr>
<tr><td colspan="5">&nbsp;</td></tr>
<tr class="bold">
<td colspan="5">PENGELUARAN KANTOR:</td>
</tr>
<tr>
<td>1</td>
<td>SHU KOPERASI</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(shu)}</td>
</tr>
<tr>
<td>2</td>
<td>OPERASIONAL KANTOR</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(ops)}</td>
</tr>
<tr><td>3</td><td>UNTUK TU</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr><td>4</td><td>UNTUK BINADIK</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr><td>5</td><td>UNTUK KAMTIB</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr><td>6</td><td>UNTUK GIATJA</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr><td>7</td><td>UNTUK STAF KPLP</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr>
<td>8</td>
<td colspan="4">UNTUK 4 (Empat) RUPAM</td>
</tr>
<tr><td></td><td style="padding-left: 20px;">RUPAM 1</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr><td></td><td style="padding-left: 20px;">RUPAM 2</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr><td></td><td style="padding-left: 20px;">RUPAM 3</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr><td></td><td style="padding-left: 20px;">RUPAM 4</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_bagian)}</td></tr>
<tr>
<td>9</td>
<td colspan="4">UNTUK PENGURUS: 4 Pegawai</td>
</tr>
<tr><td></td><td style="padding-left: 20px;">AGUS YULIANTO</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_pengurus)}</td></tr>
<tr><td></td><td style="padding-left: 20px;">KPLP</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_pengurus)}</td></tr>
<tr><td></td><td style="padding-left: 20px;">KPLP</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_pengurus)}</td></tr>
<tr><td></td><td style="padding-left: 20px;">KPLP</td><td>:</td><td>Rp</td><td class="text-right">{fmt_num(porsi_pengurus)}</td></tr>
<tr class="bold">
<td colspan="2">TOTAL PENGELUARAN KANTOR</td>
<td>:</td>
<td>Rp</td>
<td class="text-right">{fmt_num(porsi_lapas)}</td>
</tr>
</table>

<div style="clear:both;"></div>
<div style="float: right; font-size: 8pt; margin-top: 15px;">Hal. 1</div>
<div style="clear:both;"></div>
</div>"""
        st.markdown(html_h1, unsafe_allow_html=True)

    # HALAMAN 2
    with tab_h2:
        biaya_rows_h2 = ""
        for b in df_biaya_list:
            biaya_rows_h2 += f"""<tr>
<td>{b['keterangan']}</td>
<td style="width:5%;">Rp</td>
<td class="text-right" style="width:25%;">{fmt_num(b['nominal'])}</td>
</tr>"""

        if not df_biaya_list:
            biaya_rows_h2 = "<tr><td colspan='3' style='text-align:center;'>- Tidak ada data biaya -</td></tr>"

        html_h2 = f"""<div class="pdf-page">
<table class="pdf-table" style="margin-bottom: 15px;">
<tr><td style="width:20%;">NAMA WARTEL</td><td>: WARTEL LAPAS NARKOTIKA KELAS IIA YOGYAKARTA</td></tr>
<tr><td>ALAMAT</td><td>: JL KALIURANG KM 17 PAKEMBINANGUN PAKEM SLEMAN YOGYAKARTA</td></tr>
<tr><td>PERIODE PEMAKAIAN</td><td>: {sel_bulan_nama} {sel_tahun}</td></tr>
</table>

<div class="pdf-title">
LAPORAN LABA RUGI WARTEL MUFFAINDO<br>
JASA VIDIO CALL LAPAS NARKOTIKA KELAS IIA YOGYAKARTA
</div>

<table class="pdf-table">
<tr>
<td style="width: 50%; vertical-align: top;">
<div class="bold">PENDAPATAN 1:</div>
<table class="pdf-table">
<tr><td>KBU 1</td><td>Rp</td><td class="text-right">0</td></tr>
<tr><td>KBU 2</td><td>Rp</td><td class="text-right">0</td></tr>
<tr><td>KBU 3</td><td>Rp</td><td class="text-right">0</td></tr>
<tr class="bold"><td>TOTAL</td><td>Rp</td><td class="text-right">{fmt_num(pendapatan_tot)}</td></tr>
</table>
</td>
<td style="width: 50%; vertical-align: top;">
<div class="bold">PENDAPATAN II:</div>
<table class="pdf-table">
<tr><td>KBU 4</td><td>Rp</td><td class="text-right">0</td></tr>
<tr><td>KBU 5</td><td>Rp</td><td class="text-right">0</td></tr>
<tr><td>KBU 6</td><td>Rp</td><td class="text-right">0</td></tr>
<tr class="bold"><td>TOTAL</td><td>Rp</td><td class="text-right">0</td></tr>
</table>
</td>
</tr>
</table>

<br>
<table class="pdf-table">
<tr class="bold">
<td style="width: 50%;">PENGELUARAN:</td>
<td style="width: 50%;">BIAYA OPERASIONAL:</td>
</tr>
<tr>
<td style="vertical-align: top;">
<table class="pdf-table">
<tr><td>PENDAPATAN I</td><td>Rp</td><td class="text-right">{fmt_num(pendapatan_tot)}</td></tr>
<tr><td>PENDAPATAN II</td><td>Rp</td><td class="text-right">0</td></tr>
<tr class="bold"><td>TOTAL PENDAPATAN</td><td>Rp</td><td class="text-right">{fmt_num(pendapatan_tot)}</td></tr>
</table>
</td>
<td style="vertical-align: top;">
<table class="pdf-table">
{biaya_rows_h2}
<tr class="bold"><td>TOTAL PENGELUARAN</td><td>Rp</td><td class="text-right">{fmt_num(biaya_tot)}</td></tr>
</table>
</td>
</tr>
</table>

<br>
<table class="pdf-table">
<tr class="bold">
<td style="width: 25%;">TOTAL PENGELUARAN</td>
<td style="width: 5%;">Rp</td>
<td class="text-right" style="width: 20%;">{fmt_num(biaya_tot)}</td>
<td style="width: 50%;"></td>
</tr>
<tr class="bold">
<td>LABA BERSIH</td>
<td>Rp</td>
<td class="text-right">{fmt_num(laba_bersih)}</td>
<td></td>
</tr>
</table>

<br>
<div class="bold">PEMBAGIAN BAGI HASIL:</div>
<table class="pdf-table">
<tr>
<td style="width: 20%;">PROFIT SHRING</td>
<td style="width: 5%;">20%</td>
<td style="width: 3%;">X</td>
<td style="width: 15%;">{fmt_num(laba_bersih)}</td>
<td>{fmt_num(primkopasindo)} (PRIMKOPASINDO)</td>
</tr>
<tr>
<td>PROFIT SHRING</td>
<td>10%</td>
<td>X</td>
<td>{fmt_num(laba_bersih)}</td>
<td>{fmt_num(porsi_kalapas)} (PENGAWAS UPT)</td>
</tr>
<tr>
<td>PROFIT SHRING</td>
<td>10%</td>
<td>X</td>
<td>{fmt_num(laba_bersih)}</td>
<td>{fmt_num(porsi_inkopasindo)} (INKOPASINDO)</td>
</tr>
<tr>
<td>PROFIT SHRING</td>
<td>60%</td>
<td>X</td>
<td>{fmt_num(laba_bersih)}</td>
<td>{fmt_num(muffaindo2)} (CV. MUFFAINDO)</td>
</tr>
<tr class="bold">
<td colspan="3"></td>
<td>TOTAL</td>
<td>{fmt_num(laba_bersih)}</td>
</tr>
</table>

<div style="clear:both;"></div>

<div class="ttd-container">
<div>{tgl_ttd_str}</div>
<div>Penanggungjawab</div>
<div class="bold">KETUA KOPERASI</div>
<br><br><br>
<div class="bold" style="text-decoration: underline;">DANANG ANDRIYANTO</div>
</div>

<div style="clear:both;"></div>
<div style="float: right; font-size: 8pt; margin-top: 15px;">Hal 2</div>
<div style="clear:both;"></div>
</div>"""
        st.markdown(html_h2, unsafe_allow_html=True)
