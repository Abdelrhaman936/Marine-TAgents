import streamlit as st 
import requests
import time

NGROK_URL =  "https://1031-154-176-150-78.ngrok-free.app/chat"


st.title("🐢 Sea Turtles Ai AGENT")


session_id = st.sidebar.text_input("Enter Session Name" , "")

def response_generator(answer):
    for word in answer.split():
       yield word + " "
       time.sleep(0.05)



if "chat_history" not in st.session_state:
   st.session_state.chat_history = []

for message in st.session_state.chat_history:
   with st.chat_message(message["role"]):
       st.markdown(message["content"])

if prompt := st.chat_input("Ask me about sea turtles 🐢"):
   st.session_state.chat_history.append({"role" : "user" , "content":prompt})

   

   with st.chat_message("user"):
        st.markdown(prompt) 

   with st.chat_message("assistant"):
    response = requests.post(NGROK_URL , json={"session_id" : session_id , "query" : prompt})
    response = response.json().get("response" , "")
    st.write_stream(response_generator(response))
    # st.markdown(response)


   st.session_state.chat_history.append({"role":"assistant" , "content" : response})
