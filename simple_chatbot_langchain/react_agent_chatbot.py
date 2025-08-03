from langchain.agents import create_react_agent
from langchain.chat_models import ChatOpenAI

# Initialize the chat model
chat_model = ChatOpenAI(temperature=0)

# Create the ReAct agent
agent = create_react_agent(chat_model)

# Simple loop to chat with the agent
print("Simple React Agent Chatbot using Langchain. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        print("Goodbye!")
        break
    response = agent.run(user_input)
    print(f"Bot: {response}")
