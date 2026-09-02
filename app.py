import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. Konfigurasi Halaman & CSS Tema Admin POS Profesional
st.set_page_config(
    page_title="Sistem Keuangan Wartelsus - Lapas Narkotika Yogyakarta",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
    <style>
        /* Modern Admin Theme */
        .stApp {
            background-color: #f8fafc;
        }
        
        /* Custom Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #1e293b !important;
            color: #f8fafc !important;
        }
        section[data-testid="stSidebar"] .stRadio label {
            color: #cbd5e1 !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            padding: 8px 12px !important;
            border-radius: 6px !important;
        }
        section[data-testid="stSidebar"] .stRadio label:hover {
            background-color: #334155 !important;
            color: #ffffff !important;
        }

        /* Metric Cards */
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        .metric-title { font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; }
        .metric-value { font-size: 22px; color: #0f172a; font-weight: 700; margin-top: 5px; }

        /* Laporan Formatting Presisi PDF (100% Identik Acuan) */
        .pdf-page {
            background: #ffffff;
            color: #000000;
            padding: 35px 45px;
            font-family: Arial, sans-serif;
            font-size: 11pt;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
        }
        .pdf-title {
            text-align: center;
            font-weight: bold;
            font-size: 12pt;
            text-transform: uppercase;
            margin-bottom: 25px;
            line-height: 1.3;
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
            margin-top: 40px;
            float: right;
            width: 320px;
            text-align: center;
            font-size: 11pt;
        }

        @media print {
            section[data-testid="stSidebar"], 
            .stButton, 
            header, 
            footer, 
            .stTabs [role="tablist"],
            .no-print {
                display: none !important;
            }
            .main .block-container { padding: 0 !important; margin: 0 !important; }
            .pdf-page { border: none !important; padding: 0 !important; box-shadow: none !important; }
        }
    </style>
""", unsafe_allow_html=True)

# Helper Format Currency
def fmt_rupiah(val):
    try:
        val = float(val)
        return f"Rp {val:,.0f}".replace(",", ".")
    except:
        return "Rp 0"

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
    # Tabel Transaksi
    c.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            jenis TEXT, -- 'PENDAPATAN' atau 'BIAYA'
            kategori TEXT,
            keterangan TEXT,
            nominal REAL
        )
    """)
    conn.commit()

    # Seed Default Data jika kosong
    c.execute("SELECT COUNT(*) FROM transaksi")
    if c.fetchone()[0] == 0:
        default_tx = [
            ("2026-08-31", "PENDAPATAN", "WARTEL SUS", "Pendapatan Wartel Agustus 2026", 59000000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PULSA PASCA BAYAR", 2960000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "INTERNET", 1005000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "ATK", 0.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PPH 23 (2%)", 1180000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "PNBP s.d JULI 2027", 300000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "SERVER", 2243110.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "ANGSURAN PC WARTEL 8", 1000000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "INSENTIF JAGA KANTIN AGUSTUS 2026", 450000.0),
            ("2026-08-31", "BIAYA", "OPERASIONAL", "LAIN-LAIN (CHARGER + KABEL TYPE C)", 300000.0)
        ]
        c.executemany("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)", default_tx)
        conn.commit()
    conn.close()

init_db()

# 3. Sidebar Navigation UI
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0px; text-align: center;">
            <h3 style="color: #ffffff; margin: 0; font-size: 18px;">🏢 WARTELSUS KPPK</h3>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 4px;">Lapas Narkotika Yogyakarta</p>
        </div>
        <hr style="border-color: #334155; margin-bottom: 20px;">
    """, unsafe_allow_html=True)

    menu = st.radio(
        "MENU UTAMA",
        ["📊 Dashboard", "💳 Transaksi", "📄 Laporan"],
        index=0
    )

# -----------------------------------------------------------------------------
# MENU 1: DASHBOARD
# -----------------------------------------------------------------------------
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Utama Keuangan")
    st.caption("Ringkasan Seluruh Transaksi dan Grafik Tren dari Data Awal Hingga Periode Akhir")

    conn = sqlite3.connect("wartelsus_pos.db")
    df_tx = pd.read_sql_query("SELECT * FROM transaksi ORDER BY tanggal ASC, id ASC", conn)
    conn.close()

    if not df_tx.empty:
        tot_pendapatan = df_tx[df_tx['jenis'] == 'PENDAPATAN']['nominal'].sum()
        tot_biaya = df_tx[df_tx['jenis'] == 'BIAYA']['nominal'].sum()
        laba_bersih = tot_pendapatan - tot_biaya

        # Metrics Bar
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total Pendapatan</div><div class="metric-value" style="color:#10b981;">{fmt_rupiah(tot_pendapatan)}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total Biaya Operasional</div><div class="metric-value" style="color:#ef4444;">{fmt_rupiah(tot_biaya)}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Laba Bersih akumulasi</div><div class="metric-value" style="color:#0284c7;">{fmt_rupiah(laba_bersih)}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total Entry Data</div><div class="metric-value">{len(df_tx)} Transaksi</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Grafik Profesional
        col_g1, col_g2 = st.columns([6, 4])
        with col_g1:
            st.subheader("📈 Grafik Tren Keuangan")
            df_tx['tanggal_dt'] = pd.to_datetime(df_tx['tanggal'])
            df_grouped = df_tx.groupby([df_tx['tanggal_dt'].dt.strftime('%Y-%m'), 'jenis'])['nominal'].sum().reset_index()

            fig = px.bar(
                df_grouped, x='tanggal_dt', y='nominal', color='jenis',
                barmode='group',
                labels={'tanggal_dt': 'Periode Bulan', 'nominal': 'Jumlah (Rp)', 'jenis': 'Kategori'},
                color_discrete_map={'PENDAPATAN': '#10b981', 'BIAYA': '#ef4444'},
                title="Perbandingan Pendapatan vs Biaya per Bulan"
            )
            fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            st.subheader("🍰 Komposisi Biaya Operasional")
            df_biaya = df_tx[df_tx['jenis'] == 'BIAYA']
            if not df_biaya.empty:
                fig_pie = px.pie(
                    df_biaya, values='nominal', names='keterangan',
                    title="Rincian Pengeluaran Operasional",
                    hole=0.4
                )
                fig_pie.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_pie, use_container_width=True)

        # Tabel Riwayat Transaksi Seluruh Data
        st.subheader("📋 Data Riwayat Transaksi Keseluruhan")
        df_display = df_tx.copy()
        df_display['nominal'] = df_display['nominal'].apply(fmt_rupiah)
        st.dataframe(df_display[['id', 'tanggal', 'jenis', 'kategori', 'keterangan', 'nominal']], use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# MENU 2: TRANSAKSI (INPUT DATA POS)
# -----------------------------------------------------------------------------
elif menu == "💳 Transaksi":
    st.title("💳 Penginputan Data Transaksi")
    st.caption("Input data transaksi Pendapatan maupun Biaya Operasional dengan format angka otomatis")

    tab_in1, tab_in2 = st.tabs(["➕ Tambah Transaksi Baru", "📑 Kelola Data Transaksi"])

    with tab_in1:
        st.subheader("Form Entry Transaksi")
        
        c1, c2 = st.columns(2)
        with c1:
            tgl_input = st.date_input("Tanggal Transaksi", datetime.now())
            jenis_input = st.selectbox("Jenis Transaksi", ["PENDAPATAN", "BIAYA"])
            kategori_input = st.text_input("Kategori / Sumber", value="WARTEL SUS" if jenis_input == "PENDAPATAN" else "OPERASIONAL")
        
        with c2:
            ket_input = st.text_input("Keterangan Transaksi", placeholder="Contoh: Pulsa Pasca Bayar / Pendapatan Agustus")
            
            # Formatted Accounting Input (Tanpa tombol - +)
            nom_raw = st.text_input("Nominal Transaksi (Rp)", value="0", help="Ketik angka tanpa titik/koma. Otomatis terformat accounting.")
            nom_float = parse_rupiah(nom_raw)
            st.markdown(f"Format Accounting: **{fmt_rupiah(nom_float)}**")

        if st.button("💾 Simpan Transaksi", type="primary", use_container_width=True):
            if nom_float <= 0 and jenis_input == "PENDAPATAN":
                st.error("Nominal pendapatan harus lebih dari 0!")
            elif ket_input.strip() == "":
                st.error("Keterangan transaksi tidak boleh kosong!")
            else:
                conn = sqlite3.connect("wartelsus_pos.db")
                c = conn.cursor()
                c.execute("INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, nominal) VALUES (?, ?, ?, ?, ?)",
                          (str(tgl_input), jenis_input, kategori_input, ket_input.upper(), nom_float))
                conn.commit()
                conn.close()
                st.success(f"Transaksi '{ket_input.upper()}' sebesar {fmt_rupiah(nom_float)} berhasil disimpan!")
                st.rerun()

    with tab_in2:
        st.subheader("Daftar Transaksi Tersimpan")
        conn = sqlite3.connect("wartelsus_pos.db")
        df_edit = pd.read_sql_query("SELECT * FROM transaksi ORDER BY id DESC", conn)
        conn.close()

        for idx, row in df_edit.iterrows():
            c_tgl, c_jns, c_ket, c_nom, c_act = st.columns([2, 2, 4, 3, 1])
            c_tgl.write(row['tanggal'])
            c_jns.write(f"**{row['jenis']}**")
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
# MENU 3: LAPORAN (OUTPUT FISIK 100% IDENTIK PDF RESMI)
# -----------------------------------------------------------------------------
elif menu == "📄 Laporan":
    st.title("📄 Laporan Laba Rugi Resmi")
    st.caption("Cetak Laporan Keuangan Wartelsus sesuai format standar resmi")

    # Filter Periode Laporan
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([3, 3, 4])
    with col_l1:
        bulan_opt = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
        sel_bulan = st.selectbox("Bulan Laporan", bulan_opt, index=7)
    with col_l2:
        sel_tahun = st.number_input("Tahun Laporan", value=2026, min_value=2020, max_value=2030)
    with col_l3:
        sel_tgl_cetak = st.date_input("Tanggal Tanda Tangan Cetak", datetime(2026, 9, 2))
    st.markdown('</div>', unsafe_allow_html=True)

    # Fetch Data dari Database
    conn = sqlite3.connect("wartelsus_pos.db")
    df_all = pd.read_sql_query("SELECT * FROM transaksi", conn)
    conn.close()

    # Kalkulasi Otomatis dari Database[cite: 4, 5]
    pendapatan_tot = df_all[df_all['jenis'] == 'PENDAPATAN']['nominal'].sum()
    df_biaya_list = df_all[df_all['jenis'] == 'BIAYA'].to_dict('records')
    biaya_tot = sum([b['nominal'] for b in df_biaya_list])
    laba_bersih = pendapatan_tot - biaya_tot

    # Formulasi Pembagian Hal 1[cite: 4]
    porsi_lapas = 0.40 * laba_bersih
    porsi_kalapas = 0.10 * laba_bersih
    porsi_inkopasindo = 0.10 * laba_bersih
    porsi_muffaindo = 0.40 * laba_bersih

    shu = 0.325 * porsi_lapas
    ops = 0.30 * porsi_lapas
    porsi_bagian = 0.035 * porsi_lapas
    porsi_pengurus = 0.015 * porsi_lapas

    # Formulasi Pembagian Hal 2[cite: 5]
    primkopasindo = 0.20 * laba_bersih
    muffaindo2 = 0.60 * laba_bersih

    # Tombol Cetak PDF
    st.markdown('<div class="no-print" style="margin-bottom:20px;">', unsafe_allow_html=True)
    st.button("🖨️ Cetak / Print Laporan PDF", type="primary", on_click=lambda: st.components.v1.html("<script>window.parent.print();</script>", height=0))
    st.markdown('</div>', unsafe_allow_html=True)

    tab_h1, tab_h2 = st.tabs(["📄 Halaman 1 - Laporan Laba Rugi", "📄 Halaman 2 - Laporan Jasa Video Call"])

    # Helper Format Angka Laporan (Tanpa Rp)
    def fmt_num(val):
        try:
            return f"{float(val):,.0f}".replace(",", ".")
        except:
            return "0"

    tgl_ttd_str = f"Yogyakarta, {sel_tgl_cetak.strftime('%d')} {sel_bulan.capitalize()} {sel_tgl_cetak.strftime('%Y')}"

    # --- TAB HALAMAN 1 ---[cite: 4]
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

        html_h1 = f"""<div class="pdf-page">
<div style="font-size: 9pt;" class="bold">1 WARTEL SUS</div>
<div class="pdf-title">
LAPORAN LABA RUGI WARTEL MUFFAINDO<br>
LAPAS NARKOTIKA KELAS IIA YOGYAKARTA<br>
PERIODE {sel_bulan} {sel_tahun}
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

    # --- TAB HALAMAN 2 ---[cite: 5]
    with tab_h2:
        biaya_rows_h2 = ""
        for b in df_biaya_list:
            biaya_rows_h2 += f"""<tr>
<td>{b['keterangan']}</td>
<td style="width:5%;">Rp</td>
<td class="text-right" style="width:25%;">{fmt_num(b['nominal'])}</td>
</tr>"""

        html_h2 = f"""<div class="pdf-page">
<table class="pdf-table" style="margin-bottom: 15px;">
<tr><td style="width:20%;">NAMA WARTEL</td><td>: WARTEL LAPAS NARKOTIKA KELAS IIA YOGYAKARTA</td></tr>
<tr><td>ALAMAT</td><td>: JL KALIURANG KM 17 PAKEMBINANGUN PAKEM SLEMAN YOGYAKARTA</td></tr>
<tr><td>PERIODE PEMAKAIAN</td><td>: {sel_bulan} {sel_tahun}</td></tr>
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
