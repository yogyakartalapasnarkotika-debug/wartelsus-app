import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# 1. Konfigurasi Halaman & CSS A4 Print Standard
st.set_page_config(
    page_title="WARTELSUS KPPK - LAPAS NARKOTIKA YOGYAKARTA",
    page_icon="🏢",
    layout="wide"
)

st.markdown("""
    <style>
        /* Tipografi & Warna Kontras Tinggi */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #0f172a;
        }
        
        .main {
            background-color: #f1f5f9;
        }

        /* Styling Sidebar Kontras */
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
        }
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stRadio label {
            font-size: 16px !important;
            font-weight: 700 !important;
            padding: 10px 14px !important;
            border-radius: 8px !important;
            background-color: #1e293b;
            margin-bottom: 6px;
            display: block;
        }
        section[data-testid="stSidebar"] .stRadio label:hover {
            background-color: #0284c7 !important;
            color: #ffffff !important;
        }

        /* Metric Cards */
        .metric-box {
            background-color: #ffffff;
            border: 2px solid #cbd5e1;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .metric-title { font-size: 14px; color: #475569; font-weight: 800; text-transform: uppercase; }
        .metric-value { font-size: 24px; font-weight: 900; margin-top: 8px; }

        /* Judul Kapital & Jelas */
        .page-header {
            font-size: 28px;
            font-weight: 900;
            color: #0f172a;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            border-bottom: 4px solid #0284c7;
            padding-bottom: 8px;
        }
        .section-header {
            font-size: 20px;
            font-weight: 800;
            color: #0f172a;
            text-transform: uppercase;
            margin-top: 15px;
            margin-bottom: 15px;
        }

        /* Standard Cetak PDF A4 Presisi (210mm x 297mm) */
        @media print {
            @page {
                size: A4 portrait;
                margin: 15mm;
            }
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
                width: 100% !important;
            }
            .pdf-page { 
                border: none !important; 
                padding: 0 !important; 
                box-shadow: none !important;
                width: 100% !important;
                background: white !important;
            }/* Menyembunyikan Header / Toolbar Atas Streamlit */
header[data-testid="stHeader"] {
    display: none !important;
}

/* Menghilangkan tombol opsi tambahan jika masih muncul */
#MainMenu {
    visibility: hidden;
}

/* Menghilangkan footer 'Powered by Streamlit' */
footer {
    visibility: hidden;
}
        }

        /* Form Laporan Fisik */
        .pdf-page {
            background: #ffffff;
            color: #000000;
            padding: 30px;
            font-family: Arial, sans-serif;
            font-size: 11pt;
            border: 1px solid #94a3b8;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .pdf-title {
            text-align: center;
            font-weight: bold;
            font-size: 12pt;
            text-transform: uppercase;
            margin-bottom: 20px;
            line-height: 1.4;
        }
        .pdf-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 10.5pt;
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
            width: 300px;
            text-align: center;
            font-size: 11pt;
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

# 2. Database Management
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

    # Data Seed Awal
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

# 3. Sidebar Navigation
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0px; text-align: center;">
            <h2 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 900;">🏢 WARTELSUS KPPK</h2>
            <p style="color: #38bdf8; font-size: 13px; font-weight: 700; margin-top: 4px;">LAPAS NARKOTIKA YOGYAKARTA</p>
        </div>
        <hr style="border-color: #334155; margin-bottom: 20px;">
    """, unsafe_allow_html=True)

    menu = st.radio(
        "MENU UTAMA",
        ["DASHBOARD", "TRANSAKSI", "LAPORAN"],
        index=0
    )

# -----------------------------------------------------------------------------
# MENU 1: DASHBOARD
# -----------------------------------------------------------------------------
if menu == "DASHBOARD":
    st.markdown('<div class="page-header">DASHBOARD</div>', unsafe_allow_html=True)

    conn = sqlite3.connect("wartelsus_pos.db")
    df_tx = pd.read_sql_query("SELECT * FROM transaksi ORDER BY tanggal ASC", conn)
    conn.close()

    if not df_tx.empty:
        tot_pendapatan = df_tx[df_tx['jenis'] == 'PENDAPATAN']['nominal'].sum()
        tot_biaya = df_tx[df_tx['jenis'] == 'BIAYA']['nominal'].sum()
        laba_bersih = tot_pendapatan - tot_biaya

        # Metrics Card (3 Card tanpa Total Entry Data)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-box"><div class="metric-title">TOTAL PENDAPATAN</div><div class="metric-value" style="color:#10b981;">{fmt_rupiah(tot_pendapatan)}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-box"><div class="metric-title">TOTAL BIAYA OPERASIONAL</div><div class="metric-value" style="color:#ef4444;">{fmt_rupiah(tot_biaya)}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-box"><div class="metric-title">LABA BERSIH AKUMULASI</div><div class="metric-value" style="color:#0284c7;">{fmt_rupiah(laba_bersih)}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Baris Grafik
        col_g1, col_g2 = st.columns([6, 4])
        
        with col_g1:
            st.markdown('<div class="section-header">GRAFIK</div>', unsafe_allow_html=True)
            df_tx['tanggal_dt'] = pd.to_datetime(df_tx['tanggal'])
            df_tx['bulan_tahun'] = df_tx['tanggal_dt'].dt.strftime('%b %Y')
            
            df_grouped = df_tx.groupby(['bulan_tahun', 'jenis'], sort=False)['nominal'].sum().reset_index()

            fig = px.bar(
                df_grouped, x='bulan_tahun', y='nominal', color='jenis',
                barmode='group',
                labels={'bulan_tahun': 'Bulan Laporan', 'nominal': 'Jumlah (Rp)', 'jenis': 'Jenis'},
                color_discrete_map={'PENDAPATAN': '#10b981', 'BIAYA': '#ef4444'}
            )
            fig.update_layout(
                template="plotly_white", 
                font=dict(size=13, color="#0f172a"),
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(title_text='', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            st.markdown('<div class="section-header">OPERASIONAL</div>', unsafe_allow_html=True)
            df_biaya = df_tx[df_tx['jenis'] == 'BIAYA']
            if not df_biaya.empty:
                fig_pie = px.pie(
                    df_biaya, values='nominal', names='kategori',
                    hole=0.4
                )
                fig_pie.update_layout(
                    template="plotly_white",
                    font=dict(size=12, color="#0f172a"),
                    margin=dict(l=10, r=10, t=20, b=20)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# MENU 2: TRANSAKSI
# -----------------------------------------------------------------------------
elif menu == "TRANSAKSI":
    st.markdown('<div class="page-header">TRANSAKSI</div>', unsafe_allow_html=True)

    tab_in1, tab_in2 = st.tabs(["➕ INPUT TRANSAKSI BARU", "📋 DAFTAR DATA TRANSAKSI"])

    # List Pilihan Kategori Default
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
        st.markdown('<div class="section-header">FORM ENTRY TRANSAKSI</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            tgl_input = st.date_input("Tanggal Transaksi", datetime.now())
            jenis_input = st.selectbox("Jenis Transaksi", ["BIAYA", "PENDAPATAN"])
            
            kat_selected = st.selectbox("Kategori Transaksi Pengeluaran / Pendapatan", opsi_kategori_default)
            if kat_selected == "➕ TAMBAH KATEGORI BARU...":
                kategori_input = st.text_input("Tuliskan Kategori Baru:", placeholder="Contoh: BIAYA PERBAIKAN AC").upper()
            else:
                kategori_input = kat_selected

        with c2:
            ket_input = st.text_input("Keterangan Rincian / Detail Transaksi", placeholder="Contoh: Pembayaran Internet IndiHome Bulan Agustus")
            
            nom_raw = st.text_input("Nominal Transaksi (Rp)", value="0", help="Ketik angka tanpa titik. Format otomatis accounting.")
            nom_float = parse_rupiah(nom_raw)
            st.markdown(f"Nominal Terbilang: **{fmt_rupiah(nom_float)}**")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 SIMPAN DATA TRANSAKSI", type="primary", use_container_width=True):
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

    with tab_in2:
        st.markdown('<div class="section-header">DATA TRANSAKSI TERSIMPAN</div>', unsafe_allow_html=True)
        conn = sqlite3.connect("wartelsus_pos.db")
        df_edit = pd.read_sql_query("SELECT * FROM transaksi ORDER BY tanggal DESC, id DESC", conn)
        conn.close()

        if not df_edit.empty:
            for idx, row in df_edit.iterrows():
                c_tgl, c_jns, c_kat, c_ket, c_nom, c_act = st.columns([1.5, 1.5, 2.5, 3.5, 2, 1])
                c_tgl.write(f"**{row['tanggal']}**")
                c_jns.write(f"**{row['jenis']}**")
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

# -----------------------------------------------------------------------------
# MENU 3: LAPORAN (HANYA DATA BULAN YANG DIPILIH)
# -----------------------------------------------------------------------------
elif menu == "LAPORAN":
    st.markdown('<div class="page-header">LAPORAN</div>', unsafe_allow_html=True)

    # Filter Bulan & Tahun Laporan
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([3, 3, 4])
    
    bulan_dict = {
        "JANUARI": "01", "FEBRUARI": "02", "MARET": "03", "APRIL": "04",
        "MEI": "05", "JUNI": "06", "JULI": "07", "AGUSTUS": "08",
        "SEPTEMBER": "09", "OKTOBER": "10", "NOVEMBER": "11", "DESEMBER": "12"
    }

    with col_l1:
        sel_bulan_nama = st.selectbox("PILIH BULAN LAPORAN", list(bulan_dict.keys()), index=7)
        sel_bulan_kode = bulan_dict[sel_bulan_nama]
    with col_l2:
        sel_tahun = st.number_input("PILIH TAHUN LAPORAN", value=2026, min_value=2020, max_value=2030)
    with col_l3:
        sel_tgl_cetak = st.date_input("TANGGAL CETAK LAPORAN", datetime(2026, 9, 2))
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Filter Data Hanya Berdasarkan Bulan & Tahun yang Dipilih
    periode_query = f"{sel_tahun}-{sel_bulan_kode}"
    
    conn = sqlite3.connect("wartelsus_pos.db")
    df_filtered = pd.read_sql_query(
        "SELECT * FROM transaksi WHERE strftime('%Y-%m', tanggal) = ?", 
        conn, 
        params=(periode_query,)
    )
    conn.close()

    # Kalkulasi Khusus Bulan Terpilih
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
    st.markdown('<div class="no-print" style="margin-top:15px; margin-bottom:20px;">', unsafe_allow_html=True)
    if df_filtered.empty:
        st.warning(f"⚠️ Tidak ada data transaksi untuk periode bulan **{sel_bulan_nama} {sel_tahun}**.")
    else:
        st.info(f"Showing Laporan Periode: **{sel_bulan_nama} {sel_tahun}** ({len(df_filtered)} Transaksi ditemukan)")
    
    st.button("🖨️ CETAK / PRINT LAPORAN (UKURAN A4)", type="primary", on_click=lambda: st.components.v1.html("<script>window.parent.print();</script>", height=0))
    st.markdown('</div>', unsafe_allow_html=True)

    tab_h1, tab_h2 = st.tabs(["📄 HALAMAN 1 - LAPORAN LABA RUGI", "📄 HALAMAN 2 - JASA VIDEO CALL"])

    tgl_ttd_str = f"Yogyakarta, {sel_tgl_cetak.strftime('%d')} {sel_bulan_nama.capitalize()} {sel_tgl_cetak.strftime('%Y')}"

    # --- TAB HALAMAN 1 ---
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
<div style="float: right; font-size: 9pt; margin-top: 15px;">Hal. 1</div>
<div style="clear:both;"></div>
</div>"""
        st.markdown(html_h1, unsafe_allow_html=True)

    # --- TAB HALAMAN 2 ---
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

<!-- Tanda Tangan Resmi -->
<div class="ttd-container">
<div>{tgl_ttd_str}</div>
<div>Penanggungjawab</div>
<div class="bold">KETUA KOPERASI</div>
<br><br><br>
<div class="bold" style="text-decoration: underline;">DANANG ANDRIYANTO</div>
</div>

<div style="clear:both;"></div>
<div style="float: right; font-size: 9pt; margin-top: 15px;">Hal. 2</div>
<div style="clear:both;"></div>
</div>"""
        st.markdown(html_h2, unsafe_allow_html=True)
