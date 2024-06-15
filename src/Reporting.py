# the purpose of this is to create also a reporting landscape around the RAG-Chabot. A user's question is a sign of lack of knowledge.
# so what if we gather the questions from users and let AI generate an email emphazising what is missing and specifying around what subjects training is needed.
# For simplicity I will write this as a python script. Imagine using Airflow - that would be nice. Documents have a date on them.
# This is an experiment for the sake of fun.

import os
from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv
from methods import init_mongodb_connection
import openai
from openai import OpenAI


load_dotenv()
client = OpenAI()
# MongoDB connection details

# Email credentials - change receiver to your own mail.
EMAIL_SENDER = 'chatbotreporting@gmail.com'
EMAIL_PASSWORD = os.getenv("EMAIL")
EMAIL_RECEIVER = 'sonah5009@gmail.com'

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


# Step 1: Get documents from MongoDB
def get_documents_from_mongodb(collection):
    documents = collection.find({}, {"input": 1})
    inputs = [doc["input"] for doc in documents]
    return inputs


# Step 2: Send data to OpenAI
def get_openai_response(inputs):
    # german
    messages = [
        {"role": "system", "content": "Du bist ein Assistent, der dabei hilft, prägnante, präzise und kompakte Nachrichten zu verfassen. Du heisst Reporting Assistent und signierst die Nachrichten selber."},
        {"role": "user", "content": f"Anhand dieser Fragen von verschiedenen Benutzern: {inputs}, bitte verfasse eine prägnante, präzise und kompakte Nachricht, in der du dem Teamleiter berichtest, welche Wissenslücken bei den Mitarbeitern bestehen und genaue Empfehlungen für Trainings zu bestimmten Themen gibst, die sich auf die gestellten Fragen beziehen. Die Empfehlungen und die Themen sollten sich auf die in den Fragen erwähnten Versicherungen beziehen. Vermeide bitte einen Betreff in deiner Antwort."}
    ]

    # english
    messages = [
        {"role": "system", "content": "You are an assistant who helps to write concise, precise, and compact messages. Your name is Reporting Assistant and you sign the messages yourself."},
        {"role": "user",  "content": f"Based on these questions from different users: {inputs}, please write a concise, precise, and compact message reporting to the team leader about the knowledge gaps among the employees and providing specific training recommendations on certain topics related to the questions asked. The recommendations and topics should be related to the insurances mentioned in the questions. Please avoid including a subject line in your response."}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500
    )

    content = response.choices[0].message.content.strip()

    return content


# Step 3: Send the email
def send_email(body):
    em = EmailMessage()
    em['From'] = EMAIL_SENDER
    em['To'] = EMAIL_RECEIVER
    em['Subject'] = 'Report on Lacking Knowledge'
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, em.as_string())


# Main function to execute the workflow
def main():
    # MongoDB connection details
    collection = init_mongodb_connection()
    # Ensure environment variables are set
    if not EMAIL_PASSWORD or not OPENAI_API_KEY:
        raise ValueError(
            "EMAIL_PASSWORD and OPENAI_API_KEY environment variables must be set")

    # Get user questions from MongoDB
    user_questions = get_documents_from_mongodb(collection)
    if not user_questions:
        print("No user questions found in MongoDB.")
        return

    # Get response from OpenAI
    email_body = get_openai_response(user_questions)

    # Send the email
    send_email(email_body)
    print("Email sent successfully!")


main()
# if __name__ == "__main__":
#     main()
