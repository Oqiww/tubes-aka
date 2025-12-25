import streamlit as st
import time
import sys
import random
import pandas as pd
import plotly.graph_objects as go
import tracemalloc

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Tugas Besar AKA - Presensi Mahasiswa",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎓"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 {
        background: -webkit-linear-gradient(45deg, #b91d47, #ee5253); /* Warna Merah Telkom */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold !important;
        padding-bottom: 10px;
    }
    h2, h3 { color: #e0e0e0 !important; }
    div[data-testid="stMetric"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 15px;
    }
    div[data-testid="stMetricValue"] { color: #ee5253 !important; }
    section[data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #374151; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DEFINISI ALGORITMA ---
def linear_search_iterative(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def linear_search_recursive(arr, target, index=0):
    if index >= len(arr):
        return -1
    if arr[index] == target:
        return index
    return linear_search_recursive(arr, target, index + 1)

# --- 3. SIDEBAR KONFIGURASI ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/45/Telkom_University_Logo.png", width=150) # Logo Telkom (Opsional)
    st.header("⚙️ Konfigurasi Dataset")
    
    max_n = st.number_input("Jlh Mahasiswa (N)", 100, 10000, 2000, 100)
    step_size = st.number_input("Interval Uji (Step)", 50, 1000, 200, 50)
    
    st.subheader("🎯 Skenario Pencarian")
    scenario = st.selectbox(
        "Kondisi Pencarian NIM:",
        ("Worst Case (NIM Tidak Hadir)", "Best Case (NIM Pertama)", "Average Case (NIM Acak)"),
        help="Simulasi pencarian NIM dalam daftar hadir."
    )
    
    run_btn = st.button("🚀 JALANKAN ANALISIS", type="primary", use_container_width=True)

# --- 4. HALAMAN UTAMA ---
st.title("Evaluasi Efisiensi Algoritma Linear Search")
st.markdown(f"""
**Studi Kasus:** Pencarian Log Presensi Mahasiswa Universitas Telkom
<br>**Objek Data:** Nomor Induk Mahasiswa (NIM) | **Mode:** `{scenario}`
""", unsafe_allow_html=True)

if run_btn:
    sys.setrecursionlimit(max_n + 5000)
    results = {"Jumlah Mahasiswa (N)": [], "Time Iter (ms)": [], "Time Rec (ms)": [], "Mem Iter (KB)": [], "Mem Rec (KB)": []}
    
    progress_col1, progress_col2 = st.columns([3, 1])
    with progress_col1: progress_bar = st.progress(0)
    with progress_col2: status_text = st.empty()

    range_n = range(step_size, max_n + 1, step_size)
    total_steps = len(list(range_n))
    
    for idx, n in enumerate(range_n):
        status_text.caption(f"Processing N = {n} Mahasiswa...")
        
        # --- GENERATE DATA NIM ALA TELKOM ---
        # Contoh: 1301210001 s/d 130121xxxx
        start_nim = 1301210000
        data_nim = [start_nim + i for i in range(n)]
        
        if "Worst" in scenario: target = 9999999999 # NIM Ghaib (Tidak ada)
        elif "Best" in scenario: target = data_nim[0] # NIM Paling Awal
        else: target = random.choice(data_nim) # NIM Acak
            
        # 1. Iteratif
        start = time.perf_counter()
        linear_search_iterative(data_nim, target)
        time_iter = (time.perf_counter() - start) * 1000
        
        tracemalloc.start()
        linear_search_iterative(data_nim, target)
        mem_iter = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()
        
        # 2. Rekursif
        try:
            start = time.perf_counter()
            linear_search_recursive(data_nim, target)
            time_rec = (time.perf_counter() - start) * 1000
            
            tracemalloc.start()
            linear_search_recursive(data_nim, target)
            mem_rec = tracemalloc.get_traced_memory()[1] / 1024
            tracemalloc.stop()
        except RecursionError:
            time_rec = None
            mem_rec = None
            if tracemalloc.is_tracing(): tracemalloc.stop()
            
        results["Jumlah Mahasiswa (N)"].append(n)
        results["Time Iter (ms)"].append(time_iter)
        results["Time Rec (ms)"].append(time_rec)
        results["Mem Iter (KB)"].append(mem_iter)
        results["Mem Rec (KB)"].append(mem_rec)
        progress_bar.progress((idx + 1) / total_steps)

    progress_bar.empty()
    status_text.success("✅ Analisis Selesai!")
    df = pd.DataFrame(results)

    # --- 5. DASHBOARD HASIL ---
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Sampel", f"{len(df)} Titik Uji")
    m2.metric("Max Mahasiswa (N)", f"{max_n}")
    m3.metric("Peak Time (Rekursif)", f"{df['Time Rec (ms)'].max():.4f} ms")
    m4.metric("Peak Memory (Rekursif)", f"{df['Mem Rec (KB)'].max():.2f} KB")
    
    tab_chart, tab_data, tab_analysis = st.tabs(["📊 Grafik Performa", "📋 Data Detail", "📝 Analisis & Kesimpulan"])
    
    with tab_chart:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("⏱️ Time Complexity (Waktu)")
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(x=df['Jumlah Mahasiswa (N)'], y=df['Time Iter (ms)'], name='Iteratif', line=dict(color='#00d2ff', width=3)))
            fig_t.add_trace(go.Scatter(x=df['Jumlah Mahasiswa (N)'], y=df['Time Rec (ms)'], name='Rekursif', line=dict(color='#ee5253', width=3)))
            fig_t.update_layout(template="plotly_dark", height=400, xaxis_title="Jumlah Mahasiswa (N)", yaxis_title="Waktu (ms)")
            st.plotly_chart(fig_t, use_container_width=True)
        with c2:
            st.subheader("💾 Space Complexity (Memori)")
            fig_m = go.Figure()
            fig_m.add_trace(go.Scatter(x=df['Jumlah Mahasiswa (N)'], y=df['Mem Iter (KB)'], name='Iteratif', line=dict(color='#00d2ff', width=3)))
            fig_m.add_trace(go.Scatter(x=df['Jumlah Mahasiswa (N)'], y=df['Mem Rec (KB)'], name='Rekursif', line=dict(color='#ee5253', width=3)))
            fig_m.update_layout(template="plotly_dark", height=400, xaxis_title="Jumlah Mahasiswa (N)", yaxis_title="Memori (KB)")
            st.plotly_chart(fig_m, use_container_width=True)

    with tab_data:
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={
            "Jumlah Mahasiswa (N)": st.column_config.NumberColumn(format="%d Orang"),
            "Time Iter (ms)": st.column_config.NumberColumn(format="%.4f ms"),
            "Time Rec (ms)": st.column_config.NumberColumn(format="%.4f ms"),
            "Mem Iter (KB)": st.column_config.NumberColumn(format="%.2f KB"),
            "Mem Rec (KB)": st.column_config.NumberColumn(format="%.2f KB"),
        })

    with tab_analysis:
        st.subheader(f"Analisis Studi Kasus: {scenario}")
        if "Best" in scenario:
            st.success("""
            **Analisis Best Case (NIM ditemukan di awal):**
            Pada kasus ini, pencarian NIM sangat cepat (O(1)). Baik metode Iteratif maupun Rekursif langsung menemukan data mahasiswa tanpa perlu looping panjang. Grafik memori rekursif juga rendah.
            """)
        elif "Worst" in scenario:
            st.error("""
            **Analisis Worst Case (NIM Tidak Ditemukan/Absen):**
            Sistem harus mengecek seluruh daftar mahasiswa (O(N)).
            * **Memori:** Algoritma Rekursif memakan memori besar (garis merah naik tajam) karena menumpuk data di Stack.
            * **Rekomendasi:** Untuk database mahasiswa Telkom yang besar, gunakan **Iteratif** agar server tidak crash.
            """)
        else:
            st.info("**Analisis Average Case:** Pencarian NIM secara acak menunjukkan tren linear O(N). Rekursif tetap lebih boros memori dibanding Iteratif.")

else:
    st.info("👈 Masukkan jumlah mahasiswa (N) di Sidebar, lalu klik **JALANKAN ANALISIS**.")