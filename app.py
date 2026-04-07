import streamlit as st
import requests
import os

st.set_page_config(page_title="Pro-Data AI", page_icon="📈")
st.title("🚀 Profesyonel Veri Analiz Asistanı")

BACKEND_URL = "http://127.0.0.1:8000"

# Sidebar: Dosya Yükleme
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
    
    #  CSV YÜKLEME
    uploaded_csv = st.file_uploader("Analiz edilecek CSV'yi seçin", type="csv")
    if uploaded_csv:
        try:
            files = {"file": (uploaded_csv.name, uploaded_csv.getvalue(), "text/csv")}
            res = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=20)
            if res.status_code == 200:
                st.success("Veri tabanı bağlandı!")
            else:
                st.error(f"Sunucu hatası: {res.status_code}")
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")
    
    #  PDF YÜKLEME
    uploaded_pdf = st.file_uploader("Bilgi Bankası (PDF)", type="pdf")
    if uploaded_pdf:
        with st.spinner("Doküman analiz ediliyor..."):
            try:
                files = {"file": (uploaded_pdf.name, uploaded_pdf.getvalue(), "application/pdf")}
                res = requests.post(f"{BACKEND_URL}/upload_pdf", files=files, timeout=30)
                if res.status_code == 200:
                    st.success("Bilgi Bankası Güncellendi!")
                else:
                    st.error("PDF yüklenemedi.")
            except Exception as e:
                st.error(f"Hata: {e}")

# Chat Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("image"):
            st.image(msg["image"])

# Soru Girişi
if prompt := st.chat_input("Verilerin hakkında bir analiz iste..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("AI Analiz Ediyor..."):
        try:
            res = requests.post(f"{BACKEND_URL}/ask?question={prompt}", timeout=None)
            if res.status_code == 200:
                data = res.json()
                answer = data.get("answer", "Cevap üretilemedi.")
                plot_url = data.get("plot_url")

                # Görsel oluştuysa ama AI limit hatası verdiyse metni düzelt
                if "iteration limit" in str(answer).lower() and plot_url:
                    answer = "Analiz tamamlandı ve görsel oluşturuldu. İşte sonuç:"

                with st.chat_message("assistant"):
                    st.write(answer)
                    if plot_url:
                        st.image(plot_url)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "image": plot_url
                })
            else:
                st.error("Sunucudan hatalı yanıt geldi.")
        except Exception as e:
            st.error(f"Analiz hatası: {e}")