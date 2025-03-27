import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Add the current directory to sys.path

from Turtles_Agent import agent_with_message_history
import streamlit as st
from Grader_Agent import grade_answer
from utils import get_message_history , BinaryGrade , GraderOutput
from langchain_core.messages import AIMessage
from Online_Search import search_agent_executor , search_agent_with_message_history
import time
import redis

# client = redis.StrictRedis("localhost" , port=6379 , db=0)

def app(session_id : str , input_message : str):
    initial_answer = agent_with_message_history.invoke(

            {
                "input": input_message
            } ,
            config={"configurable" : {"session_id":session_id}}

    )
    print(initial_answer)
    initial_answer = initial_answer["output"]

    grader_response : BinaryGrade = grade_answer(input_message , initial_answer)


    if grader_response.binary_score.lower() == "yes":

        return initial_answer
    
    else:
        search_response = search_agent_with_message_history.invoke(
            {
                "input": input_message
            } ,
            config={"configurable" : {"session_id":session_id}}
        )["output"]
        # search_response = search_agent_executor.invoke(
        #     {
        #         "input": input_message
        #     }
        # )["output"]

        # chat_history = get_message_history(session_id)

        # if chat_history.messages:
        #     all_messages = chat_history.messages

        #     all_messages[-1] = AIMessage(content=search_response)

        #     chat_history.clear()

        #     for message in all_messages:
        #         # client.rpush(f"message_store:{session_id}" , message) #using redis client to save messages manually in case of search
        #         chat_history.add_message(message)
        return search_response
    

# print(app(session_id="test memory" , input_message="show me photos for it?"))
st.title("🐢 Sea Turtles Ai AGENT")


session_id = st.sidebar.text_input("Enter Session Name" , "")

def response_generator(answer : str):
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
        response = app(session_id , prompt)

        st.write_stream(response_generator(response))
        


    st.session_state.chat_history.append({"role":"assistant" , "content" : response})





