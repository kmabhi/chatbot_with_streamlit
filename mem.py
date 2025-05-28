from langchain.memory import ConversationBufferMemory

#loading memory object
memory = ConversationBufferMemory(
memory_key = 'chat_history',
return_messages=True
)