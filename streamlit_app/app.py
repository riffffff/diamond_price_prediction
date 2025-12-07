import streamlit as st
import requests
import os

# -------------------------
# Style custom
# -------------------------
st.set_page_config(
    page_title="💎 Prediksi Harga Diamond",
    page_icon="💎",
    layout="centered"
)

st.markdown("""
<style>
h1 {
    color: #4B0082;
}
div.stButton > button:first-child {
    background-color: #4B0082;
    color:white;
    height:3em;
    width:100%;
    border-radius:10px;
    font-size:16px;
}
.stAlert {
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Judul
# -------------------------
st.title("💎 Prediksi Harga Diamond")
st.write("Isi detail diamond untuk mendapatkan prediksi harga secara cepat dan akurat.")

# -------------------------
# Form input user (2 kolom)
# -------------------------
with st.form("diamond_form"):
    col1, col2 = st.columns(2)

    with col1:
        carat = st.number_input("Berat (Carat)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        cut = st.selectbox("Potongan (Cut)", ["Ideal", "Premium", "Very Good", "Good"])
        color = st.selectbox("Warna (Color)", ["D", "E", "F", "G", "H", "I", "J"])
        clarity = st.selectbox("Kejernihan (Clarity)", ["IF","VVS1","VVS2","VS1","VS2","SI1","SI2"])
    
    with col2:
        table = st.number_input("Persentase Table (%)", min_value=50, max_value=70, value=55)
        panjang = st.number_input("Panjang (mm)", min_value=3.0, max_value=10.0, value=6.5)
        lebar = st.number_input("Lebar (mm)", min_value=3.0, max_value=10.0, value=6.5)
        tinggi = st.number_input("Tinggi (mm)", min_value=2.0, max_value=7.0, value=4.0)
    
    submitted = st.form_submit_button("✨ Prediksi Harga")

# -------------------------
# Kirim ke API dan tampilkan hasil
# -------------------------
if submitted:
    payload = {
        "carat": carat,
        "cut": cut,
        "color": color,
        "clarity": clarity,
        "table": table,
        "x": panjang,
        "y": lebar,
        "z": tinggi
    }

    # Get API URL from environment variable or use default
    api_url = os.getenv("API_URL", "http://127.0.0.1:5000/predict")

    try:
        response = requests.post(api_url, json=payload)
        response_data = response.json()
        price = response_data['predicted_price']

        # Warna harga berdasarkan range
        if price < 2:
            color_price = "🔴 Murah"
        elif price < 5:
            color_price = "🟠 Sedang"
        else:
            color_price = "🟢 Mahal"

        # Tampilkan hasil cantik
        st.markdown("### 💰 Hasil Prediksi Harga")
        st.markdown(f"""
        Diamond dengan **{carat} Carat**, potongan **{cut}**, warna **{color}**, dan kejernihan **{clarity}** 
        diperkirakan memiliki harga sekitar:
        """)
        st.success(f"**{price:.2f}** ({color_price})")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat menghubungi API: {e}")