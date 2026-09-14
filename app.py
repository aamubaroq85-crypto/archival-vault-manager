import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import hashlib
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Archival Vault Manager | Aa Baroq Applied Technologies",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] * {
        color: #f0f6fc !important;
    }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #f0f6fc !important;
        border-color: #30363d !important;
    }
    div.stDateInput input, div[data-baseweb="input"] input, input[aria-label] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    div[data-baseweb="input"] *, span[data-baseweb="tag"] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    .stTextInput label, .stNumberInput label, .stDateInput label, .stSelectbox label {
        color: #f0f6fc !important;
        font-weight: 600 !important;
    }
    .stButton > button, div.stFormSubmitButton > button {
        background-color: #21262d !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #30363d !important;
        border-color: #8b949e !important;
    }
    div[data-baseweb="popover"] div, div[data-baseweb="menu"] div {
        background-color: #161b22 !important;
        color: #ffffff !important;
    }
    pre, code {
        background-color: #161b22 !important;
        color: #79c0ff !important;
        border: 1px solid #30363d !important;
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
    .pricing-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION FOR COMMERCIAL & DATABASE ---
if "user_db" not in st.session_state:
    # Akun demo bawaan untuk pengujian tier
    st.session_state["user_db"] = {
        "free_user": {"pass": "free123", "tier": "Free Tier", "key": "zf_free_demo_key"},
        "pro_user": {"pass": "pro123", "tier": "Pro Tier", "key": "zf_pro_99a8bc76d"},
        "institutional_user": {"pass": "inst123", "tier": "Institutional Tier", "key": "zf_inst_x9988776655"}
    }

if "auth_state" not in st.session_state:
    st.session_state["auth_state"] = {"logged_in": False, "username": "", "tier": "Free Tier", "api_key": ""}

if "vault_db" not in st.session_state:
    np.random.seed(42)
    timestamps = pd.date_range(start="2026-09-01 09:00:00", periods=600, freq="s")
    base_price = 1.0850
    prices = base_price + np.cumsum(np.random.randn(600) * 0.0002)
    volumes = np.random.randint(100, 5000, size=600)
    
    st.session_state["vault_db"] = pd.DataFrame({
        "timestamp": timestamps,
        "symbol": "EURUSD",
        "price": prices,
        "volume": volumes
    })

df_vault = st.session_state["vault_db"]

# --- AUTHENTICATION & LOGIN SIDEBAR MODUL ---
st.sidebar.header("🔐 Portal Akses Komersial")

if not st.session_state["auth_state"]["logged_in"]:
    auth_mode = st.sidebar.radio("Pilih Opsi", ["🔑 Login Akun", "📝 Registrasi Paket / Upgrade"])
    
    if auth_mode == "🔑 Login Akun":
        with st.sidebar.form("login_form"):
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Masuk Vault")
            
            if login_btn:
                user_record = st.session_state["user_db"].get(username_input)
                if user_record and user_record["pass"] == password_input:
                    st.session_state["auth_state"] = {
                        "logged_in": True,
                        "username": username_input,
                        "tier": user_record["tier"],
                        "api_key": user_record["key"]
                    }
                    st.success("Login Berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
        
        st.sidebar.markdown("---")
        st.sidebar.info("💡 **Akun Demo Cepat:**\n- Free: `free_user` / `free123`\n- Pro: `pro_user` / `pro123`\n- Inst: `institutional_user` / `inst123`")

    else:
        st.sidebar.subheader("Pilih Paket Komersial")
        st.sidebar.markdown("""
        - **Free Tier**: Dashboard dasar & simulasi terbatas.
        - **Pro Tier ($10/bln)**: Analitik Kuantitatif & Ekspor tanpa batas.
        - **Institutional Tier ($50/bln)**: Akses API DaaS & Multi-Thread Engine.
        """)
        with st.sidebar.form("register_form"):
            new_user = st.text_input("Buat Username Baru")
            new_pass = st.text_input("Buat Password Baru", type="password")
            selected_tier = st.selectbox("Pilih Tier", ["Free Tier", "Pro Tier", "Institutional Tier"])
            reg_btn = st.form_submit_button("Daftar & Simulasi Bayar 🚀")
            
            if reg_btn and new_user:
                if new_user in st.session_state["user_db"]:
                    st.sidebar.error("Username sudah terdaftar!")
                else:
                    generated_key = "zf_" + uuid.uuid4().hex[:12]
                    st.session_state["user_db"][new_user] = {
                        "pass": new_pass,
                        "tier": selected_tier,
                        "key": generated_key
                    }
                    st.sidebar.success("Registrasi sukses! Silakan login melalui menu Login Akun.")

    st.stop() # Hentikan eksekusi dashboard utama jika belum login

# Jika sudah login, tampilkan panel profil di sidebar
st.sidebar.success(f"👤 {st.session_state['auth_state']['username']}\n🏷️ Status: **{st.session_state['auth_state']['tier']}**")
if st.sidebar.button("🚪 Keluar (Logout)"):
    st.session_state["auth_state"] = {"logged_in": False, "username": "", "tier": "Free Tier", "api_key": ""}
    st.rerun()

st.sidebar.markdown("---")

# --- HEADER SECTION ---
st.title("🏛️ Archival Vault Manager")
st.markdown("**No. 73 | High-Density Tick-by-Tick Quant & Institutional Storage Engine**")
st.markdown("---")

# --- SIDEBAR NAVIGATION ---
user_tier = st.session_state["auth_state"]["tier"]
st.sidebar.header("⚙️ Vault Operations")
selected_symbol = st.sidebar.selectbox("Select Asset Symbol", ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSDT", "COMPOSITE.JK"])

nav_options = ["📊 Vault Dashboard", "📥 Ingest Tick Stream", "🌐 WebSocket Feeder Simulator", "🔍 Historical Backtest Query"]

if user_tier in ["Pro Tier", "Institutional Tier"]:
    nav_options.insert(3, "📈 Advanced Quant Analytics")

if user_tier == "Institutional Tier":
    nav_options.append("🔌 DaaS API Endpoint & Multi-Thread Engine")
else:
    nav_options.append("⭐ Upgrade ke Institutional / DaaS")

action_mode = st.sidebar.radio("Navigation", nav_options)

# --- 1. VAULT DASHBOARD ---
if action_mode == "📊 Vault Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Stored Records", f"{len(df_vault):,}")
    with col2:
        st.metric("Compression Ratio", "86.5% (Parquet ZSTD)")
    with col3:
        st.metric("Average Read Latency", "1.1 ms")
    with col4:
        st.metric("Vault Status", "🟢 Live & Secure", "100%")

    st.markdown("### 📈 Live Tick Density Stream")
    st.line_chart(df_vault.set_index("timestamp")["price"])

    st.markdown("### 🗄️ Recent Partition Index Preview")
    st.dataframe(df_vault.tail(10), use_container_width=True)

# --- 2. INGEST TICK STREAM ---
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

# --- 3. WEBSOCKET FEEDER SIMULATOR ---
elif action_mode == "🌐 WebSocket Feeder Simulator":
    st.subheader("Real-Time WebSocket Feed Simulation")
    st.markdown("Mensimulasikan koneksi *streaming feed* eksternal secara otomatis untuk memasukkan data tick langsung ke dalam sistem vault.")
    
    col1, col2 = st.columns(2)
    with col1:
        stream_count = st.slider("Jumlah Tick yang Disimulasikan", min_value=5, max_value=50, value=10)
    with col2:
        stream_speed = st.selectbox("Kecepatan Feed", ["High-Speed (0.1s)", "Standard (0.5s)", "Low-Speed (1.0s)"])
    
    delay_val = 0.1 if "0.1" in stream_speed else (0.5 if "0.5" in stream_speed else 1.0)
    
    if st.button("Mulai Live Feed Stream ⚡"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        current_prices = df_vault["price"].values
        last_val = current_prices[-1] if len(current_prices) > 0 else 1.0850
        
        streamed_data = []
        for i in range(stream_count):
            status_text.text(f"Menerima tick ke-{i+1} dari WebSocket endpoint...")
            last_val += np.random.randn() * 0.0003
            vol_val = np.random.randint(200, 3000)
            
            new_entry = {
                "timestamp": datetime.datetime.now(),
                "symbol": selected_symbol,
                "price": last_val,
                "volume": vol_val
            }
            streamed_data.append(new_entry)
            progress_bar.progress((i + 1) / stream_count)
            time.sleep(delay_val)
            
        df_streamed = pd.DataFrame(streamed_data)
        st.session_state["vault_db"] = pd.concat([st.session_state["vault_db"], df_streamed], ignore_index=True)
        st.success(f"Berhasil mengamankan dan menyinkronkan {stream_count} tick baru ke Vault!")
        st.rerun()

# --- 4. ADVANCED QUANT ANALYTICS (PRO & INSTITUTIONAL) ---
elif action_mode == "📈 Advanced Quant Analytics":
    st.subheader("Advanced Quantitative & Technical Analytics")
    st.markdown("Analisis indikator teknis mendalam (SMA, RSI, Volatilitas, dan MACD) berbasis data historis *tick* vault.")
    
    df_quant = df_vault.copy()
    window_sma = st.slider("Periode Moving Average (SMA)", min_value=5, max_value=50, value=20)
    
    df_quant["SMA"] = df_quant["price"].rolling(window=window_sma).mean()
    df_quant["Daily_Return"] = df_quant["price"].pct_change()
    df_quant["Volatility"] = df_quant["Daily_Return"].rolling(window=window_sma).std() * np.sqrt(252)
    
    delta = df_quant["price"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_quant["RSI"] = 100 - (100 / (1 + rs))
    
    st.markdown("### 📊 Grafik Overlay Harga & Moving Average")
    st.line_chart(df_quant.set_index("timestamp")[["price", "SMA"]])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📉 Indikator Volatilitas")
        st.line_chart(df_quant.set_index("timestamp")["Volatility"])
    with col2:
        st.markdown("### ⚡ Relative Strength Index (RSI)")
        st.line_chart(df_quant.set_index("timestamp")["RSI"])

# --- 5. HISTORICAL BACKTEST QUERY ---
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

# --- 6. DAAS API ENDPOINT & MULTI-THREAD ENGINE (INSTITUTIONAL ONLY) ---
elif action_mode == "🔌 DaaS API Endpoint & Multi-Thread Engine":
    st.subheader("🔌 Data-as-a-Service (DaaS) API & Multi-Thread Storage")
    st.markdown("Akses eksklusif endpoint data mentah dan manajemen partisi kolumnar berskala institusional.")
    
    st.info(f"🔑 **Your Active API Key:** `{st.session_state['auth_state']['api_key']}`")
    st.markdown("Gunakan *API Key* di atas untuk menarik data langsung via skrip Python eksternal:")
    
    st.code(f"""
import requests

url = "https://api.aaroq-tech.com/v1/vault/query"
headers = {{"Authorization": "Bearer {st.session_state['auth_state']['api_key']}"}}
params = {{"symbol": "{selected_symbol}", "format": "parquet"}}

response = requests.get(url, headers=headers, params=params)
print(response.json())
    """, language="python")
    
    st.markdown("### ⚙️ Multi-Thread Cluster Diagnostics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Worker Threads", "16 Threads (Dedicated)")
        st.metric("ZSTD Compression Rate", "88.2%")
    with col2:
        st.metric("SLA Uptime", "99.99%")
        st.metric("Data Throughput", "1.2 GB/s")

    st.progress(85, text="Cluster Storage Utilization: 8.5 GB / 50.0 GB (17%)")

# --- 7. UPGRADE PAYWALL PROMPT ---
else:
    st.subheader("⭐ Tingkatkan Paket Langganan Anda")
    st.markdown("Nikmati fitur penuh tanpa batas untuk mengoptimalkan strategi trading dan analitik kuantitatif Anda.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚀 Pro Tier ($10/bulan)")
        st.markdown("- Akses Full Advanced Quant Analytics (RSI, Volatility, MACD)\n- Ekspor dataset tanpa batas kuota\n- Prioritas *High-Speed Query*")
        if st.button("Upgrade ke Pro Tier Sekarang"):
            st.success("Simulasi pembayaran berhasil! Silakan hubungi admin untuk aktivasi instan atau ubah tier akun.")
    with col2:
        st.markdown("### 🏛️ Institutional / DaaS ($50/bulan)")
        st.markdown("- Akses Dedicated API Key untuk Bot Trading\n- Multi-Thread Storage Engine (16 Threads)\n- Dukungan SLA 99.99%")
        if st.button("Upgrade ke Institutional Tier"):
            st.success("Simulasi pembayaran korporat berhasil diproses!")

# --- FOOTER ---
st.markdown('<div class="brand-footer">Aa Baroq Applied Technologies | Archival Vault Manager (No. 73)</div>', unsafe_allow_html=True)
