from Config import qwen , REDIS_URL , qwen_json_mode
from langchain_core.prompts import ChatPromptTemplate , SystemMessagePromptTemplate , HumanMessagePromptTemplate
import json
import re
from utils import GraderOutput , BinaryGrade
from langchain.chains.llm import LLMChain

# def grade_answer(question : str , answer : str):
#     grader_prompt = ChatPromptTemplate.from_messages([
#         ("system", 
#         "You are an expert answer evaluator. Your task is to analyze whether the provided answer correctly and completely responds to the given question.\n"
#         "\n"
#         "**Instructions:**\n"
#         "1. **Understand the Question:** Identify the key information being requested.\n"
#         "2. **Analyze the Answer:** Check if it:\n"
#         "   - Is relevant to the question.\n"
#         "   - Provides a complete and accurate response.\n"
#         "   - Avoids unnecessary or misleading information.\n"
#         "   - If the answer contains URLs (e.g., links to images), verify whether they are appropriate and relevant to the question.\n"
#         "3. **Provide a Verdict:** Return one of the following labels:\n"
#         "   - **'Fully Relevant'** – The answer (text or links) is correct, complete, and directly addresses the question.\n"
#         "   - **'Partially Relevant'** – The answer contains some useful information but is incomplete or somewhat off-topic.\n"
#         "   - **'Irrelevant'** – The answer does not meaningfully address the question.\n"
#         "4. **Justify Your Decision:** Explain why you chose the label and, if applicable, specify what is missing.\n"
#         "\n"
#         "**Output Format:**\n"
#         "- **Verdict:** [Fully Relevant / Partially Relevant / Irrelevant]\n"
#         "- **Justification:** [Brief explanation]"
#         "- **needs_search:** [boolean value represents If the answer is not relevant and needs search]"
#         ),
#         ("human", "Question: {question}\nAnswer: {retrieved_answer}")
#     ])
    
#     llm = qwen.with_structured_output(GraderOutput)
    
#     # grader_chain = LLMChain(llm=llm, prompt=grader_prompt)
#     grader_chain = grader_prompt | llm
    
#     response = grader_chain.invoke({"question":question , "retrieved_answer" : answer})

#     return response


def grade_answer(question : str , answer : str):
    # grading_instructions = SystemMessagePromptTemplate.from_template(""" Yor are a turtles researcher grader assessing answer of a question,

    # If the answer contains keyword(s) or semantic meaning related to the question, grade it as relevant.
    
    # Return JSON with single key, 'binary_score' that is 'yes' or 'no' score to indicate wehter the document cotains atleast some information that is relevant to the question.
    # """)
    grading_instructions = SystemMessagePromptTemplate.from_template(""" Yor are an answer evaluation agent, Your task is to determine wether the given answer is relevant to the provided question.

    If the answer contains keyword(s) or semantic meaning related to the question, grade it as relevant.
                                                                     
    If the answer contains 'I don't know' then the grade is no
    
    Return JSON with single key, 'binary_score' that is 'yes' or 'no' score to indicate wehter the document cotains atleast some information that is relevant to the question.
    """)

    grading_prompt = HumanMessagePromptTemplate.from_template("""
    Please grade the following:

    QUESTION: {question}
    ANSWER: {answer}
    """)

    chat_prompt = ChatPromptTemplate.from_messages([
        grading_instructions,
        grading_prompt],
        # input_variables=["question", "answer"]
          )
    
    structured_qwen = qwen.with_structured_output(BinaryGrade)

    
    grader_chain = chat_prompt | structured_qwen 

    
    grade = grader_chain.invoke({"question" : question , "answer" : answer})
    
    return grade



# print(grade_answer(question="Is there any laying spots in Arizona for mating?" , answer="""The Turtles_Researcher did not find any specific information on laying spots for loggerhead turtles in Arizona. Loggerhead turtles are typically found along the coasts of warmer regions such as Florida and parts of Mexico, rather than Arizona, which is inland. For accurate information, you might want to check with local conservation organizations or wildlife agencies. Would you like me to search online for more detailed information?"""))