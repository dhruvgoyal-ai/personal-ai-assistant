from backend.ingest import get_vectorstore
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import os

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    temperature=0
)

def get_answer(session_id: str, question: str):
    if not session_id:
        return "❌ Please upload a PDF first."

    vectorstore = get_vectorstore(session_id)

    if vectorstore is None:
        return "❌ Please upload a PDF first."

    docs = vectorstore.similarity_search(question, k=4)

    if not docs:
        return "❌ Answer not found in the uploaded PDF."

    context = "\n\n".join(doc.page_content for doc in docs)

    messages = [
        SystemMessage(
            content=(
                "You are a PDF-based assistant. "
                "Answer ONLY from the given PDF content. "
                "If answer is not present, say: "
                "'Answer not found in the uploaded PDF.'"
            )
        ),
        HumanMessage(
            content=f"""
PDF Content:
{context}

Question:
{question}
"""
        )
    ]

    response = llm(messages)
    return response.content
