import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. Konfigurasi Halaman & CSS Cetak Presisi
st.set_page_config(
    page_title="Sistem Laporan Wartelsus KPPK - Lapas Narkotika Yogyakarta",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px;
            border-radius: 8px;
            color: white;
            margin-bottom: 20px;
        }
        .main-header h1 { color: white !important; margin: 0; font-size: 22px; font-weight: 700; }
        .main-header p { color: #e0e0e0 !important; margin: 5px 0 0 0; font-size: 14px; }

        /* Document Formatting Presisi 100% mirip PDF */
        .pdf-page {
            background: #ffffff;
            color: #000000;
            padding: 30px 40px;
            font-family: Arial, sans-serif;
            font-size: 11pt;
            border: 1px solid #ccc;
            margin-bottom: 20px;
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
            padding: 3px 6px;
            vertical-align: top;
        }
        .border-bottom { border-bottom: 1px solid #000; }
        .border-top { border-top: 1px solid #000; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
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
            .pdf-page { border: none !important; padding: 0 !important; }
        }
    </style>
""", unsafe_allow_html=True)

# Helper Format Angka
def fmt(val):
    try:
        val = float(val)
        return f"{val:,.0f}".replace(",", ".")
    except:
        return "0"

# 2. Database Handler
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
            rincian_biaya TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def simpan_laporan(bulan, tahun, tgl, pendapatan, biaya_list):
    conn = sqlite3.connect("wartelsus_data.db")
    c = conn.cursor()
    biaya_df = pd.DataFrame(biaya_list)
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
        return bulan, tahun, datetime.strptime(tgl, "%Y-%m-%d").date(), pendapatan, biaya_df.to_dict('records')
    return None

# Session State Init untuk List Dynamic Input
if "list_biaya" not in st.session_state:
    st.session_state.list_biaya = [
        {"nama": "PULSA PASCA BAYAR", "nominal": 2960000.0},
        {"nama": "INTERNET", "nominal": 1005000.0},
        {"nama": "ATK", "nominal": 0.0},
        {"nama": "PPH 23 (2%)", "nominal": 1180000.0},
        {"nama": "PNBP s.d JULI 2027", "nominal": 300000.0},
        {"nama": "SERVER", "nominal": 2243110.0},
        {"nama": "ANGSURAN PC WARTEL 8", "nominal": 1000000.0},
        {"nama": "INSENTIF JAGA KANTIN AGUSTUS 2026", "nominal": 450000.0},
        {"nama": "LAIN-LAIN (CHARGER + KABEL TYPE C)", "nominal": 300000.0},
    ]

# 3. Header Panel
st.markdown("""
    <div class="main-header no-print">
        <h1>📊 Sistem Laporan Laba Rugi Wartelsus KPPK</h1>
        <p>Lapas Narkotika Kelas IIA Yogyakarta — Panel Formulasi & Arsip Laporan Resmi</p>
    </div>
""", unsafe_allow_html=True)

# 4. Sidebar Navigasi & Form Digital Entry
with st.sidebar:
    st.header("📌 Menu Navigasi")
    mode_aplikasi = st.radio("Pilih Mode:", ["Formulir Input Laporan", "Lihat Laporan Bulan Lalu (Arsip)"])
    st.markdown("---")

    if mode_aplikasi == "Formulir Input Laporan":
        st.subheader("⚙️ Parameter Utama Laporan")
        col1, col2 = st.columns(2)
        with col1:
            bulan_list = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
            periode_bulan = st.selectbox("Bulan", bulan_list, index=7)
        with col2:
            periode_tahun = st.number_input("Tahun", min_value=2020, max_value=2030, value=2026)

        tanggal_laporan = st.date_input("Tanggal Cetak Laporan", datetime(2026, 9, 2))
        total_pendapatan = st.number_input("Total Pendapatan (Rp)", min_value=0.0, value=59000000.0, step=1000000.0, format="%.2f")

        st.markdown("---")
        st.subheader("📝 Formulir Digital Biaya Operasional")
        
        # Form Entry Rincian Biaya
        with st.form("form_tambah_biaya", clear_on_submit=True):
            st.caption("Tambah Komponen Biaya Baru:")
            new_nama = st.text_input("Nama Biaya Operasional")
            new_nom = st.number_input("Nominal (Rp)", min_value=0.0, step=50000.0)
            if st.form_submit_button("➕ Tambah Ke Daftar"):
                if new_nama.strip() != "":
                    st.session_state.list_biaya.append({"nama": new_nama.upper(), "nominal": new_nom})
                    st.rerun()

        st.markdown("**Daftar Biaya Operasional Saat Ini:**")
        
        biaya_temp = []
        for idx, item in enumerate(st.session_state.list_biaya):
            c_nama, c_nom, c_del = st.columns([5, 4, 1.5])
            with c_nama:
                nama_val = st.text_input(f"Nama #{idx+1}", value=item["nama"], key=f"name_{idx}", label_visibility="collapsed")
            with c_nom:
                nom_val = st.number_input(f"Nom #{idx+1}", value=float(item["nominal"]), key=f"nom_{idx}", label_visibility="collapsed", format="%.2f")
            with c_del:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.list_biaya.pop(idx)
                    st.rerun()
            biaya_temp.append({"nama": nama_val, "nominal": nom_val})

        st.session_state.list_biaya = biaya_temp

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Simpan Laporan ke Database", type="primary", use_container_width=True):
            simpan_laporan(periode_bulan, periode_tahun, tanggal_laporan, total_pendapatan, st.session_state.list_biaya)
            st.success(f"Laporan periode {periode_bulan} {periode_tahun} berhasil disimpan!")

    else:
        st.subheader("📁 Pilih Periode Laporan Lalu")
        df_periode = get_daftar_periode()
        
        if df_periode.empty:
            st.warning("Belum ada data tersimpan di database.")
            periode_bulan, periode_tahun, tanggal_laporan, total_pendapatan = "AGUSTUS", 2026, datetime(2026, 9, 2).date(), 59000000.0
        else:
            opsi_periode = {f"{row['periode_bulan']} {row['periode_tahun']}": row['id'] for _, row in df_periode.iterrows()}
            pilihan = st.selectbox("Pilih Periode Arsip:", list(opsi_periode.keys()))
            selected_id = opsi_periode[pilihan]
            
            periode_bulan, periode_tahun, tanggal_laporan, total_pendapatan, st.session_state.list_biaya = load_laporan(selected_id)
            st.info(f"Menampilkan Data Arsip Periode: **{periode_bulan} {periode_tahun}**")

# 5. Kalkulasi Angka Laporan
biaya_list = st.session_state.list_biaya
total_biaya = sum([float(x["nominal"]) for x in biaya_list])
laba_bersih = total_pendapatan - total_biaya

# Rumus Laporan 1
porsi_lapas = 0.40 * laba_bersih
porsi_kalapas = 0.10 * laba_bersih
porsi_inkopasindo = 0.10 * laba_bersih
porsi_muffaindo = 0.40 * laba_bersih

shu = 0.325 * porsi_lapas
ops = 0.30 * porsi_lapas
porsi_bagian = 0.035 * porsi_lapas
porsi_pengurus = 0.015 * porsi_lapas

# Rumus Laporan 2
primkopasindo = 0.20 * laba_bersih
muffaindo2 = 0.60 * laba_bersih

# 6. Tombol Cetak PDF
st.markdown('<div class="no-print">', unsafe_allow_html=True)
col_c1, col_c2 = st.columns([2, 8])
with col_c1:
    st.button("🖨️ Cetak Laporan / PDF", type="primary", on_click=lambda: st.components.v1.html("<script>window.parent.print();</script>", height=0))
st.markdown('</div>', unsafe_allow_html=True)

# 7. Rendering Laporan Presisi PDF
tab1, tab2 = st.tabs(["📄 Hal. 1 - Laporan Laba Rugi Wartel Muffaindo", "📄 Hal. 2 - Laporan Jasa Video Call"])

# Format Bulan Tgl Indonesia
tgl_formatted = f"Yogyakarta, {tanggal_laporan.strftime('%d')} {periode_bulan.capitalize()} {tanggal_laporan.strftime('%Y')}"

with tab1:
    biaya_rows_h1 = ""
    for idx, b in enumerate(biaya_list):
        biaya_rows_h1 += f"""
        <tr>
            <td style="width:5%;">{idx+1}</td>
            <td>{b['nama']}</td>
            <td style="width:3%;">:</td>
            <td style="width:5%;">Rp</td>
            <td class="text-right" style="width:20%;">{fmt(b['nominal'])}</td>
        </tr>
        """

    html_h1 = f"""
    <div class="pdf-page">
        <div style="font-size: 9pt;" class="bold">1 WARTEL SUS</div>
        <div class="pdf-title">
            LAPORAN LABA RUGI WARTEL MUFFAINDO<br>
            LAPAS NARKOTIKA KELAS IIA YOGYAKARTA<br>
            PERIODE {periode_bulan} {periode_tahun}
        </div>

        <table class="pdf-table">
            <tr class="bold">
                <td colspan="2">TOTAL PENDAPATAN</td>
                <td style="width:3%;">:</td>
                <td style="width:5%;">Rp</td>
                <td class="text-right" style="width:20%;">{fmt(total_pendapatan)}</td>
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
                <td class="text-right">{fmt(total_biaya)}</td>
            </tr>
            <tr><td colspan="5">&nbsp;</td></tr>
            <tr class="bold">
                <td colspan="2">PENDAPATAN BERSIH</td>
                <td>:</td>
                <td>Rp</td>
                <td class="text-right">{fmt(laba_bersih)}</td>
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
                <td class="text-right">{fmt(porsi_lapas)}</td>
            </tr>
            <tr>
                <td>2</td>
                <td>10% X PENDAPATAN BERSIH (Ka.LAPAS)</td>
                <td>:</td>
                <td>Rp</td>
                <td class="text-right">{fmt(porsi_kalapas)}</td>
            </tr>
            <tr>
                <td>3</td>
                <td>10% X IURAN 10% UNTUK INKOPASINDO</td>
                <td>:</td>
                <td>Rp</td>
                <td class="text-right">{fmt(porsi_inkopasindo)}</td>
            </tr>
            <tr>
                <td>4</td>
                <td>40% X PENDAPATAN BERSIH (MUFAINDO)</td>
                <td>:</td>
                <td>Rp</td>
                <td class="text-right">{fmt(porsi_muffaindo)}</td>
            </tr>
            <tr class="bold">
                <td></td>
                <td>TOTAL BAGI HASIL</td>
                <td>:</td>
                <td>Rp</td>
                <td class="text-right">{fmt(laba_bersih)}</td>
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
                <td class="text-right">{fmt(shu)}</td>
            </tr>
            <tr>
                <td>2</td>
                <td>OPERASIONAL KANTOR</td>
                <td>:</td>
                <td>Rp</td>
                <td class="text-right">{fmt(ops)}</td>
            </tr>
            <tr><td>3</td><td>UNTUK TU</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr><td>4</td><td>UNTUK BINADIK</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr><td>5</td><td>UNTUK KAMTIB</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr><td>6</td><td>UNTUK GIATJA</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr><td>7</td><td>UNTUK STAF KPLP</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr>
                <td>8</td>
                <td colspan="4">UNTUK 4 (Empat) RUPAM</td>
            </tr>
            <tr><td></td><td style="padding-left: 20px;">RUPAM 1</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr><td></td><td style="padding-left: 20px;">RUPAM 2</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr><td></td><td style="padding-left: 20px;">RUPAM 3</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr><td></td><td style="padding-left: 20px;">RUPAM 4</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_bagian)}</td></tr>
            <tr>
                <td>9</td>
                <td colspan="4">UNTUK PENGURUS: 4 Pegawai</td>
            </tr>
            <tr><td></td><td style="padding-left: 20px;">AGUS YULIANTO</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_pengurus)}</td></tr>
            <tr><td></td><td style="padding-left: 20px;">KPLP</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_pengurus)}</td></tr>
            <tr><td></td><td style="padding-left: 20px;">KPLP</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_pengurus)}</td></tr>
            <tr><td></td><td style="padding-left: 20px;">KPLP</td><td>:</td><td>Rp</td><td class="text-right">{fmt(porsi_pengurus)}</td></tr>
            <tr class="bold">
                <td colspan="2">TOTAL PENGELUARAN KANTOR</td>
                <td>:</td>
                <td>Rp</td>
                <td class="text-right">{fmt(porsi_lapas)}</td>
            </tr>
        </table>
        
        <div style="clear:both;"></div>
        <div style="float: right; font-size: 9pt; margin-top: 15px;">Hal. 1</div>
        <div style="clear:both;"></div>
    </div>
    """
    st.markdown(html_h1, unsafe_allow_html=True)

with tab2:
    # Generasi Komponen Operasional Hal 2
    biaya_rows_h2 = ""
    for b in biaya_list:
        biaya_rows_h2 += f"""
        <tr>
            <td>{b['nama']}</td>
            <td style="width:5%;">Rp</td>
            <td class="text-right" style="width:25%;">{fmt(b['nominal'])}</td>
        </tr>
        """

    html_h2 = f"""
    <div class="pdf-page">
        <table class="pdf-table" style="margin-bottom: 15px;">
            <tr><td style="width:20%;">NAMA WARTEL</td><td>: WARTEL LAPAS NARKOTIKA KELAS IIA YOGYAKARTA</td></tr>
            <tr><td>ALAMAT</td><td>: JL KALIURANG KM 17 PAKEMBINANGUN PAKEM SLEMAN YOGYAKARTA</td></tr>
            <tr><td>PERIODE PEMAKAIAN</td><td>: {periode_bulan} {periode_tahun}</td></tr>
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
                        <tr class="bold"><td>TOTAL</td><td>Rp</td><td class="text-right">{fmt(total_pendapatan)}</td></tr>
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
                        <tr><td>PENDAPATAN I</td><td>Rp</td><td class="text-right">{fmt(total_pendapatan)}</td></tr>
                        <tr><td>PENDAPATAN II</td><td>Rp</td><td class="text-right">0</td></tr>
                        <tr class="bold"><td>TOTAL PENDAPATAN</td><td>Rp</td><td class="text-right">{fmt(total_pendapatan)}</td></tr>
                    </table>
                </td>
                <td style="vertical-align: top;">
                    <table class="pdf-table">
                        {biaya_rows_h2}
                        <tr class="bold"><td>TOTAL PENGELUARAN</td><td>Rp</td><td class="text-right">{fmt(total_biaya)}</td></tr>
                    </table>
                </td>
            </tr>
        </table>

        <br>
        <table class="pdf-table">
            <tr class="bold">
                <td style="width: 25%;">TOTAL PENGELUARAN</td>
                <td style="width: 5%;">Rp</td>
                <td class="text-right" style="width: 20%;">{fmt(total_biaya)}</td>
                <td style="width: 50%;"></td>
            </tr>
            <tr class="bold">
                <td>LABA BERSIH</td>
                <td>Rp</td>
                <td class="text-right">{fmt(laba_bersih)}</td>
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
                <td style="width: 15%;">{fmt(laba_bersih)}</td>
                <td>{fmt(primkopasindo)} (PRIMKOPASINDO)</td>
            </tr>
            <tr>
                <td>PROFIT SHRING</td>
                <td>10%</td>
                <td>X</td>
                <td>{fmt(laba_bersih)}</td>
                <td>{fmt(porsi_kalapas)} (PENGAWAS UPT)</td>
            </tr>
            <tr>
                <td>PROFIT SHRING</td>
                <td>10%</td>
                <td>X</td>
                <td>{fmt(laba_bersih)}</td>
                <td>{fmt(porsi_inkopasindo)} (INKOPASINDO)</td>
            </tr>
            <tr>
                <td>PROFIT SHRING</td>
                <td>60%</td>
                <td>X</td>
                <td>{fmt(laba_bersih)}</td>
                <td>{fmt(muffaindo2)} (CV. MUFFAINDO)</td>
            </tr>
            <tr class="bold">
                <td colspan="3"></td>
                <td>TOTAL</td>
                <td>{fmt(laba_bersih)}</td>
            </tr>
        </table>

        <div style="clear:both;"></div>
        
        <!-- Tanda Tangan Resmi -->
        <div class="ttd-container">
            <div>{tgl_formatted}</div>
            <div>Penanggungjawab</div>
            <div class="bold">KETUA KOPERASI</div>
            <br><br><br>
            <div class="bold" style="text-decoration: underline;">DANANG ANDRIYANTO</div>
        </div>

        <div style="clear:both;"></div>
        <div style="float: right; font-size: 9pt; margin-top: 15px;">Hal. 2</div>
        <div style="clear:both;"></div>
    </div>
    """
    st.markdown(html_h2, unsafe_allow_html=True)
