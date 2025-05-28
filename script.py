#importing needed packages

import os
import streamlit as st
from dotenv import load_dotenv,find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
# from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate,MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from mem import memory

#defining prompt template
prompt = ChatPromptTemplate(
input_variables = ['content'],
messages=[
    SystemMessage(content='You are a chat bot having a conversation with the human'),
    MessagesPlaceholder(variable_name='chat_history'),
    HumanMessagePromptTemplate.from_template('{content}')
])

#loading environment variables
load_dotenv(find_dotenv(),override=True)

#define title
st.title("Chatbot")

#side bar widgets, can be commented
st.sidebar.selectbox("Region",['KA','TN','AP','TS','KL','MH','DL'])
temperature = st.sidebar.slider('Temperature',min_value=0.0,max_value=1.0,step=0.1,value=0.3)

#create LLM model object
# llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash',temperature=temperature)
llm = ChatOpenAI(model='gpt-4.1-mini',temperature=1)


#create chain, with combined prompts and llm
chain = LLMChain(
llm = llm,
prompt = prompt,
memory = memory,
verbose=False)

#welcome message
with st.chat_message('Assistant'):
    st.write('Hi, how can i help you today?')


#create a msg variable for a session
if 'msgs' not in st.session_state:
    st.session_state.msgs = []

#display all the msgs in the session
for msg in st.session_state.msgs:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

#asking user input
query = st.chat_input('Ask your query')

if query:
    with st.chat_message('Human'):
        st.markdown(f"{query}")
    st.session_state.msgs.append({'role': 'Human', 'content':query})

    #getting completion from LLM
    ans = chain.invoke(query)
    response = ans['text']

    #displaying the response
    with st.chat_message('Assistant'):
        st.markdown(f"AI says : {response}")
    st.session_state.msgs.append({'role': 'Assistant', 'content': response})
