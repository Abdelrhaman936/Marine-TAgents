print('arias')
# from langchain_google_genai import ChatGoogleGenerativeAI , GoogleGenerativeAIEmbeddings
from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.retrievers import EnsembleRetriever
import os
from dotenv import load_dotenv

load_dotenv()


qwen = ChatOllama(model="qwen2.5" , temperature=0.05 , num_ctx=8192)
qwen_json_mode = ChatOllama(model="qwen2.5" , mode="json")
embedder_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
tavily_tool = TavilySearchResults(k=3)

REDIS_URL= "redis://localhost:6379/0"
# REDIS_URL= "redis://redis-stack:6379/0"

json_vectorstore = "DataEmbeddings/Turtles_Embeddings/JSONData/"
question_answer = "DataEmbeddings/Turtles_Embeddings/Qustion&Answer/"
online_data_path = "DataEmbeddings/Turtles_Embeddings/OnlineScraped2/"

json_vectorstore_retriever = FAISS.load_local(json_vectorstore , embedder_model , allow_dangerous_deserialization= True).as_retriever(kwargs={"k":5})

excel_vectorstore_retriever = FAISS.load_local(question_answer , embedder_model , allow_dangerous_deserialization= True).as_retriever(kwargs={"k":3})

if os.path.exists(online_data_path):
    online_vectorstore_retriever = FAISS.load_local(online_data_path , embedder_model , allow_dangerous_deserialization=True).as_retriever(kwargs={"k":5})       

    all_retrievers = EnsembleRetriever(
    retrievers=[
        json_vectorstore_retriever , excel_vectorstore_retriever , online_vectorstore_retriever
        ],
    weights= [0.5 , 0.3 , 0.2])

else:
    all_retrievers = EnsembleRetriever(
    retrievers=[
        json_vectorstore_retriever , excel_vectorstore_retriever
        ],
    weights= [0.5 , 0.5])