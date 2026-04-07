🤖 AI-Powered Data Analysis Assistant (Local & Hybrid RAG)

This project is an end-to-end AI Data Agent platform that enables non-technical users to perform complex data analysis, gain insights, and generate strategic reports using natural language interactions.

🚀 Key Features

Hybrid Analysis: Simultaneously processes structured data (CSV) and unstructured business rules (PDF).

Local & Private: Built for data privacy using Llama 3 locally via Ollama; your sensitive data never leaves your machine.

Autonomous Reasoning: Uses the LangChain ReAct (Reasoning and Acting) framework. The agent plans, writes Python code, executes it, and interprets the results.

RAG Integration: Stores company policies and discount rules in a FAISS vector database to contextualize data insights.

Robust Error Handling: Features a custom regex-based backend to handle LLM formatting inconsistencies and prevent infinite loops.

🛠️ Tech Stack

Language: Python 3.10+

LLM & Agent: Llama 3 (Local via Ollama), LangChain

Backend: FastAPI (Asynchronous API)

Frontend: Streamlit (Interactive Chat UI)

Data Science: Pandas, NumPy, Matplotlib

Vector Database: FAISS (Facebook AI Similarity Search)

Embeddings: HuggingFace (Sentence-Transformers)

📋 Architectural Flow

User Input: The user asks a question in plain English/Turkish.

RAG Retrieval: The system fetches relevant business rules from the PDF via similarity search.

Agent Planning: Llama 3 formulates a step-by-step plan to solve the query using the available data tools.

Action & Observation: The agent executes Python code in a secure REPL environment and observes the output.

Synthesis: The final result is synthesized from the numerical data and document-based rules into a human-readable strategic recommendation.

⚙️ Installation

Clone the Repository:

Bash

git clone https://github.com/drsevin/smartaiassistant.git

cd smartaiassistant

Setup Ollama & Llama 3:

Download Ollama from ollama.ai and pull the model:

Bash

ollama run llama3

Install Dependencies:

Bash

pip install -r requirements.txt

Run the Application:

Start Backend: uvicorn main:app --reload

Start Frontend: streamlit run app.py
