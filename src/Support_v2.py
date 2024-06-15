import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import OpenAIEmbeddings
from methods import (orchestrate_response_and_upload, orchestration_pdf_vectore_store,
                     get_context_retriever_chain, get_conversational_rag_chain,
                     init_mongodb_connection, get_systems_health)

# Save and load vector store using Chroma's built-in methods


def save_vector_store(vector_store, path):
    vector_store.save(path)
    print("Vector store saved at:", path)


def load_vector_store(path):
    if os.path.exists(path):
        vector_store = Chroma.load(path)
        print("Vector store loaded from:", path)
        return vector_store
    else:
        print("No vector store found at:", path)
        return None


# app config
st.set_page_config(page_title="Medicall Support", page_icon="ℹ️")
st.title("Medicall Support")

# initialize mongodb and embeddings model for validation
if "collection" not in st.session_state:
    st.session_state.collection = init_mongodb_connection()

if "embeddings" not in st.session_state:
    st.session_state.embeddings = OpenAIEmbeddings()

# Check system status in the sidebar
with st.sidebar:
    if st.button("Systemstatus prüfen"):  # Check system status
        health_status = get_systems_health(st.session_state.collection)
        st.write(health_status)
    else:
        st.write("Click on the button to check the system status.")

    st.write("System status is not updated automatically. Click on the button to check the current system status.")

# Initialize PDF and get vector store
pdf_path = "/Users/sonah/Library/CloudStorage/OneDrive-ZHAW/ML2/Final_project_ML2/src/Leistungen_en.pdf"
vector_store_path = "vector_store"

if "vector_store" not in st.session_state:
    vector_store = load_vector_store(vector_store_path)
    if vector_store is None:
        vector_store = orchestration_pdf_vectore_store(pdf_path)
        save_vector_store(vector_store, vector_store_path)
    st.session_state.vector_store = vector_store

# Get the context needed to answer the question
retriever_chain = get_context_retriever_chain(st.session_state.vector_store)

# Connect the chains together
conversational_rag_chain = get_conversational_rag_chain(retriever_chain)

# Chat history using langchain schema and making it persistent during our session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hey! How can I help you?"),
    ]

# User input
user_query = st.chat_input("Write your questions here")
if user_query is not None and user_query != "":
    with st.spinner("We prepare the best answer ⏳"):
        response = orchestrate_response_and_upload(
            st.session_state.chat_history, conversational_rag_chain, user_query, st.session_state.collection, st.session_state.embeddings)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

# Conversation display
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)
