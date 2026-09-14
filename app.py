import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Archival Vault Manager | Aa Baroq Applied Technologies",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM PROFESSIONAL STYLING (FULL DARK MODE + SIDEBAR FIX) ---
st.markdown("""
    <style>
    /* Paksa seluruh aplikasi, header, kontainer utama, dan sidebar menjadi gelap total */
    .stApp, .main, [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        color: #ffffff !important;
    }
    /* Pastikan seluruh teks dan label di dalam sidebar menjadi terang */
    [data-testid="stSidebar"] * {
        color: #f0f6fc !important;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
    .stMetric label {
        color: #8b949e !important;
        font-size: 0.9em !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    h1, h2, h3 {
        color: #79c0ff !important;
    }
    p, span, label, .streamlit-expanderHeader, div[data-testid="stMarkdownContainer"] {
        color: #f0f6fc !important;
    }
    .brand-footer {
        text-align: center;
        color: #8b949e;
        font-size: 0.85em;
        margin-top: 50px;
        border-top: 1px solid #30363d;
        padding-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("🏛️ Archival Vault Manager")
st.markdown("**No. 73 | High-Density Tick-by-Tick Quant & Institutional Storage Engine**")
st.markdown("---")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Vault Operations")
selected_symbol = st.sidebar.selectbox("Select Asset Symbol", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSDT", "COMPOSITE.JK"])
action_mode = st.sidebar.radio("Navigation", ["📊 Vault Dashboard", "📥 Ingest Tick Stream", "🔍 Historical Backtest Query", "⚙️ Storage Diagnostics"])

# --- SESSION STATE INITIALIZATION FOR SIMULATED VAULT ---
if "vault_db" not in st.session_state:
    np.random.seed(42)
    timestamps = pd.date_range(start="2026-09-01 09:00:00", periods=500, freq="s")
    base_price = 1.0850 if "USD" in selected_symbol else (2500.0 if "XAU" in selected_symbol else 6500.0)
    prices = base_price + np.cumsum(np.random.randn(500) * 0.0002)
    volumes = np.random.randint(100, 5000, size=500)
    
    st.session_state["vault_db"] = pd.DataFrame({
        "timestamp": timestamps,
        "symbol": selected_symbol,
        "price": prices,
        "volume": volumes
    })

df_vault = st.session_state["vault_db"]

# --- DASHBOARD VIEW ---
if action_mode == "📊 Vault Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Stored Records", f"{len(df_vault):,}")
    with col2:
        st.metric("Compression Ratio", "84.2% (Parquet)")
    with col3:
        st.metric("Average Read Latency", "1.4 ms")
    with col4:
        st.metric("Vault Status", "🟢 Online / Secure", "100%")

    st.markdown("### 📈 Live Tick Density Stream")
    st.line_chart(df_vault.set_index("timestamp")["price"])

    st.markdown("### 🗄️ Recent Partition Index Preview")
    st.dataframe(df_vault.tail(10), use_container_width=True)

# --- INGEST STREAM VIEW ---
elif action_mode == "📥 Ingest Tick Stream":
    st.subheader("Simulate Real-Time Tick Ingestion")
    st.markdown("Masukkan data transaksi tick baru ke dalam partisi kolom terkompresi.")
    
    with st.form("ingest_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_price = st.number_input("Tick Price", value=1.08550, format="%.5f")
        with col2:
            new_volume = st.number_input("Volume Size", value=1500.0, step=100.0)
        
        submitted = st.form_submit_button("Commit to Vault 🚀")
        if submitted:
            new_row = pd.DataFrame({
                "timestamp": [datetime.datetime.now()],
                "symbol": [selected_symbol],
                "price": [new_price],
                "volume": [new_volume]
            })
            st.session_state["vault_db"] = pd.concat([st.session_state["vault_db"], new_row], ignore_index=True)
            st.success(f"Successfully ingested tick for {selected_symbol} at price {new_price}!")
            time.sleep(0.5)
            st.rerun()

# --- HISTORICAL QUERY VIEW ---
elif action_mode == "🔍 Historical Backtest Query":
    st.subheader("Institutional Backtest Query Engine")
    st.markdown("Tarik data historis berdensitas tinggi untuk kebutuhan audit dan *backtesting* kuantitatif.")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.date(2026, 9, 1))
    with col2:
        end_date = st.date_input("End Date", datetime.date.today())

    if st.button("Execute High-Speed Query ⚡"):
        filtered_df = df_vault[(df_vault["timestamp"].dt.date >= start_date) & (df_vault["timestamp"].dt.date <= end_date)]
        st.success(f"Query completed successfully! Retrieved {len(filtered_df)} records.")
        st.dataframe(filtered_df, use_container_width=True)

        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Vault Dataset (CSV/Parquet)",
            data=csv_data,
            file_name=f"vault_export_{selected_symbol}.csv",
            mime="text/csv"
        )

# --- STORAGE DIAGNOSTICS VIEW ---
else:
    st.subheader("⚙️ Storage & Partition Diagnostics")
    st.markdown("Memantau kesehatan partisi *Columnar Parquet Storage* dan alokasi memori.")
    
    st.info("Storage Engine menggunakan Apache Arrow format dengan pengindeksan nano-detik timestamp.")
    st.write("**Active Partitions:**")
    st.code("zf_vault_storage/symbol=EURUSD/date=2026-09-01.parquet\nzf_vault_storage/symbol=BTCUSDT/date=2026-09-01.parquet")
    
    st.progress(42, text="Storage Utilization: 4.2 GB / 10.0 GB (42%)")

# --- FOOTER ---
st.markdown('<div class="brand-footer">Aa Baroq Applied Technologies | Archival Vault Manager (No. 73)</div>', unsafe_allow_html=True)
