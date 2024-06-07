#on this page we will write the methods we will need for our prototype

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import pytz 
import os
import concurrent.futures
import numpy as np


from dotenv import load_dotenv

load_dotenv()

#Was wondering why my Document inside of my vectore store method was yellow. Chat-GPT saved the day.
class Document: 
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata if metadata is not None else {}

#get pdf text
def process_pdf(pdf_path):
    text=""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text() if page.extract_text is not None else ""
    return text

#get chunks from pdf
def get_chunks_from_pdf(text):
    text_splitter = RecursiveCharacterTextSplitter()
    chunks = text_splitter.split_text(text)
    return chunks

#create vector store from chunks
def get_vector_store(chunks):
    persist_directory = r"C:\Users\Admin\Desktop\ML2\Final_Project\src\db"
    embeddings = OpenAIEmbeddings()
    documents = [Document(chunk) for chunk in chunks]
    vectore_store = Chroma.from_documents(documents, embeddings, persist_directory = persist_directory)
    return vectore_store

def orchestration_pdf_vectore_store(pdf_path):
    text_pdf = process_pdf(pdf_path)
    text_chunks = get_chunks_from_pdf(text_pdf)
    vectore_store = get_vector_store(text_chunks)
    return vectore_store

def get_context_retriever_chain(vectore_store):
    llm = ChatOpenAI()
    retriever = vectore_store.as_retriever()
    #this prompt will be filled with the variables we will pass in the chain
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Erstelle basierend auf dem obigen Gespräch eine Suchanfrage, um Informationen zu erhalten, die für das Gespräch relevant sind.")
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    return retriever_chain

#final retriever chain, this is taking our user query, our chat history and is going to return us an answer based on the entire conversation
# and context the previous chain has found.
def get_conversational_rag_chain(retriever_chain): 
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Antworten Sie auf die Fragen des Benutzers ausschliesslich basierend auf dem untenstehenden Kontext.:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def get_response(chat_history, conversational_rag_chain, input):
    response = conversational_rag_chain.invoke({
        "chat_history": chat_history,
        "input": input
    })
    return response["answer"]

def init_mongodb_connection():
    # Retrieve the connection string from the environment variable
    mongo_db_connection_string = os.getenv("MONGO_DB_CONNECTION_STRING")

    if not mongo_db_connection_string:
        raise ValueError("MONGO_DB_CONNECTION_STRING is not set in the environment variables")

    client = MongoClient(mongo_db_connection_string)
    db = client["validationDB"]
    collection = db["answerValidation"]
    return collection

def upload_to_mongodb(input, answer, embeddings, collection, time_zone='Europe/Zurich'):
    # Get the current time in the specified time zone
    tz = pytz.timezone(time_zone)
    timestamp = datetime.now(tz)
    bot_embeddings_response = embeddings.embed_documents([answer])
    embeddingsBot = bot_embeddings_response[0]
    # Create the document to insert
    document = {
        "timestamp": timestamp,  # Add timestamp with time zone info
        "input": input,
        "answerBot": answer,
        "embeddingsBot": embeddingsBot,
        "validationAnswer": None,
        "embeddingsAnswer": None,
        "cosineSimilarity": None
    }
    # Insert the document into the collection
    collection.insert_one(document)
    print("Document inserted successfully")

def orchestrate_response_and_upload(chat_history, conversational_rag_chain, input, collection, embeddings):
    # Step 1: Get the chatbot's response
    chatbot_answer = get_response(chat_history, conversational_rag_chain, input)
    
    # Step 2: Upload the data to the database asynchronously
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(upload_to_mongodb, input, chatbot_answer, embeddings, collection)
    
    # Step 3: Return the chatbot's answer
    return chatbot_answer


def update_document(document_id, validation_answer, collection, embeddings):

    # Compute the embeddings for the validation answer
    validation_embeddings_response = embeddings.embed_documents([validation_answer])
    validation_embeddings = validation_embeddings_response[0]  # Extract the embedding vector

    # Update the document in MongoDB with the validation and embeddings
    collection.update_one(
        {"_id": ObjectId(document_id)},
        {
            "$set": {
                "validationAnswer": validation_answer,
                "embeddingsAnswer": validation_embeddings  # Store the vector as a list
            }
        }
    )
    print(f"Document {document_id} updated with validation and embeddings successfully")
     # Trigger cosine similarity calculation
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(trigger_cosine_similarity_calculation, document_id, collection)
    
#once the experienced employee gives us an answer we calculate the cosine similarity
def trigger_cosine_similarity_calculation(document_id, collection):
    document = collection.find_one({"_id": ObjectId(document_id)})
    if document and document.get("embeddingsBot") and document.get("embeddingsAnswer"):
        embeddingsBot = document["embeddingsBot"]
        embeddingsAnswer = document["embeddingsAnswer"]
        cosine_similarity = calculate_cosine_similarity(embeddingsBot, embeddingsAnswer)
        
        # Update the document with the cosine similarity
        collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"cosineSimilarity": cosine_similarity}}
        )
        print(f"Document {document_id} updated with cosine similarity {cosine_similarity}")

def calculate_cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    return dot_product / (norm_vec1 * norm_vec2)

def calculate_average_cosine_similarity(collection):
    pipeline = [
        {"$match": {"cosineSimilarity": {"$ne": None}}},
        {"$group": {"_id": None, "averageCosineSimilarity": {"$avg": "$cosineSimilarity"}}}
    ]
    result = collection.aggregate(pipeline)
    average_cosine_similarity = list(result)[0]["averageCosineSimilarity"]
    return average_cosine_similarity

#have old documents in the db that will not get updated by the other triggers.
def update_old_documents(collection):
    # Fetch documents where embeddingsAnswer is not None and cosineSimilarity is None
    documents = collection.find({"embeddingsAnswer": {"$ne": None}, "cosineSimilarity": None})

    for doc in documents:
        embeddingsBot = doc.get("embeddingsBot")
        embeddingsAnswer = doc.get("embeddingsAnswer")
        
        if embeddingsBot and embeddingsAnswer:
            # Ensure the embeddings are numpy arrays
            embeddingsBot = np.array(embeddingsBot)
            embeddingsAnswer = np.array(embeddingsAnswer)
            
            # Calculate cosine similarity
            cosine_similarity = calculate_cosine_similarity(embeddingsBot, embeddingsAnswer)
            
            # Update the document with the calculated cosine similarity
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"cosineSimilarity": cosine_similarity}}
            )
            print(f"Document {doc['_id']} updated with cosine similarity {cosine_similarity}")

def get_systems_health(collection):
    
    average_cosine_similarity = calculate_average_cosine_similarity(collection)
    
    if average_cosine_similarity < 0.8:
        return "Momentan sind die Antworten unseres Systems nicht ganz mit den Antworten erfahrener Mitarbeiter abgestimmt. Wir kümmern uns um die Situation."
    else:
        return "Derzeit entspricht die Qualität unserer Antworten den Antworten erfahrener Mitarbeiter."
