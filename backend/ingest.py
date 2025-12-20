from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# One user → one vectorstore (multi-PDF)
user_vectorstores = {}

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Promotion keywords (keep minimal)
PROMO_KEYWORDS = [
    "ascent circle", "join", "register", "contact",
    "telegram", "whatsapp", "fees", "batch"
]

def is_promotional(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in PROMO_KEYWORDS)

def ingest_pdf(session_id, pdf_path):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    
    clean_chunks = [
        c for c in chunks
        if len(c.page_content.strip()) > 30   
        and not is_promotional(c.page_content)
    ]

    if not clean_chunks:
        clean_chunks = [
            c for c in chunks
            if len(c.page_content.strip()) > 30
        ]

    if not clean_chunks:
        raise ValueError("No valid study content found")

    # Add to existing knowledge base
    if session_id in user_vectorstores:
        user_vectorstores[session_id].add_documents(clean_chunks)
    else:
        user_vectorstores[session_id] = FAISS.from_documents(
            clean_chunks, embeddings
        )

def get_vectorstore(session_id):
    return user_vectorstores.get(session_id)
