import os
import psycopg2
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL")

genai.configure(api_key=os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY"))

@st.cache_resource
def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        print("✅ Database connected")
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

conn = init_db()
cursor = conn.cursor() if conn else None

# --- Session state init ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "saved_chunks" not in st.session_state:
    st.session_state.saved_chunks = []
if "sample_vector" not in st.session_state:
    st.session_state.sample_vector = None

# --- 2. CHUNKING & STORING ---
def process_and_store_text(raw_text):
    chunks = [chunk.strip() for chunk in raw_text.split('\n\n') if chunk.strip()]
    sample_embedding = None

    for i, chunk in enumerate(chunks):
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=chunk,
            task_type="retrieval_document",
            output_dimensionality=768
        )
        embedding = result['embedding']
        if i == 0:
            sample_embedding = embedding
        cursor.execute(
            "INSERT INTO document_chunks (content, embedding) VALUES (%s, %s)",
            (chunk, str(embedding))
        )
    conn.commit()
    return chunks, sample_embedding

# --- 3. SEARCHING ---
def search_similar_chunks(user_question, limit=3):
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=user_question,
        task_type="retrieval_query",
        output_dimensionality=768
    )
    question_embedding = result['embedding']
    cursor.execute(
        """
        SELECT content 
        FROM document_chunks 
        ORDER BY embedding <-> %s 
        LIMIT %s
        """,
        (str(question_embedding), limit)
    )
    return [row[0] for row in cursor.fetchall()]

# --- 4. GENERATING ANSWER ---
def generate_answer(user_question, context_chunks):
    context_text = "\n\n".join(context_chunks)
    prompt = f"""
    You are a helpful AI assistant. Answer the user's question ONLY using the provided context. 
    If the answer is not in the context, say "I cannot answer this based on the uploaded text."
    
    Context:
    {context_text}
    
    Question: {user_question}
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Upload Knowledge")
    document_text = st.text_area("Paste document text:", height=200)

    if st.button("Store in Database"):
        if document_text and conn:
            with st.spinner("Chunking and generating Gemini embeddings..."):
                saved_chunks, sample_vector = process_and_store_text(document_text)
                # ✅ Save to session state immediately
                st.session_state.saved_chunks = saved_chunks
                st.session_state.sample_vector = sample_vector
            st.success(f"Saved {len(saved_chunks)} chunks to the database!")
        else:
            st.warning("Please paste some text first.")

    # ✅ Rendered OUTSIDE the button block — persists across reruns
    if st.session_state.saved_chunks:
        st.markdown("---")
        st.subheader("🕵️‍♂️ Under the Hood")
        with st.expander("1. See the Text Chunks"):
            st.write("We split your text by paragraphs. Here is exactly how the database stored it:")
            for i, chunk in enumerate(st.session_state.saved_chunks):
                st.info(f"**Chunk {i+1}:** {chunk}")

        if st.session_state.sample_vector:
            with st.expander("2. See the Vector Embeddings"):
                st.write("The AI turns every chunk into an array of 768 numbers. Here are the first 15 numbers of **Chunk 1**:")
                preview = st.session_state.sample_vector[:15] + ["... and 753 more numbers!"]
                st.json(preview)

# --- MAIN ---
st.title("🧠 Basic AI Q&A System")
st.header("2. Ask a Question")
question = st.text_input("What would you like to know about the text you uploaded?")

if st.button("Get Answer"):
    if question and conn:
        with st.spinner("Searching database and thinking..."):
            relevant_chunks = search_similar_chunks(question)
            if not relevant_chunks:
                st.warning("No context found. Did you upload text first?")
            else:
                answer = generate_answer(question, relevant_chunks)
                st.session_state.chat_history.append({"role": "user", "text": question})
                st.session_state.chat_history.append({"role": "ai", "text": answer})

# ✅ Chat history rendered OUTSIDE the button block — persists across reruns
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.write(f"**🧑 You:** {msg['text']}")
    else:
        st.write("### ✨ AI Answer:")
        st.success(msg["text"])