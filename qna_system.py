import os
import psycopg2
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

# --- 1. SETUP & CONFIGURATION ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configure the free Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@st.cache_resource
def init_db():
    try:
        # conn = psycopg2.connect(
        #     dbname=st.secrets["POSTGRES_DB"],
        #     user=st.secrets["POSTGRES_USER"],
        #     password=st.secrets["POSTGRES_PASSWORD"],
        #     host=st.secrets["POSTGRES_HOST"],
        #     port=st.secrets["POSTGRES_PORT"]
        # )
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Database connected")
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

conn = init_db()
cursor = conn.cursor() if conn else None

# --- 2. CHUNKING & STORING (GEMINI VERSION) ---
def process_and_store_text(raw_text):
    chunks = [chunk.strip() for chunk in raw_text.split('\n\n') if chunk.strip()]
    
    sample_embedding = None # We will grab one embedding to show you on screen
    
    for i, chunk in enumerate(chunks):
        # Get the native 768-dimension embedding
        result = genai.embed_content(
            model="models/text-embedding-004", 
            content=chunk,
            task_type="retrieval_document"
        )
        embedding = result['embedding']
        
        # Save the very first embedding to display in the UI later
        if i == 0:
            sample_embedding = embedding
            
        # Store in PostgreSQL
        cursor.execute(
            "INSERT INTO document_chunks (content, embedding) VALUES (%s, %s)",
            (chunk, str(embedding))
        )
    conn.commit()
    
    # Return the raw data so Streamlit can display it!
    return chunks, sample_embedding

# --- 3. SEARCHING (GEMINI VERSION) ---
def search_similar_chunks(user_question, limit=3):
    # Convert the user's question into a Gemini embedding
    result = genai.embed_content(
        model="models/text-embedding-004", 
        content=user_question,
        task_type="retrieval_query"
    )
    question_embedding = result['embedding']
    
    # PG Vector <-> operator finds the closest matches
    cursor.execute(
        """
        SELECT content 
        FROM document_chunks 
        ORDER BY embedding <-> %s 
        LIMIT %s
        """,
        (str(question_embedding), limit)
    )
    
    results = cursor.fetchall()
    return [row[0] for row in results]

# --- 4. GENERATING THE ANSWER (GEMINI VERSION) ---
def generate_answer(user_question, context_chunks):
    context_text = "\n\n".join(context_chunks)
    
    # We combine the system prompt and user prompt for Gemini
    prompt = f"""
    You are a helpful AI assistant. Answer the user's question ONLY using the provided context. 
    If the answer is not in the context, say "I cannot answer this based on the uploaded text."
    
    Context:
    {context_text}
    
    Question: {user_question}
    """
    
    # Use the fast, free Gemini 2.5 Flash model
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    return response.text

# --- STREAMLIT WEB INTERFACE ---
st.title("🧠 My Free AI Q&A System")

with st.sidebar:
    st.header("1. Upload Knowledge")
    document_text = st.text_area("Paste document text:", height=200)
    
    if st.button("Store in Database"):
        if document_text and conn:
            with st.spinner("Chunking and generating Gemini embeddings..."):
                # Catch the new return values
                saved_chunks, sample_vector = process_and_store_text(document_text)
                
            st.success(f"Saved {len(saved_chunks)} chunks to the database!")
            
            # --- THE BLACK BOX BREAKER ---
            st.markdown("---")
            st.subheader("🕵️‍♂️ Under the Hood")
            
            with st.expander("1. See the Text Chunks"):
                st.write("We split your text by paragraphs. Here is exactly how the database stored it:")
                for i, chunk in enumerate(saved_chunks):
                    st.info(f"**Chunk {i+1}:** {chunk}")
                    
            with st.expander("2. See the Vector Embeddings"):
                st.write("The AI turns every chunk into an array of 768 numbers. Here are the first 15 numbers of **Chunk 1**:")
                # We only show 15 so it doesn't crash your browser tab!
                preview = sample_vector[:15]
                preview.append("... and 753 more numbers!")
                st.json(preview)
                
        else:
            st.warning("Please paste some text first.")

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
                
                # Show the final AI Answer
                st.write("### ✨ AI Answer:")
                st.success(answer)
                
                # --- DEMYSTIFYING THE SEARCH ---
                st.write("---")
                st.write("### 🔍 How it found this answer:")
                st.write("We converted your question into a vector, compared it against the database, and pulled these closest matches. The AI *only* saw this text:")
                
                for i, chunk in enumerate(relevant_chunks):
                    st.code(f"Retrieved Context {i+1}:\n{chunk}", language="text")