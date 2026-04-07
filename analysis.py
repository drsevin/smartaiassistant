import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_pandas_dataframe_agent

# Örnek bir veri seti (Sanal bir satış verisi)
data = {
    'Urun': ['iPhone 15', 'MacBook M2', 'AirPods', 'iPad Pro'],
    'Fiyat': [45000, 65000, 7000, 35000],
    'Stok': [120, 45, 300, 15],
    'Kategori': ['Telefon', 'Bilgisayar', 'Aksesuar', 'Tablet']
}
df = pd.DataFrame(data)

print("--- Veri Seti Yüklendi ---")
print(df)

# Ollama üzerinden Llama 3 modelini bağla
llm = OllamaLLM(
    model="llama3", 
    temperature=0, # 0 yaparak AI'nın uydurmasını (halüsinasyon) engelliyoruz, daha net olur.
    system="Sen bir veri analistisin. Sadece Python kodları yazarak soruları cevapla. Gereksiz açıklama yapma."
)

agent = create_pandas_dataframe_agent(
    llm, 
    df_storage["data"], 
    verbose=True, 
    allow_dangerous_code=True,
    handle_parsing_errors=True,
    max_iterations=5,        # 5 denemede bulamazsa dur (Sonsuz döngüyü engeller)
    early_stopping_method="generate", # Limit dolarsa elindeki en iyi tahmini söyle
    return_intermediate_steps=False
)

#Sorgu yapıyoruz
soru = "En pahalı ürün hangisi ve stokta kaç adet var?"
print(f"\nSoru: {soru}")

try:
    cevap = agent.invoke(soru)
    print(f"\nAI Sonucu: {cevap['output']}")
except Exception as e:
    print(f"Bir hata oluştu: {e}")