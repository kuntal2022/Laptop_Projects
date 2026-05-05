from langchain_core.messages import HumanMessage
from click import prompt
from IPython.core.page import page
from tiktoken import model
from langchain_core.prompts import *
import streamlit as st, pandas as pd, numpy as np 

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.messages import *
from dotenv import load_dotenv
load_dotenv()
from langchain_experimental.tools import PythonREPLTool


st.set_page_config(page_title="Math Agent", layout="wide", page_icon="🤖")
st.title("Test To Math Problem Solver")

open_ai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
st.sidebar.write("****************************************")
question = st.text_area("Enter your question:")




if open_ai_api_key and question:
    with st.spinner("Thinking...!"):

        try:
            llm =ChatOpenAI(temperature=0.5,model="gpt-5.1", max_tokens=100, api_key=open_ai_api_key    )



            agent = create_agent(
            model=llm, 
            tools=[PythonREPLTool()]) 

            response=agent.invoke({"messages" : [HumanMessage(content=question)]})
            result=response['messages'][-1].content
           
        except Exception as e:
            st.error(f"An error occurred: 'Invalid API Key'")
            st.sidebar.error(f"An error occurred: 'Invalid API Key'")
        else:
            st.write(result)

