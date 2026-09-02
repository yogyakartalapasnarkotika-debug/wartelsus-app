import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import calendar
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="KeuanganApp - Lapas Narkotika Yogyakarta",
    page_icon="💼",
    layout="wide"
)

# Initialize Active Menu State
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "DASHBOARD"

# -----------------------------------------------------------------------------
# 2. DATABASE MANAGEMENT
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("wartelsus_pos.db")
    c = conn.cursor()
    
    # Tabel Transaksi
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
    
    # Tabel Users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nama_lengkap TEXT,
            role TEXT
        )
    """)
    
    # User Default
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        default_users = [
            ("admin", "admin123", "Ahmad Jhony", "Admin"),
            ("user1", "user123", "Staf Keuangan", "User")
        ]
        c.executemany("INSERT INTO users (username, password, nama_lengkap, role) VALUES (?, ?, ?, ?)", default_users)
    
    # Data Default Transaksi
    c.execute("SELECT COUNT(*) FROM transaksi")
    if c.fetchone()[0] == 0:
        default_tx = [
            ("2026-08-31", "PENDAPATAN", "PENDAPATAN WARTELSUS", "PENDAPATAN WARTELSUS AGUSTUS", 59000000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PULSA PASCA BAYAR", 2960000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "TAGIHAN TELEPON & INTERNET", 1005000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "ATK", 0.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PAJAK (PPH 23 2%)", 1180000.0),
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
# 3. SESI AUTENTIKASI & LOGIN
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.nama_lengkap = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Login KeuanganApp</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        if st.button("LOG IN", type="primary", use_container_width=True):
            conn = sqlite3.connect("wartelsus_pos.db")
            c = conn.cursor()
            c.execute("SELECT username, nama_lengkap, role FROM users WHERE username=? AND password=?", (username_input, password_input))
            user = c.fetchone()
            conn.close()
            
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.nama_lengkap = user[1]
                st.session_state.role = user[2]
                st.rerun()
            else:
                st.error("Username atau password salah!")
    st.stop()

# -----------------------------------------------------------------------------
# 4. CSS STYLING & HELPER FUNCTIONS
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Source Sans Pro', 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
            background-color: #f4f6f9 !important;
        }

        /* HILANGKAN FOOTER, "HOSTED WITH STREAMLIT", DAN STATUS BADGE */
        footer, 
        [data-testid="stStatusWidget"],
        .viewerBadge_container__1A51w,
        div[class*="viewerBadge"],
        a[href*="streamlit.io"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        /* HILANGKAN FLOATING TOOLBAR DATAFRAME */
        [data-testid="stElementToolbar"], 
        .stElementToolbar,
        div[data-testid="stDataFrameResizable"] > div:first-child > div:nth-child(2) {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        header, [data-testid="stHeader"], [data-testid="stToolbar"],
        .stAppHeader, #MainMenu {
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

        /* TOP NAVBAR */
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

        /* DESAIN SIDEBAR */
        section[data-testid="stSidebar"] { 
            background-color: #222d32 !important; 
            width: 250px !important; 
        }
        section[data-testid="stSidebar"] * { 
            color: #b8c7ce !important; 
        }
        
        .user-panel { 
            padding: 15px 12px; 
            display: flex; 
            align-items: center; 
            gap: 12px; 
            border-bottom: 1px solid #1a2226; 
            margin-bottom: 10px;
        }
        .user-avatar-img { 
            width: 45px; 
            height: 45px; 
            border-radius: 50%; 
            background-color: #5b9bd5; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 24px; 
            color: #fff;
            border: 2px solid #ffffff33;
        }
        .user-info-box { 
            display: flex;
            flex-direction: column;
        }
        .user-name-text { 
            font-size: 14px; 
            font-weight: 700; 
            color: #ffffff !important; 
            line-height: 1.2;
        }
        .user-online-status { 
            font-size: 11px; 
            color: #b8c7ce !important; 
            margin-top: 3px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .online-dot {
            height: 9px;
            width: 9px;
            background-color: #00a65a;
            border-radius: 50%;
            display: inline-block;
        }

        .nav-header {
            padding: 10px 12px 5px 12px; 
            font-size: 11px; 
            font-weight: bold; 
            color: #4b646f !important;
            letter-spacing: 0.5px;
        }

        div[data-testid="stRadio"] > div {
            gap: 2px !important;
        }
        div[data-testid="stRadio"] label {
            padding: 10px 15px !important;
            border-radius: 0px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.3px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #1e282c !important;
            color: #ffffff !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] {
            background-color: #1e282c !important;
            color: #ffffff !important;
            border-left: 3px solid #3c8dbc !important;
        }

        /* BOX COMPONENTS TANPA MORE INFO */
        .small-box {
            border-radius: 3px; position: relative; display: block; margin-bottom: 15px;
            box-shadow: 0 1px 1px rgba(0,0,0,0.1); color: #ffffff !important; padding: 18px 15px;
        }
        .small-box-green { background-color: #00a65a !important; }
        .small-box-blue { background-color: #00c0ef !important; }
        .small-box-orange { background-color: #f39c12 !important; }
        .small-box-black { background-color: #222d32 !important; }
        .small-box-red { background-color: #dd4b39 !important; }
        
        .small-box .inner h3 { font-size: 18px; font-weight: bold; margin: 0 0 5px 0; white-space: nowrap; padding: 0; color: #fff !important;}
        .small-box .inner p { font-size: 12px; margin: 0; color: #fff !important; opacity: 0.9; }
        .small-box .icon-bg { position: absolute; top: 12px; right: 12px; z-index: 0; font-size: 36px; color: rgba(0, 0, 0, 0.15); }

        .box-container {
            background: #ffffff; border-top: 3px solid #3c8dbc; border-radius: 3px;
            padding: 15px; margin-bottom: 20px; box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        }
        .box-header { font-size: 16px; font-weight: 600; color: #444; border-bottom: 1px solid #f4f4f4; padding-bottom: 8px; margin-bottom: 12px; }

        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { 
            -webkit-appearance: none; 
            margin: 0; 
        }
        input[type=number] { -moz-appearance: textfield; }
    </style>
""", unsafe_allow_html=True)

# Helper Format Akuntansi Rupiah & Angka
def fmt_rupiah(val):
    try:
        return f"Rp {float(val):,.0f}".replace(",", ".")
    except:
        return "Rp 0"

def fmt_num(val):
    try:
        return f"{float(val):,.0f}".replace(",", ".")
    except:
        return "0"

# -----------------------------------------------------------------------------
# 5. SIDEBAR & NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
        <div class="user-panel">
            <div class="user-avatar-img">👤</div>
            <div class="user-info-box">
                <div class="user-name-text">{st.session_state.nama_lengkap}</div>
                <div class="user-online-status"><span class="online-dot"></span> Online</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="nav-header">MAIN NAVIGATION</div>', unsafe_allow_html=True)
    
    if st.session_state.role == "Admin":
        menu_options = [
            "📊 DASHBOARD", 
            "📁 TRANSAKSI POS", 
            "👥 DATA PENGGUNA", 
            "📄 LAPORAN KEUANGAN"
        ]
    else:
        menu_options = [
            "📊 DASHBOARD", 
            "📄 LAPORAN KEUANGAN"
        ]

    default_idx = 0
    for idx, opt in enumerate(menu_options):
        if st.session_state.active_menu in opt:
            default_idx = idx
            break

    selected_menu = st.radio("", menu_options, index=default_idx, label_visibility="collapsed")
    
    if "DASHBOARD" in selected_menu:
        st.session_state.active_menu = "DASHBOARD"
    elif "TRANSAKSI POS" in selected_menu:
        st.session_state.active_menu = "TRANSAKSI POS"
    elif "DATA PENGGUNA" in selected_menu:
        st.session_state.active_menu = "DATA PENGGUNA"
    elif "LAPORAN KEUANGAN" in selected_menu:
        st.session_state.active_menu = "LAPORAN KEUANGAN"

    menu = st.session_state.active_menu

    st.write("---")
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

st.markdown(f"""
    <div class="admin-navbar">
        <div class="admin-navbar-brand">KeuanganApp</div>
        <div class="admin-navbar-user">{st.session_state.nama_lengkap} - {st.session_state.role.lower()}</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. MENU: DASHBOARD
# -----------------------------------------------------------------------------
if menu == "DASHBOARD":
    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <span style="font-size:20px; font-weight:600; color:#333;">Dashboard <small style="font-size:12px; color:#777;">Control panel</small></span>
            <span style="font-size:12px; color:#777;">🏠 Home > Dashboard</span>
        </div>
    """, unsafe_allow_html=True)

    conn = sqlite3.connect("wartelsus_pos.db")
    df_all = pd.read_sql_query("SELECT * FROM transaksi", conn)
    conn.close()

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    month_str = now.strftime("%Y-%m")
    year_str = now.strftime("%Y")

    df_in = df_all[df_all['jenis'] == 'PENDAPATAN']
    df_out = df_all[df_all['jenis'] == 'BIAYA']

    # Akumulasi Pemasukan
    in_today = df_in[df_in['tanggal'] <= today_str]['nominal'].sum()
    in_month = df_in[df_in['tanggal'].str.startswith(month_str) & (df_in['tanggal'] <= today_str)]['nominal'].sum()
    in_year = df_in[df_in['tanggal'].str.startswith(year_str) & (df_in['tanggal'] <= today_str)]['nominal'].sum()
    in_total = df_in['nominal'].sum()

    # Akumulasi Pengeluaran
    out_today = df_out[df_out['tanggal'] <= today_str]['nominal'].sum()
    out_month = df_out[df_out['tanggal'].str.startswith(month_str) & (df_out['tanggal'] <= today_str)]['nominal'].sum()
    out_year = df_out[df_out['tanggal'].str.startswith(year_str) & (df_out['tanggal'] <= today_str)]['nominal'].sum()
    out_total = df_out['nominal'].sum()

    # PEMASUKAN BOXES (TANPA TULISAN/TOMBOL MORE INFO)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="small-box small-box-green"><div class="inner"><h3>{fmt_rupiah(in_today)}</h3><p>Pemasukan Hari Ini</p></div><div class="icon-bg">📊</div></div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="small-box small-box-blue"><div class="inner"><h3>{fmt_rupiah(in_month)}</h3><p>Pemasukan Bulan Ini</p></div><div class="icon-bg">📊</div></div>', unsafe_allow_html=True)

    with c3:
        st.markdown(f'<div class="small-box small-box-orange"><div class="inner"><h3>{fmt_rupiah(in_year)}</h3><p>Pemasukan Tahun Ini</p></div><div class="icon-bg">📊</div></div>', unsafe_allow_html=True)

    with c4:
        st.markdown(f'<div class="small-box small-box-black"><div class="inner"><h3>{fmt_rupiah(in_total)}</h3><p>Seluruh Pemasukan</p></div><div class="icon-bg">📊</div></div>', unsafe_allow_html=True)

    # PENGELUARAN BOXES (TANPA TULISAN/TOMBOL MORE INFO)
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(f'<div class="small-box small-box-red"><div class="inner"><h3>{fmt_rupiah(out_today)}</h3><p>Pengeluaran Hari Ini</p></div><div class="icon-bg">📉</div></div>', unsafe_allow_html=True)

    with c6:
        st.markdown(f'<div class="small-box small-box-red"><div class="inner"><h3>{fmt_rupiah(out_month)}</h3><p>Pengeluaran Bulan Ini</p></div><div class="icon-bg">📉</div></div>', unsafe_allow_html=True)

    with c7:
        st.markdown(f'<div class="small-box small-box-red"><div class="inner"><h3>{fmt_rupiah(out_year)}</h3><p>Pengeluaran Tahun Ini</p></div><div class="icon-bg">📉</div></div>', unsafe_allow_html=True)

    with c8:
        st.markdown(f'<div class="small-box small-box-black"><div class="inner"><h3>{fmt_rupiah(out_total)}</h3><p>Seluruh Pengeluaran</p></div><div class="icon-bg">📉</div></div>', unsafe_allow_html=True)

    col_chart, col_cal = st.columns([7, 3])
    with col_chart:
        st.markdown('<div class="box-container"><div class="box-header">Grafik Data Pemasukan & Pengeluaran Per Bulan</div>', unsafe_allow_html=True)
        if not df_all.empty:
            df_chart = df_all.groupby(['jenis'])['nominal'].sum().reset_index()
            fig = px.bar(df_chart, x='jenis', y='nominal', color='jenis',
                         color_discrete_map={'PENDAPATAN': '#00a65a', 'BIAYA': '#dd4b39'}, text_auto=True)
            fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data transaksi.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cal:
        st.markdown('<div class="box-container"><div class="box-header" style="background:#00a65a; color:#fff; padding:6px 10px; margin:-15px -15px 10px -15px;">📅 Kalender</div>', unsafe_allow_html=True)
        cal_html = calendar.HTMLCalendar().formatmonth(now.year, now.month)
        st.markdown(f"<div style='font-size:12px;'>{cal_html}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. MENU: TRANSAKSI POS
# -----------------------------------------------------------------------------
elif menu == "TRANSAKSI POS" and st.session_state.role == "Admin":
    st.markdown('<div class="box-container"><div class="box-header">Input Transaksi Keuangan</div>', unsafe_allow_html=True)

    jenis_selected = st.selectbox("Jenis Transaksi", ["PENDAPATAN", "BIAYA"])

    if jenis_selected == "BIAYA":
        kategori_options = ["OPERASIONAL", "LAIN-LAIN"]
        preset_keterangan = [
            "PAJAK (PPH 23 2%)",
            "PNBP",
            "TAGIHAN TELEPON & INTERNET",
            "SERVER",
            "ATK",
            "PULSA PASCA BAYAR",
            "ANGSURAN PC WARTEL",
            "INSENTIF JAGA KANTIN",
            "PERBAIKAN / PEMELIHARAAN ALAT",
            "+ Tambah Keterangan Baru..."
        ]
    else:
        kategori_options = ["PENDAPATAN WARTELSUS"]
        preset_keterangan = [
            "PENDAPATAN WARTELSUS",
            "PENDAPATAN VIDEO CALL",
            "PENDAPATAN LAIN-LAIN",
            "+ Tambah Keterangan Baru..."
        ]

    kategori_selected = st.selectbox("Kategori Transaksi", kategori_options)
    ket_choice = st.selectbox("Pilih / Tambah Keterangan Transaksi", preset_keterangan)

    if ket_choice == "+ Tambah Keterangan Baru...":
        ket_final = st.text_input("Ketikkan Keterangan Baru:")
    else:
        ket_final = ket_choice

    col_tgl, col_nom = st.columns(2)
    with col_tgl:
        tgl_transaksi = st.date_input("Tanggal Transaksi", datetime.now())
    with col_nom:
        nominal_raw = st.number_input("Nominal Transaksi (Rp)", min_value=0, step=10000, value=100000)
        st.caption(f"Format Akuntansi: **{fmt_rupiah(nominal_raw)}**")

    if st.button("💾 Simpan Transaksi POS", type="primary"):
        if nominal_raw > 0 and ket_final.strip() != "":
            conn = sqlite3.connect("wartelsus_pos.db")
            c = conn.cursor()
            c.execute("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)",
                      (tgl_transaksi.strftime('%Y-%m-%d'), jenis_selected, kategori_selected, ket_final, float(nominal_raw)))
            conn.commit()
            conn.close()
            st.success("✅ Transaksi berhasil disimpan!")
            st.rerun()
        else:
            st.warning("⚠️ Mohon lengkapi nominal dan keterangan transaksi.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="box-container"><div class="box-header">Riwayat Transaksi Terdaftar</div>', unsafe_allow_html=True)
    conn = sqlite3.connect("wartelsus_pos.db")
    df_riwayat = pd.read_sql_query("SELECT id, tanggal, jenis, kategori, keterangan, nominal FROM transaksi ORDER BY id DESC", conn)
    conn.close()
    
    if not df_riwayat.empty:
        df_riwayat_display = df_riwayat.copy()
        # Format Murni Angka Ribuan Tanpa "Rp"
        df_riwayat_display['nominal'] = df_riwayat_display['nominal'].apply(lambda x: fmt_num(x))
        
        # Konfigurasi Kolom dengan Rata Kanan pada Nominal
        st.dataframe(
            df_riwayat_display,
            column_config={
                "id": st.column_config.NumberColumn("ID", format="%d"),
                "tanggal": "Tanggal",
                "jenis": "Jenis",
                "kategori": "Kategori",
                "keterangan": "Keterangan",
                "nominal": st.column_config.TextColumn(
                    "Nominal",
                    help="Nominal Transaksi (Format Ribuan)",
                    width="medium"
                )
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Belum ada data transaksi.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. MENU: DATA PENGGUNA
# -----------------------------------------------------------------------------
elif menu == "DATA PENGGUNA" and st.session_state.role == "Admin":
    st.markdown('<div class="box-container"><div class="box-header">Pendaftaran User Baru</div>', unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        new_username = st.text_input("Username Baru")
        new_password = st.text_input("Password", type="password")
    with col_u2:
        new_fullname = st.text_input("Nama Lengkap")
        new_role = st.selectbox("Role / Level Hak Akses", ["User", "Admin"])

    if st.button("➕ Daftarkan Pengguna", type="primary"):
        if new_username.strip() != "" and new_password.strip() != "":
            try:
                conn = sqlite3.connect("wartelsus_pos.db")
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password, nama_lengkap, role) VALUES (?, ?, ?, ?)",
                          (new_username, new_password, new_fullname, new_role))
                conn.commit()
                conn.close()
                st.success(f"✅ User '{new_username}' berhasil didaftarkan sebagai {new_role}!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("⚠️ Username sudah terdaftar, gunakan username lain.")
        else:
            st.warning("⚠️ Lengkapi username dan password.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="box-container"><div class="box-header">Daftar Pengguna Sistem & Aksi (Edit / Hapus)</div>', unsafe_allow_html=True)
    
    conn = sqlite3.connect("wartelsus_pos.db")
    c = conn.cursor()
    c.execute("SELECT id, username, nama_lengkap, role, password FROM users")
    users_list = c.fetchall()
    conn.close()

    st.markdown("""
        <table style="width:100%; border-collapse:collapse; font-size:13px; font-weight:bold; margin-bottom:10px;">
            <tr style="background:#f4f6f9; border-bottom:2px solid #ddd; text-align:left;">
                <th style="padding:8px; width:10%;">ID</th>
                <th style="padding:8px; width:25%;">USERNAME</th>
                <th style="padding:8px; width:35%;">NAMA LENGKAP</th>
                <th style="padding:8px; width:15%;">ROLE</th>
                <th style="padding:8px; width:15%; text-align:center;">AKSI</th>
            </tr>
        </table>
    """, unsafe_allow_html=True)

    for u in users_list:
        u_id, u_user, u_nama, u_role, u_pass = u
        
        c_id, c_usr, c_nam, c_rol, c_act = st.columns([1, 2.5, 3.5, 1.5, 1.5])
        with c_id:
            st.write(f"#{u_id}")
        with c_usr:
            st.write(u_user)
        with c_nam:
            st.write(u_nama)
        with c_rol:
            st.write(f"**{u_role}**")
        with c_act:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                edit_pressed = st.button("✏️", key=f"edit_btn_{u_id}", help="Edit User")
            with btn_col2:
                del_pressed = st.button("🗑️", key=f"del_btn_{u_id}", help="Hapus User")

        if f"show_edit_{u_id}" not in st.session_state:
            st.session_state[f"show_edit_{u_id}"] = False

        if edit_pressed:
            st.session_state[f"show_edit_{u_id}"] = not st.session_state[f"show_edit_{u_id}"]

        if st.session_state[f"show_edit_{u_id}"]:
            with st.expander(f"📝 Form Edit User #{u_id} ({u_user})", expanded=True):
                e_nama = st.text_input("Nama Lengkap", value=u_nama, key=f"e_nama_{u_id}")
                e_pass = st.text_input("Password Baru (Kosongkan jika tidak diubah)", type="password", key=f"e_pass_{u_id}")
                e_role = st.selectbox("Role", ["User", "Admin"], index=0 if u_role == "User" else 1, key=f"e_role_{u_id}")
                
                if st.button("💾 Simpan Perubahan", key=f"save_edit_{u_id}", type="primary"):
                    conn = sqlite3.connect("wartelsus_pos.db")
                    c = conn.cursor()
                    if e_pass.strip() != "":
                        c.execute("UPDATE users SET nama_lengkap=?, role=?, password=? WHERE id=?", (e_nama, e_role, e_pass, u_id))
                    else:
                        c.execute("UPDATE users SET nama_lengkap=?, role=? WHERE id=?", (e_nama, e_role, u_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ Data user berhasil diperbarui!")
                    st.session_state[f"show_edit_{u_id}"] = False
                    st.rerun()

        if del_pressed:
            if u_user == st.session_state.username:
                st.error("⚠️ Anda tidak bisa menghapus akun anda sendiri yang sedang digunakan!")
            else:
                conn = sqlite3.connect("wartelsus_pos.db")
                c = conn.cursor()
                c.execute("DELETE FROM users WHERE id=?", (u_id,))
                conn.commit()
                conn.close()
                st.success(f"🗑️ User #{u_id} ({u_user}) berhasil dihapus!")
                st.rerun()

        st.markdown("<hr style='margin:5px 0; border:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. MENU: LAPORAN KEUANGAN
# -----------------------------------------------------------------------------
elif menu == "LAPORAN KEUANGAN":
    st.markdown('<div class="box-container"><div class="box-header">Filter & Parameter Cetak Laporan</div>', unsafe_allow_html=True)
    
    c_f1, c_f2, c_f3, c_f4 = st.columns([2.5, 2.5, 3, 4])
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
    with c_f4:
        nama_ttd = st.text_input("NAMA PENANDATANGAN / KETUA", value="DANANG ANDRIYANTO")
        
    st.markdown('</div>', unsafe_allow_html=True)

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

    tab_h1, tab_h2 = st.tabs(["📄 Halaman 1 - Laba Rugi", "📄 Halaman 2 - Jasa Video Call"])
    tgl_ttd_str = f"Yogyakarta, {sel_tgl_cetak.strftime('%d')} {sel_bulan_nama.capitalize()} {sel_tgl_cetak.strftime('%Y')}"

    doc_style = """
    <style>
        @page { 
            size: A4 portrait; 
            margin-top: 2.54cm; 
            margin-bottom: 2.54cm; 
            margin-left: 1.5cm; 
            margin-right: 1.5cm; 
        }
        body { font-family: Arial, sans-serif; font-size: 9pt; color: #000; margin:0; padding:0; background:#fff; }
        .pdf-page { width: 100%; max-width: 210mm; background: #fff; padding: 0; box-sizing: border-box; }
        .pdf-header-code { font-size: 10pt; font-weight: bold; margin-bottom: 8px; }
        .pdf-title { text-align: center; font-weight: bold; font-size: 11pt; text-transform: uppercase; margin-bottom: 12px; line-height: 1.3; }
        
        .report-table { width: 100%; border-collapse: collapse; font-size: 9pt; color: #000; table-layout: fixed; }
        .report-table td { padding: 2px 3px; vertical-align: top; }
        .num-col { width: 4%; text-align: left; }
        .label-col { width: 56%; }
        .sep-col { width: 3%; text-align: center; }
        .currency-col { width: 7%; text-align: left; }
        .val-col { width: 30%; text-align: right; }
        
        .text-right { text-align: right !important; }
        .bold { font-weight: bold !important; }
        .indent-1 { padding-left: 18px !important; }
        
        .ttd-wrapper { margin-top: 15px; width: 100%; display: flex; justify-content: flex-end; }
        .ttd-box { width: 280px; text-align: center; font-size: 9pt; color: #000; float: right; }
        .page-footer { margin-top: 10px; text-align: right; font-size: 8.5pt; color: #000; }
        
        .btn-print { background-color: #00a65a; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-bottom: 15px; }
        @media print { .btn-print { display: none !important; } }
    </style>
    """

    # HALAMAN 1
    with tab_h1:
        df_ops_items = df_biaya_all[df_biaya_all['kategori'] != 'LAIN-LAIN'].to_dict('records')
        df_lain_items = df_biaya_all[df_biaya_all['kategori'] == 'LAIN-LAIN'].to_dict('records')

        biaya_rows_h1 = ""
        idx_count = 1
        for b in df_ops_items:
            biaya_rows_h1 += f"<tr><td class='num-col'>{idx_count}</td><td class='label-col'>{b['keterangan']}</td><td class='sep-col'>:</td><td class='currency-col'>Rp</td><td class='val-col'>{fmt_num(b['nominal'])}</td></tr>"
            idx_count += 1

        for b in df_lain_items:
            biaya_rows_h1 += f"<tr><td class='num-col'>{idx_count}</td><td class='label-col'>{b['keterangan']}</td><td class='sep-col'>:</td><td class='currency-col'>Rp</td><td class='val-col'>{fmt_num(b['nominal'])}</td></tr>"
            idx_count += 1

        html_h1 = f"""
        <!DOCTYPE html>
        <html>
        <head>{doc_style}</head>
        <body>
            <button class="btn-print" onclick="window.print()">🖨️ CETAK DOKUMEN HALAMAN 1</button>
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
            </div>
        </body>
        </html>
        """
        components.html(html_h1, height=950, scrolling=True)

    # HALAMAN 2
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
        <!DOCTYPE html>
        <html>
        <head>{doc_style}</head>
        <body>
            <button class="btn-print" onclick="window.print()">🖨️ CETAK DOKUMEN HALAMAN 2</button>
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

                <table class="report-table" style="margin-bottom: 10px;">
                    <tr>
                        <td style="width: 48%; vertical-align: top; padding-right: 10px;">
                            <div class="bold" style="margin-bottom: 4px;">PENDAPATAN I:</div>
                            <table class="report-table">
                                <tr><td style="width: 50%;">KBU 1</td><td style="width: 10%;">Rp</td><td class="text-right">0</td></tr>
                                <tr><td>KBU 2</td><td>Rp</td><td class="text-right">0</td></tr>
                                <tr><td>KBU 3</td><td>Rp</td><td class="text-right">0</td></tr>
                                <tr class="bold" style="border-top: 1px solid #ccc;">
                                    <td>TOTAL I</td><td>Rp</td><td class="text-right">{fmt_num(pendapatan_tot)}</td>
                                </tr>
                            </table>
                        </td>

                        <td style="width: 4%;"></td>

                        <td style="width: 48%; vertical-align: top; padding-left: 10px;">
                            <div class="bold" style="margin-bottom: 4px;">PENDAPATAN II:</div>
                            <table class="report-table">
                                <tr><td style="width: 50%;">KBU 4</td><td style="width: 10%;">Rp</td><td class="text-right">0</td></tr>
                                <tr><td>KBU 5</td><td>Rp</td><td class="text-right">0</td></tr>
                                <tr><td>KBU 6</td><td>Rp</td><td class="text-right">0</td></tr>
                                <tr class="bold" style="border-top: 1px solid #ccc;">
                                    <td>TOTAL II</td><td>Rp</td><td class="text-right">0</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>

                <table class="report-table" style="border-top: 1px solid #000; border-bottom: 1px solid #000; margin-bottom: 12px; padding: 3px 0;">
                    <tr class="bold">
                        <td style="width: 70%;">TOTAL PENDAPATAN (PENDAPATAN I + PENDAPATAN II)</td>
                        <td style="width: 5%;">Rp</td>
                        <td class="text-right" style="width: 25%;">{fmt_num(pendapatan_tot)}</td>
                    </tr>
                </table>

                <div class="bold" style="margin-bottom: 4px;">PENGELUARAN:</div>
                <table class="report-table" style="width: 70%;">
                    {rows_ops_h2}
                    <tr class="bold"><td colspan="3" style="padding-top:4px;">LAIN-LAIN:</td></tr>
                    {rows_lain_h2}
                </table>

                <table class="report-table" style="margin-top: 8px; border-top: 1px dashed #000; padding-top: 4px; width: 70%;">
                    <tr class="bold">
                        <td style="width: 50%;">TOTAL PENGELUARAN</td>
                        <td style="width: 5%;">Rp</td>
                        <td class="text-right" style="width: 45%;">{fmt_num(biaya_tot)}</td>
                    </tr>
                    <tr class="bold">
                        <td>LABA BERSIH</td>
                        <td>Rp</td>
                        <td class="text-right">{fmt_num(laba_bersih)}</td>
                    </tr>
                </table>

                <div class="bold" style="margin-top: 15px; margin-bottom: 4px;">PEMBAGIAN BAGI HASIL:</div>
                <table class="report-table" style="width: 85%; line-height: 1.2;">
                    <tr>
                        <td style="width: 18%;">PROFIT SHARING</td>
                        <td style="width: 6%;">20%</td>
                        <td style="width: 2%;">X</td>
                        <td style="width: 18%;">Rp {fmt_num(laba_bersih)}</td>
                        <td style="width: 3%; text-align:center;">=</td>
                        <td style="width: 18%;">Rp {fmt_num(primkopasindo)}</td>
                        <td>(PRIMKOPASINDO)</td>
                    </tr>
                    <tr>
                        <td>PROFIT SHARING</td>
                        <td>10%</td>
                        <td>X</td>
                        <td>Rp {fmt_num(laba_bersih)}</td>
                        <td style="text-align:center;">=</td>
                        <td>Rp {fmt_num(porsi_kalapas)}</td>
                        <td>(PENGAWAS UPT)</td>
                    </tr>
                    <tr>
                        <td>PROFIT SHARING</td>
                        <td>10%</td>
                        <td>X</td>
                        <td>Rp {fmt_num(laba_bersih)}</td>
                        <td style="text-align:center;">=</td>
                        <td>Rp {fmt_num(porsi_inkopasindo)}</td>
                        <td>(INKOPASINDO)</td>
                    </tr>
                    <tr>
                        <td>PROFIT SHARING</td>
                        <td>60%</td>
                        <td>X</td>
                        <td>Rp {fmt_num(laba_bersih)}</td>
                        <td style="text-align:center;">=</td>
                        <td>Rp {fmt_num(muffaindo2)}</td>
                        <td>(CV. MUFFAINDO)</td>
                    </tr>
                    <tr class="bold" style="border-top: 1px solid #ccc;">
                        <td colspan="3">TOTAL BAGI HASIL</td>
                        <td>Rp {fmt_num(laba_bersih)}</td>
                        <td style="text-align:center;">=</td>
                        <td>Rp {fmt_num(laba_bersih)}</td>
                        <td></td>
                    </tr>
                </table>

                <div class="ttd-wrapper">
                    <div class="ttd-box">
                        <div>{tgl_ttd_str}</div>
                        <div>Penanggungjawab</div>
                        <div class="bold" style="margin-top:2px;">KETUA KOPERASI</div>
                        <br><br>
                        <div class="bold" style="text-decoration: underline;">{nama_ttd.upper()}</div>
                    </div>
                </div>

                <div style="clear:both;"></div>
                <div class="page-footer">Hal. 2</div>
            </div>
        </body>
        </html>
        """
        components.html(html_h2, height=950, scrolling=True)
