# on this page we will write the methods we will need for our prototype

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


class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata if metadata is not None else {}


# get pdf text
def process_pdf(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text() if page.extract_text is not None else ""
    return text


# get chunks from pdf
def get_chunks_from_pdf(text):
    text_splitter = RecursiveCharacterTextSplitter()
    chunks = text_splitter.split_text(text)
    return chunks


# create vector store from chunks
def get_vector_store(chunks):
    # Set the directory where the vector store database will be saved
    persist_directory = "/Users/sonah/Library/CloudStorage/OneDrive-ZHAW/ML2/Final_project_ML2/src/db"
    # persist_directory = r"C:\Users\Admin\Desktop\ML2\Final_Project\src\db"

    # Initialize the OpenAI embeddings model
    embeddings = OpenAIEmbeddings()

    # Convert the given text chunks into Document objects
    documents = [Document(chunk) for chunk in chunks]

    # Create a vector store from the documents using the embeddings model and save it to the specified directory
    vectore_store = Chroma.from_documents(
        documents, embeddings, persist_directory=persist_directory)

    # Return the vector store object
    return vectore_store

    """
    FOR EXAMPLE
    chunks = ["This is a test sentence.", "Here is another sentence.", "Machine learning is fascinating."]
    vector_store = get_vector_store(chunks)
    
    This returns the created vector store object, which can be used later for various operations like searching or similarity calculations.
    """


# This is for using in Support.py
def orchestration_pdf_vectore_store(pdf_path):
    text_pdf = process_pdf(pdf_path)
    text_chunks = get_chunks_from_pdf(text_pdf)
    vectore_store = get_vector_store(text_chunks)
    # A vector store created from the PDF text chunks.
    return vectore_store


def get_context_retriever_chain(vectore_store):
    """
        1. Creating the Context Retriever Chain (Retrieval Phase):
        This function creates a chain that retrieves information using the vector store. 
        This chain uses user input and previous conversation history to search for relevant information.
    """

    # This is for using in Support.py
    # Creates a context-aware retriever chain using a language model and a vector store retriever.

    llm = ChatOpenAI()
    retriever = vectore_store.as_retriever()
    # this prompt will be filled with the variables we will pass in the chain
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Erstelle basierend auf dem obigen Gespräch eine Suchanfrage, um Informationen zu erhalten, die für das Gespräch relevant sind.")
        # Create a search request based on the above conversation to obtain information relevant to the conversation.
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    # A context-aware retriever chain for querying the vector store.
    return retriever_chain


def get_conversational_rag_chain(retriever_chain):
    """
        2. Creating the Conversational RAG Chain (Generation Phase):
        This function creates the final RAG chain by combining the retriever chain and a generative model. 
        The generative model uses the retrieved documents to answer user queries.
    """
    # final retriever chain, this is taking our user query, our chat history and is going to return us an answer based on the entire conversation
    # and context the previous chain has found.
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Antworten Sie auf die Fragen des Benutzers ausschliesslich basierend auf dem untenstehenden Kontext.:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        # "Respond to the user's questions solely based on the context below.:\n\n{!!!t}),
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
        raise ValueError(
            "MONGO_DB_CONNECTION_STRING is not set in the environment variables")

    client = MongoClient(mongo_db_connection_string)
    db = client["validationDB"]
    collection = db["answerValidation"]
    return collection


def upload_to_mongodb(input, answer, embeddings, collection, time_zone='Europe/Zurich'):
    """
    Uplads the (user's) input, (chatbot response) answer, and embeddings (model) to MongoDB.
    """
    # Get the current time in the specified time zone
    tz = pytz.timezone(time_zone)
    timestamp = datetime.now(tz)
    bot_embeddings_response = embeddings.embed_documents([answer])
    #       The embed_documents method of the embeddings object is called with the answer text.
    #  `answer` : converting -> into a numerical vector representation

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
    """
        3. Generating the Final Response and Uploading (Orchestration Phase):
        This function orchestrates the entire process. 
        It takes the user input and conversation history, generates a final response using retrieval and generation, 
        and uploads the data to the database.
    """
    # Step 1: Get the chatbot's response
    chatbot_answer = get_response(
        chat_history, conversational_rag_chain, input)

    # Step 2: Upload the data to the database asynchronously
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(upload_to_mongodb, input,
                        chatbot_answer, embeddings, collection)

    # Step 3: Return the chatbot's answer
    return chatbot_answer


"""
when I go to the `Validierung(Validation)` tab and answer the quesion like that;

question: Ein Kunde möchte wissen, ob alle Insassen seines Fahrzeugs versichert sind oder nur er selbst. Wie soll ich darauf antworten? Er ist beim VCS versichert.
answer: Beim Verkehrs-Club der Schweiz (VCS) sind in der Regel sowohl der Fahrzeughalter als auch die Insassen des Fahrzeugs versichert. Es kommt jedoch darauf an, welche spezifischen Versicherungsleistungen der Kunde gewählt hat. Der VCS bietet verschiedene Versicherungen an, darunter Haftpflichtversicherung, Teilkasko und Vollkasko.
^- Answer from the chatgpt site. That's why the similarity is high.
=>
Document 665b47eaabb145fcc25aae7e updated with validation and embeddings successfully
Document 665b47eaabb145fcc25aae7e updated with cosine similarity 0.9520938488463478
2024-06-13 03:08:51.472 Please replace `st.experimental_rerun` with `st.rerun`.

`st.experimental_rerun` will be removed after 2024-04-01.

---
question: my feeling is bad
answer: Ohhhhhhh. Who make you feeling so bad??? I can scold. :(
=>
Document 666a4256f9b6e41af2e41b3b updated with validation and embeddings successfully
Document 666a4256f9b6e41af2e41b3b updated with cosine similarity 0.7740296291928712
2024-06-13 03:14:22.856 Please replace `st.experimental_rerun` with `st.rerun`.
"""


def update_document(document_id, validation_answer, collection, embeddings):

    # Compute the embeddings for the validation answer
    validation_embeddings_response = embeddings.embed_documents(
        [validation_answer])
    # Extract the embedding vector
    validation_embeddings = validation_embeddings_response[0]

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
    print(
        f"Document {document_id} updated with validation and embeddings successfully")
    # Trigger cosine similarity calculation
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(trigger_cosine_similarity_calculation,
                        document_id, collection)

# once the experienced employee gives us an answer we calculate the cosine similarity


def trigger_cosine_similarity_calculation(document_id, collection):
    """
    embeddingsBot: an embedding vector for the answer generated by the chatbot.
    embeddingsAnswer: an embedding vector for the correct answer provided by the user (initially set to None).

    """
    document = collection.find_one({"_id": ObjectId(document_id)})
    if document and document.get("embeddingsBot") and document.get("embeddingsAnswer"):
        embeddingsBot = document["embeddingsBot"]
        embeddingsAnswer = document["embeddingsAnswer"]
        cosine_similarity = calculate_cosine_similarity(
            embeddingsBot, embeddingsAnswer)

        # Update the document with the cosine similarity
        collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"cosineSimilarity": cosine_similarity}}
        )
        print(
            f"Document {document_id} updated with cosine similarity {cosine_similarity}")


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
    """
    Calculates the average cosine similarity across all documents in the MongoDB collection.
    """
    pipeline = [
        {"$match": {"cosineSimilarity": {"$ne": None}}},
        {"$group": {"_id": None, "averageCosineSimilarity": {"$avg": "$cosineSimilarity"}}}
    ]
    result = collection.aggregate(pipeline)
    average_cosine_similarity = list(result)[0]["averageCosineSimilarity"]
    return average_cosine_similarity

# have old documents in the db that will not get updated by the other triggers.


def update_old_documents(collection):
    # Update old documents in MongoDB with validation answers but no cosine similarity calculated.
    # Fetch documents where embeddingsAnswer is not None and cosineSimilarity is None
    documents = collection.find(
        {"embeddingsAnswer": {"$ne": None}, "cosineSimilarity": None})

    for doc in documents:
        embeddingsBot = doc.get("embeddingsBot")
        embeddingsAnswer = doc.get("embeddingsAnswer")

        if embeddingsBot and embeddingsAnswer:
            # Ensure the embeddings are numpy arrays
            embeddingsBot = np.array(embeddingsBot)
            embeddingsAnswer = np.array(embeddingsAnswer)

            # Calculate cosine similarity
            cosine_similarity = calculate_cosine_similarity(
                embeddingsBot, embeddingsAnswer)

            # Update the document with the calculated cosine similarity
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"cosineSimilarity": cosine_similarity}}
            )
            print(
                f"Document {doc['_id']} updated with cosine similarity {cosine_similarity}")


def get_systems_health(collection):

    average_cosine_similarity = calculate_average_cosine_similarity(collection)

    if average_cosine_similarity < 0.8:
        # return "Momentan sind die Antworten unseres Systems nicht ganz mit den Antworten erfahrener Mitarbeiter abgestimmt. Wir kümmern uns um die Situation."
        return "At the moment, the answers of our system are not fully aligned with the answers of experienced employees. We'll take care of the situation."
    else:
        # return "Derzeit entspricht die Qualität unserer Antworten den Antworten erfahrener Mitarbeiter."
        return "Currently, the quality of our answers corresponds to the answers of experienced employees."
