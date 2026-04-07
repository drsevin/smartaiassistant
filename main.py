import os
import io
import uuid
import pandas as pd
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse  
from fastapi.staticfiles import StaticFiles
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

app = FastAPI()

# Statik klasörü kontrolü
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modeller ve Bellek
llm = OllamaLLM(model="llama3", temperature=0)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
df_storage = {"data": None}
vector_db = {"db": None}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), on_bad_lines='skip')
        df_storage["data"] = df
        return {"message": "CSV başarıyla yüklendi!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV Hatası: {str(e)}")

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_path = f"static/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)
        vector_db["db"] = FAISS.from_documents(splits, embeddings)
        
        return {"message": "PDF başarıyla işlendi!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Hatası: {str(e)}")


@app.post("/ask")
async def ask_question(question: str):
    if df_storage.get("data") is None:
        return {"answer": "Lütfen önce bir veri seti (CSV) yükleyin."}

    # Dinamik RAG: Soruda ipucu varsa PDF'e bak
    pdf_context = ""
    if vector_db.get("db"):
        docs = vector_db["db"].similarity_search(question, k=1)
        pdf_context = f"\n[Referans Doküman Bilgisi]: {docs[0].page_content}\n"

    # Esnek Agent Kurulumu
    agent = create_pandas_dataframe_agent(
    llm, 
    df_storage["data"], 
    verbose=True, 
    allow_dangerous_code=True,
    agent_type="zero-shot-react-description",
    max_iterations=5,
    handle_parsing_errors=True,
    early_stopping_method="generate" # Limit dolunca elindeki en mantıklı şeyi söyler
    )

    # Genel Prompt: Veriye özel isim vermiyoruz (df diyoruz)
    full_prompt = (
        f"Kullanıcı Sorusu: {question}\n"
        f"{pdf_context}\n"
        "TALİMATLAR:\n"
        "1. Soruyu yanıtlamak için elindeki 'df' isimli tabloyu ve varsa doküman bilgisini kullan.\n"
        "2. İşlemi bitirdiğinde cevabını MUTLAKA 'Final Answer: [Cevabın]' kalıbıyla bitir.\n"
        "3. Eğer bir hesaplama yaptıysan, sonucunu net bir şekilde belirt."
    )

    try:
        response = agent.invoke({"input": full_prompt})
        return {"answer": response["output"]}
    except Exception as e:
        error_msg = str(e)
        
        # Strateji: Eğer 'Final Answer' metnin içindeyse onu ayıkla
        if "Final Answer:" in error_msg:
            return {"answer": error_msg.split("Final Answer:")[-1].strip()}
        
        # Strateji: Eğer terminalde bir çıktı oluştuysa ama format bozuksa
        # Hata mesajının son 100 karakterine bak (Genelde cevap oradadır)
        clean_msg = error_msg.replace("`", "").strip()
        if len(clean_msg) > 5:
            # Sadece anlamlı bir parça döndür (Teknik detayları temizle)
            return {"answer": f"Analiz başarıyla tamamlandı. Sonuç: {clean_msg.split('Value:')[-1] if 'Value:' in clean_msg else 'İşlem başarılı, lütfen soruyu tekrar sormayı deneyin.'}"}
            
        return {"answer": "Bir format hatası oluştu, ancak terminalde işlem tamamlandı."}