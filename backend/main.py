from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uuid

from ingest import ingest_pdf
from rag import get_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backend running"}

# ---------------- UPLOAD PDF ----------------
@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile,
    session_id: str = Form(None)
):
    
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        pdf_path = f"temp_{session_id}_{file.filename}"

        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        ingest_pdf(session_id, pdf_path)

        return {
            "session_id": session_id,
            "message": "PDF uploaded and added to knowledge base"
        }

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return {
            "session_id": session_id,   
            "error": str(e)
        }

# ---------------- CHAT ----------------
@app.post("/chat")
async def chat(
    question: str = Form(...),
    session_id: str = Form(...)
):
    answer = get_answer(session_id, question)
    return {"answer": answer}

