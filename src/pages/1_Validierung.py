import streamlit as st
from methods import init_mongodb_connection, update_document
from bson.objectid import ObjectId
from langchain_openai import OpenAIEmbeddings

# we need this to update the documents inside of our
# Initialize MongoDB connection
collection = init_mongodb_connection()

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Set Streamlit page configuration
st.set_page_config(page_title="Validierung", page_icon="✅")
st.title("Validierung")  # Title of the page

# Sidebar with instructions for answering questions
# Explanation on how the answers based on the questions should be answered.
# with st.sidebar:
#     st.write("Beantworte bitte die Frage präzise und konkret:")
#     st.write("1. Halte deine Antwort kurz und prägnant.")
#     st.write("2. Konzentriere dich auf relevante Informationen, die die Frage direkt beantworten.")
#     st.write("3. Stelle sicher, dass die Antwort klar und verständlich ist.")
#     st.write("4. Wenn eine detaillierte Erklärung notwendig ist, teile die Antwort in klare, unterscheidbare Abschnitte.")

with st.sidebar:
    st.write("Please answer the question precisely and concretely:")
    st.write("1. Keep your answer short and concise.")
    st.write("2. Focus on relevant information that directly answers the question.")
    st.write("3. Ensure the answer is clear and understandable.")
    st.write("4. If a detailed explanation is necessary, divide the answer into clear, distinguishable sections.")

# Fetch all documents from MongoDB collection where validationAnswer is None
documents = list(collection.find({"validationAnswer": None}))

if documents:
    # Display each document one by one
    for doc in documents:
        # Displaying the question (assuming "Frage" means "Question" in German)
        st.write("Frage")
        # Display the question content from the document
        st.write(doc["input"])

        # Container for user input and update button
        with st.container():
            validation_answer = st.text_input(
                f"Beantworte die Frage, wie beschrieben", key=str(doc['_id']))

            # Button to add validation answer
            if st.button(f"Füge Antwort hinzu", key=f"button_{str(doc['_id'])}"):
                # Call method to update the document with validation answer and embeddings
                update_document(
                    str(doc['_id']), validation_answer, collection, embeddings)
                # st.success(f"Bewertung erfolgreich hinzugefügt {str(doc['_id'])}!") - I am not sure if i want to use this. Try it with and without and tell me what is faster :D. Wanted it for double safety. Thanks!
                # Refresh the page to show the next document
                st.experimental_rerun()
else:
    # Warning if no documents are found in the collection
    st.warning("No documents found.")
