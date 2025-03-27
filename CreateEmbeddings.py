from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveJsonSplitter
from langchain.schema import Document
from Config import embedder_model
import pandas as pd
import json







with open("../Data/TurtlesAllV2.json" , "r" , encoding="utf-8") as file:
    data = json.load(file)

def get_chunks(text):
  splitter = RecursiveJsonSplitter(
      max_chunk_size=1024,
      min_chunk_size=100
  )

  return splitter.split_text(text)


def excel_to_documents(path: str):
    df = pd.read_excel(path)
    documents = []
    for _, row in df.iterrows():
        doc = Document(
            page_content=row["Response"],
            metadata={
                "Topic": row["Topic"],
                "Question Examples": row["Different Question Variations"].split("/")
            }
        )
        documents.append(doc)  # Keep appending instead of returning early
    
    return documents  # Return after processing all rows

   




chunks = get_chunks(data)

excel_docs = excel_to_documents("../Data/Questions and answer for the chatbot (1).xlsx")

# print(excel_docs)

turtles_vector_store = FAISS.from_texts(chunks , embedder_model)

excel_vector_store = FAISS.from_documents(excel_docs , embedder_model)

turtles_vector_store.save_local("DataEmbeddings/Turtles_Embeddings/JSONData/")

excel_vector_store.save_local("DataEmbeddings/Turtles_Embeddings/Qustion&Answer/")

# print(excel_vector_store.similarity_search("Can sea turtle communicate with each other?" , k=3))