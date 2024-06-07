Final project for ML2 

**Project Overview**
This project aims to develop a Retrieval-Augmented Generation (RAG) Chatbot for Medicall AG, a company providing round-the-clock assistance in various fields, including medical assistance, professional support in case of breakdowns and accidents, and emergency calls for senior citizens. The RAG-Chatbot is designed to assist employees by providing quick access to information about insurance coverage, thereby improving the efficiency of operations and reducing the burden on experienced employees.

**Motivation**
I have been working for Medicall AG for the past four years, where I started in the department responsible for organizing help in case of breakdowns or accidents involving automobiles. The processes in this department are knowledge-intensive and often require the intervention of experienced employees to support less experienced staff. Currently, I work as an IT service manager and aim to leverage my experience to build a RAG-Chatbot that can assist employees by providing instant information about insurance coverage. This will enable experienced employees to focus on more critical tasks and improve overall efficiency.

**Project Structure**
The project is organized into several key components:

methods.py: Contains the core methods for processing PDFs, creating vector stores, managing the chatbot's conversational chains, validatig answers, uploading and updating documents on mongodb
mongotest.py: A script to test the MongoDB connection.
reporting.py: Generates reports based on user questions and sends emails to highlight areas where training is needed.
Support.py: A Streamlit app providing a user interface for interacting with the chatbot and a checking system health button.
1_Validierung.py: A page in my app for validating chatbot responses with the help of experienced employees.

**Data** 
I spent 2 hours of my life trying to find the policies for the assistance coverages from the insurances we work with. Sadly i just found 3. I had to copy information and also type it myself because the format was a picture and not text. At the end i came up with the pdf "Leistngen".

**Used Technologies**
This project leverages a variety of technologies and libraries to build a robust RAG-Chatbot system:

1. Programming Languages 
    
    Python: The primary programming language used for developing the backend logic, data processing, and interaction with machine learning models.

2. Libraries and Frameworks

    PyPDF2: For extracting text from PDF documents.
    Langchain: For building conversational AI chains and managing chat history.
    Chroma: For creating and managing vector stores for document retrieval.
    OpenAI: For generating embeddings and creating conversational models.
    pymongo: For interacting with MongoDB databases.
    bson: For handling MongoDB object IDs.
    datetime: For managing dates and times.
    pytz: For handling time zones.
    dotenv: For loading environment variables from a .env file.
    numpy: For numerical computations and handling embeddings.
    Streamlit: For building interactive web applications and user interfaces.

3. Databases
    MongoDB: A NoSQL database used for storing chatbot responses, validation answers, and calculated embeddings.

4. Cloud and API Services:
    OpenAI API: Used for generating embeddings and creating chatbot responses using language models.

**Directory Structure**
project_root/
├── .venv/
├── src/
│   ├── __pycache__/
│   ├── db/
│   ├── pages/
│   │   └── 1_Validierung.py
│   ├── .env
│   ├── Leistungen.pdf
│   ├── methods.py
│   ├── mongotest.py
│   ├── Reporting.py
│   ├── Support.py
├── .gitignore
├── Motivation.pdf
├── README.md
├── requirements.txt

**Setup and Installation**
1. Clone the Repository: git clone <repository_url>
2. Set Up Virtual Environment: I run this on python version 3.10.11. If you use VS Code you will find how to create a virtual enviroment under this link https://code.visualstudio.com/docs/python/environments 
3. Activate venv: I am a Windows user and activate my venv with ".venv\Scripts\activate" - if you use mac, check please how to do it. 
4. Install Requirements: After activating the venv you can do pip install -r requirements.txt - if you don't have pip, you should get it. It's nice. https://pip.pypa.io/en/stable/installation/
5. Environment Variables: Create a .env file in the root directory and add the following - 
    MONGO_DB_CONNECTION_STRING=your_mongodb_connection_string
    OPENAI_API_KEY=your_openai_api_key
    EMAIL=your_email_password
    Please contact me, i am going to provide all keys. So you get the full experience. 

**Setup Instructions for macOS Users**
Setup for macOS Users shouldn't vary that much, but i am not sure, i am a windows user. Please check this: 

- Modify any Windows-style file paths to Unix-style paths in the code.
- Check how to import os variables. 
- If there is any libraries that are not available for macOS, what i don't think, just comment them out and try again. 

**Running the Project**

The only error i sometimes got, was from mongodb because the connection needed too long. I just refreshed and it functioned. 

1. You should creat a folder inside of the src folder for chromaDB. This is needed to make it persistent. You will find a comment on the methods.py file. Please change the path from the folder. Also in the Support.py, please change the path for the file "Leistungen".

2. MongoDB Connection Test: once you have gotten all keys run the mongotest.py to check if the connection to my mongodb collections runs smoothly. On the terminal you of course need to cd src and then to run the script enter python mongotest.py.

3. Streamlit App: Once you succesfully tested the connection to the mongodb, let's run the app. You do this by entering streamlit run Support.py on your terminal. 

4. I have prepared something for you. I have questions you can pose and also answers from one of the department's managers so you can validate them and test the whole process. I have also answers from the manager, for questions i did. You would play the part of the manager and write the answers. 

        So first we chat: 

            - Question: Ich habe einen Kunden am Telefon, er ist im Ausland und hat eine Panne. Das Auto
                        kann leider nicht repariert werden und muss in der Garage bleiben. Die Garage
                        verlangt Standgebühren von 500 Franken. Ist das gedeckt? Er hat den VCS-
                        Schutzbrief.

            - Question: Ein Kunde, der über ERV versichert ist, hat eine Frage bezüglich
                        Rückholungstransport eines damals gestohlenen Autos. Der Diebstahl hat vor 4
                        Monate im Ausland stattgefunden. Die spanische Polizei hat das Fahrzeug wieder
                        und hat ihm mitgeteilt, man könne das Fahrzeug holen. Ist dieser Transport gedeckt?

            - Question: Ein Kunde, der über VCS-Schutzbrief versichert ist, hat eine Panne im Ausland. Man
                        muss Ersatzteile bestellen. Ist die Spedition der Ersatzteile gedeckt?

            - Question: Wie lange kann ein Kunde der VCS ein Mietfahrzeug haben? Er hat eine Panne in
                        der Schweiz und sein Auto kann erst in einer Woche repariert werden.
        
        Now change to the "Validierung" site by clicking on the name in the Sidebar. As I said, there are questions i did in
        order to test the functionality of my ideas. Validate them all by entering the answers i got from the manager and clicking on the button to add answers. 

            - Question: Ein Kunde möchte wissen, ob alle Insassen seines Fahrzeugs versichert sind oder
                        nur er selbst. Wie soll ich darauf antworten? Er ist beim VCS versichert.
                        
            - Answer:   Wenn ich die Frage richtig verstehe, dann geht es darum ob Insassen ebenfalls von
                        Versicherungsleistungen profitieren können. Fahrzeuginsassen sind grundsätzlich beim VCS mitversichert. Sie können von der Heim- oder Weiterreise mit dem öffentlichen Verkehr oder Taxi profitieren oder mit dem Fahrzeughalter zusammen einen Mietwagen erhalten. Die Kosten sind hierzu aber gesamthaft limitiert mit 400.- CHF.
                        Ausserdem wäre eine Übernachtung in einer Unterkunft mit 150.- CHF pro Fahrzeuginsasse gedeckt, falls die Heim- oder Weiterreise nicht gleichentags möglich ist.

            - Question:  Ich habe einen Kunden am Telefon. Er ist beim VCS versichert. Er hatte einen Unfall
                        und fragt, ob die Bergungskosten seines Fahrzeugs abgedeckt sind. Wenn ja, bis wie
                        viel?
            - Answer:   Ja, die Bergungskosten sind beim VCS versichert. Die Bergungskosten sind bis maximal 1000.- CHF gedeckt. 
                        Dabei muss darauf geachtet werden, dass die eventuell hinzukommenden Transportkosten, ebenfalls in diese 1000.- CHF inkludiert sind.

            - Question: Ein Kunde möchte wissen, ob er die Wahl hat, ein Flugbillett anstelle eines
                        Bahnbilletts für die Rückreise zu wählen, wenn sein Auto im Ausland nicht innerhalb von 5 Tagen repariert werden kann. Er ist bei Smile Direct versichert. 
                        
            - Answer    Wenn das Fahrzeug nicht innert 5 Tagen reparierbar ist, ist der Kunde bei Heim- oder
                        Weiterreise für anstelle eines Bahnbillets auch für ein Flugticket versichert. Dabei
                        muss beachtet werden, dass nur Flüge in der Economy Class gedeckt und die maximalen Kosten 1500.- CHF pro Insasse sind.

            - Question: Ein Kunde fragt, ob er im Falle einer hohen Reparaturrechnung im Ausland einen
                        Kostenvorschuss erhalten kann. Wie genau funktioniert das und welche Bedingungen
                        sind daran geknüpft? Er ist bei Smile Direct versichert.

            - Answer:   Im Falle einer hohen Reparaturrechnung oder anderen ausserordentlichen
                        Ereignissen im Ausland kann der Kunde einen rückzuerstattenden Kostenvorschuss
                        erhalten. Der Vorschuss darf eine Höhe von maximal 2000.- CHF haben und muss bei der
                        Rückkehr in die Schweiz zurückbezahlt werden.

            - Question: Ich habe einen Kunden am Telefon, er ist im Ausland und hat eine Panne. Das Auto
                        kann leider nicht repariert werden und muss in der Garage bleiben. Die Garage
                        verlangt Standgebühren von 500 Franken. Ist das gedeckt? Er hat den VCS-
                        Schutzbrief.

            - Answer:   Die Standgebühren sind beim VCS-Schutzbrief versichert. Die Limite beträgt 500.-
                        CHF, wodurch der volle Betrag gedeckt ist.

            - Question: Ein Kunde, der über ERV versichert ist, hat eine Frage bezüglich Rückholungstransport eines 
                        damals gestohlenen Autos. Der Diebstahl hat vor 4 Monate im Ausland stattgefunden. Die spanische Polizei hat das Fahrzeug wieder und hat ihm mitgeteilt, man könne das Fahrzeug holen. Ist dieser Transport gedeckt?

            - Answer:   Der Versicherungsschutz bei der ERV besteht unter anderem auch bei Diebstahl.
                        Somit gelten die AVB und der Kunde hat eine Repatriierung zugute, falls das
                        Fahrzeug länger als 48h nicht aufgefunden wurde und falls der Zeitwert des
                        Fahrzeugs höher liegt, als die Kosten für die Rückführung. Das Fahrzeug wurde länger als 48h nicht aufgefunden, aber den Zeitwert des Fahrzeugs müsstest du noch überprüfen.

            - Question: Ein Kunde, der über VCS-Schutzbrief versichert ist, hat eine Panne im Ausland. Man
                        muss Ersatzteile bestellen. Ist die Spedition der Ersatzteile gedeckt?

            - Answer:   Ja, die Speditionskosten sind beim VCS-Schutzbrief gedeckt. Die Ersatzteile sind
                        allerdings nicht versichert.

            - Question: Wie lange kann ein Kunde der VCS ein Mietfahrzeug haben? Er hat eine Panne in
                        der Schweiz und sein Auto kann erst in einer Woche repariert werden. 
            - Answer:   Beim VCS ist der Mietwagen nur für Heim- oder Weiterreise und keinesfalls während der Reparatur. 
                        Deshalb kann der Kunde den Mietwagen maximal 3 Tage haben. Zudem müssen zwingende Gründe vorhanden sein, um den Erhalt eines Mietwagens zu rechtfertigen.

5. What happened? Check methods orchestrate_response_and_upload, update_document, trigger_cosine_similarity_calculation and calculate_cosine_similarity.

6. System's quality: So in this application we are using cosine similarity as a metric to decide if the answers the system is giving are good or not. The treshhold is set by 0.8. Change to the main page and click on the button "Systemstatus prüfen". 

The only error i sometimes got, was from mongodb because the connection needed too long. I just refreshed and it functioned. 

**Methods Overview**

Document Class
- **Description**: This class represents a document with its content and metadata.
- **Attributes**:
  - `content`: The text content of the document.
  - `metadata`: Metadata associated with the document (optional).

process_pdf
- **Description**: Extracts text from a PDF file.
- **Parameters**:
  - `pdf_path` (str): Path to the PDF file.
- **Returns**: Extracted text as a string.

get_chunks_from_pdf
- **Description**: Splits the extracted text from a PDF into smaller chunks.
- **Parameters**:
  - `text` (str): The extracted text from the PDF.
- **Returns**: List of text chunks.

get_vector_store
- **Description**: Creates a vector store from text chunks.
- **Parameters**:
  - `chunks` (list): List of text chunks.
- **Returns**: A vector store containing document embeddings.
- **Note**: The `persist_directory` path must be updated to match your local environment.

orchestration_pdf_vectore_store
- **Description**: Orchestrates the process of extracting text from a PDF, splitting it into chunks, and creating a vector store.
- **Parameters**:
  - `pdf_path` (str): Path to the PDF file.
- **Returns**: A vector store created from the PDF text chunks.

get_context_retriever_chain
- **Description**: Creates a context-aware retriever chain.
- **Parameters**:
  - `vectore_store`: The vector store created from document chunks.
- **Returns**: A context-aware retriever chain for querying the vector store.

get_conversational_rag_chain
- **Description**: Creates a conversational RAG (Retrieval-Augmented Generation) chain.
- **Parameters**:
  - `retriever_chain`: The retriever chain for fetching relevant documents.
- **Returns**: A conversational RAG chain for generating responses based on retrieved documents and chat history.

get_response
- **Description**: Generates a response based on the chat history and user input.
- **Parameters**:
  - `chat_history` (list): The history of the conversation.
  - `conversational_rag_chain`: The conversational RAG chain.
  - `input` (str): The user's input/query.
- **Returns**: The generated response as a string.

init_mongodb_connection
- **Description**: Initializes a connection to MongoDB.
- **Returns**: A MongoDB collection object for the "answerValidation" collection.

upload_to_mongodb
- **Description**: Uploads the input, chatbot response, and embeddings to MongoDB.
- **Parameters**:
  - `input` (str): The user's input/query.
  - `answer` (str): The chatbot's response.
  - `embeddings`: The embeddings model.
  - `collection`: The MongoDB collection object.
  - `time_zone` (str, optional): The time zone for the timestamp (default: 'Europe/Zurich').

orchestrate_response_and_upload
- **Description**: Orchestrates the process of generating a response and uploading it to MongoDB.
- **Parameters**:
  - `chat_history` (list): The history of the conversation.
  - `conversational_rag_chain`: The conversational RAG chain.
  - `input` (str): The user's input/query.
  - `collection`: The MongoDB collection object.
  - `embeddings`: The embeddings model.
- **Returns**: The chatbot's response as a string.

update_document
- **Description**: Updates a MongoDB document with the validation answer and its embeddings.
- **Parameters**:
  - `document_id` (str): The ID of the document to update.
  - `validation_answer` (str): The validation answer provided by an experienced employee.
  - `collection`: The MongoDB collection object.
  - `embeddings`: The embeddings model.

trigger_cosine_similarity_calculation
- **Description**: Triggers the calculation of cosine similarity between the chatbot's response and the validation answer.
- **Parameters**:
  - `document_id` (str): The ID of the document to update.
  - `collection`: The MongoDB collection object.

calculate_cosine_similarity
- **Description**: Calculates the cosine similarity between two vectors.
- **Parameters**:
  - `vec1` (list): The first vector.
  - `vec2` (list): The second vector.
- **Returns**: The cosine similarity as a float.

calculate_average_cosine_similarity
- **Description**: Calculates the average cosine similarity across all documents in the MongoDB collection.
- **Parameters**:
  - `collection`: The MongoDB collection object.
- **Returns**: The average cosine similarity as a float.

update_old_documents
- **Description**: Updates old documents in MongoDB that have validation answers but no cosine similarity calculated.
- **Parameters**:
  - `collection`: The MongoDB collection object.

get_systems_health
- **Description**: Evaluates the system's health based on the average cosine similarity of responses.
- **Parameters**:
  - `collection`: The MongoDB collection object.
- **Returns**: A message indicating the system's health.