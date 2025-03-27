from flask import Flask , request , jsonify
from Turtles_Agent import agent_with_message_history
from Grader_Agent import grade_answer
from utils import get_message_history , BinaryGrade , GraderOutput
from langchain_core.messages import AIMessage
from Online_Search import search_agent_executor

app_flask = Flask(__name__)







def app(session_id : str , input_message : str):
    initial_answer = agent_with_message_history.invoke(

            {
                "input": input_message
            } ,
            config={"configurable" : {"session_id":session_id}}

    )["output"]

    grader_response : BinaryGrade = grade_answer(input_message , initial_answer)


    if grader_response.binary_score.lower() == "yes":

        return initial_answer
    
    else:
        search_response = search_agent_executor.invoke(
            {
                "input": input_message
            }
        )["output"]

        chat_history = get_message_history(session_id)

        if chat_history.messages:
            all_messages = chat_history.messages

            all_messages[-1] = AIMessage(content=search_response)

            chat_history.clear()

            for message in all_messages:
                # client.rpush(f"message_store:{session_id}" , message) #using redis client to save messages manually in case of search
                chat_history.add_message(message)
        return search_response





@app_flask.route("/chat" , methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id" , "")
    query = data.get("query" , "")

    answer = app(session_id , query)

    return jsonify({"response" : answer})

if __name__ == "__main__":
    app_flask.run(port=5000)