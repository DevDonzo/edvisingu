from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

# Load system prompt
prompt_path = os.path.join(os.path.dirname(__file__), "../../prompts/hermes_system.txt")
with open(prompt_path) as f:
    SYSTEM_PROMPT = f.read()

# Embeddings via local Ollama
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Persistent ChromaDB memory
db_path = os.path.join(os.path.dirname(__file__), "../../vector-db/chroma-data")
vectorstore = Chroma(
    persist_directory=db_path,
    embedding_function=embeddings,
    collection_name="hermes_memory",
)

# Claude as the reasoning LLM
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=4096,
)

# Conversation memory (last 10 exchanges)
memory = ConversationBufferWindowMemory(
    k=10,
    memory_key="chat_history",
    return_messages=True,
    output_key="answer",
)

# Build retrieval chain
chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    memory=memory,
    return_source_documents=False,
    verbose=False,
)


def chat(message: str) -> str:
    full_message = f"{SYSTEM_PROMPT}\n\nUser: {message}"
    result = chain({"question": full_message})
    return result["answer"]


if __name__ == "__main__":
    print("Hermes Agent ready. Type 'quit' to exit.")
    while True:
        user_input = input("Dr. D: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        print(f"Hermes: {chat(user_input)}")
