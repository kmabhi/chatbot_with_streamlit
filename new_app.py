import os
import streamlit as st
from dotenv import load_dotenv,find_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
# from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate,MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from mem import memory
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
import getpass

#loading environment variables
load_dotenv(find_dotenv(),override=True)

#defining agents
converter_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[],
    prompt=(
        """
        You are an expert .NET programmer with immense knowledge, you are tasked to convert the .NET code to detailed natural language description.
                        Focus on the purpose, functionality, and logic of the code.
                        Include information about:
                        1. The overall purpose of this file
                        2. Classes, methods, and their relationships
                        3. Business logic and workflows
                        4. Any UI elements and their interactions
                        5. Data structures and models
                        6. External dependencies and services used
                        7. After you're done with your tasks, respond to the supervisor directly
                        8. Respond ONLY with the results of your work, do NOT include ANY other text.

                        Provide a comprehensive natural language description that could be used to recreate this code in another language.
       """
    ),
    name="converter_agent",
)

generator_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[],
    prompt=(
        """
                You are an expert .NET-to-Java Developer Agent. Your task is to convert the following natural language description of .NET code to idiomatic Java 17. Ensure thread-safety and use appropriate Java equivalents for LINQ, delegates, and async methods.
                Requirements:
                1. Use lates Java version syntax and features
                2. Maintain the same functionality and business logic
                3. Use appropriate Java libraries and frameworks that match the .NET functionality
                4. Include all necessary imports
                5. Provide complete, compilable Java code
                6. Maintain the same class and method structure where appropriate
                7. Add Java documentation comments
                8. Generate unit test cases as well

                Provide the complete Java code implementation.
                """
    ),
    name="generator_agent",
)

reviewer_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[],
    prompt=(
        """
        You are an experienced Java programmer, you are tasked with reviewing the java code for conventions and best practices.flag any discrepencies and how they can be improved.
        also Ensures design patterns and architecture align.
                """
    ),
    name="reviewer_agent",
)

refactor_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[],
    prompt=(
        """
        You are an experienced Java programmer, you are tasked with Optimizes and simplifies the generated Java code.
                """
    ),
    name="refactor_agent",
)


supervisor = create_supervisor(
    model=init_chat_model("gpt-4.1-mini"),
    agents=[converter_agent, generator_agent,reviewer_agent,refactor_agent],
    prompt=(
        "You are a supervisor managing four agents:\n"
        "- a converter agent. Assign .Net code to natural language conversion tasks to this agent\n"
        "- a generator agent. Assign generation of Java code from natural language description tasks to this agent\n"
        "- a reviwer agent. Assign code review tasks to this agent\n"
        "- a refactor agent. Assign code refactor or optimisation tasks to this agent\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile()




#defining prompt template
prompt = ChatPromptTemplate(
input_variables = ['content'],
messages=[
    SystemMessage(content='You are a chat bot having a conversation with the human'),
    MessagesPlaceholder(variable_name='chat_history'),
    HumanMessagePromptTemplate.from_template('{content}')
])



#define title
st.title(".Net to Java converter")

#side bar widgets, can be commented
# st.sidebar.selectbox("Region",['KA','TN','AP','TS','KL','MH','DL'])
# temperature = st.sidebar.slider('Temperature',min_value=0.0,max_value=1.0,step=0.1,value=0.3)

#create LLM model object
# llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash',temperature=temperature)
# llm = ChatOpenAI(model='gpt-4.1-mini',temperature=1)


#create chain, with combined prompts and llm
# chain = LLMChain(
# llm = llm,
# prompt = prompt,
# memory = memory,
# verbose=False)

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
    config = {"configurable": {"thread_id": "test"}}
    ans = supervisor.invoke({"messages": query}, config=config)
    response = ans['text']

    #displaying the response
    with st.chat_message('Assistant'):
        st.markdown(f"AI says : {response}")
    st.session_state.msgs.append({'role': 'Assistant', 'content': response})