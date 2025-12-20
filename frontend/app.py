import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI PDF Knowledge Assistant")
st.title("📘 AI PDF Knowledge Assistant")

# ---------------- SESSION ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# ---------------- UPLOAD ----------------
st.subheader("📤 Upload PDFs (up to 100 MB)")

uploaded_file = st.file_uploader(
    "Upload study notes PDF",
    type=["pdf"]
)

if uploaded_file:
    with st.spinner("Uploading and processing PDF (large files may take time)..."):
        files = {
            "file": (uploaded_file.name, uploaded_file, "application/pdf")
        }

        data = {}
        if st.session_state.session_id:
            data["session_id"] = st.session_state.session_id

        try:
            response = requests.post(
                f"{BACKEND_URL}/upload-pdf",
                files=files,
                data=data,
                timeout=600
            )

            res = response.json()

            
            if "session_id" in res and "error" not in res:
                st.session_state.session_id = res["session_id"]
                st.success("✅ PDF uploaded and added to knowledge base!")
                st.info("You can upload more PDFs or ask questions.")
            else:
                st.error(f"❌ Upload failed: {res.get('error', 'Unknown error')}")

        except Exception as e:
            st.error(f"❌ Upload error: {e}")

# ---------------- ASK ----------------
st.subheader("💬 Ask Questions from Uploaded Notes")

question = st.text_input("Type your question here")

if st.button("Ask"):
    if not st.session_state.session_id:
        st.warning("⚠️ Please upload at least one PDF first.")
    elif not question.strip():
        st.warning("⚠️ Enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "question": question,
                    "session_id": st.session_state.session_id
                }

                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    data=payload,
                    timeout=300
                )

                if response.status_code == 200:
                    answer = response.json().get("answer", "")
                    st.markdown("### ✅ Answer")
                    st.write(answer)
                else:
                    st.error("❌ Failed to get answer")

            except Exception as e:
                st.error(f"❌ Error: {e}")

st.caption("AI answers are generated strictly from uploaded PDF notes.")
