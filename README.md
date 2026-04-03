# 🧠 Free AI Q&A System

A powerful, free AI-powered question-answering system that uses **Google Gemini API** for embeddings and text generation, combined with **Supabase** (PostgreSQL + pgvector) for vector similarity search. Upload any document, ask questions, and get intelligent answers based only on your uploaded content.

---

## 🚀 Live Demo

**Try it now:** [https://rag-basic-qna-app.streamlit.app/](https://rag-basic-qna-app.streamlit.app/)

Deployed on **Streamlit Cloud** with **Supabase** backend.

---

## ✨ Features

- 📄 **Upload & Process Documents** — Paste any text and automatically split it into semantic chunks
- 🔍 **Vector Search** — Find the most relevant content using AI-powered embeddings (768-dimensional vectors)
- 🤖 **AI-Generated Answers** — Get contextually accurate answers using Google Gemini 2.5 Flash
- 🚀 **Free to Use** — Leverages free tier of Google Gemini API
- 🔓 **Transparent Search** — See exactly which chunks the AI used to answer your question
- 🎨 **Interactive UI** — Beautiful Streamlit web interface with real-time feedback

---

## 🏗️ How It Works

### 1. **Document Processing**
```
Raw Text Input
    ↓
Split by Paragraphs (\\n\\n)
    ↓
Generate 768-Dimensional Vectors (Gemini Embeddings)
    ↓
Store in Supabase (PostgreSQL + pgvector)
```

### 2. **Question & Answer**
```
User Question
    ↓
Convert to Vector (same 768-dim space)
    ↓
Find 3 Most Similar Chunks (cosine distance)
    ↓
Send Context + Question to Gemini API
    ↓
Return AI-Generated Answer
```

---

## 🔧 Project Structure

```
Basic_QnA_System/
├── qna_system.py      # Main Streamlit application
├── README.md          # This file
├── .env               # Environment variables (not in repo)
└── requirements.txt   # Python dependencies
```

---

## 📋 Requirements

- **Python 3.8+**
- **Supabase Account** (free tier at https://supabase.com)
- **Google Gemini API Key** (free tier available)
- **Internet connection** (for API calls)

---

## ⚙️ Installation & Setup

### 1. **Clone/Download the Project**
```bash
cd Basic_QnA_System
```

### 2. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Set Up Supabase Database**

**1. Create a Supabase Project:**
- Go to [https://supabase.com](https://supabase.com) and sign up (free tier)
- Create a new project
- Go to **SQL Editor** and run the following:

**2. Enable pgvector extension:**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**3. Create the document_chunks table:**
```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster similarity search
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);
```

**4. Get Connection String:**
- In Supabase dashboard → **Settings → Database → Connection pooling**
- Copy the connection string

### 5. **Configure Environment Variables**

Create a `.env` file in the project root:
```bash
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Database (copy from connection string)
POSTGRES_DB=postgres
POSTGRES_USER=postgres.xxxxxxxxxxxxxxx
POSTGRES_PASSWORD=your_supabase_password
POSTGRES_HOST=db.xxxxxxxxxxxxxxx.supabase.co
POSTGRES_PORT=5432
```

**Get API Keys:**
- **Gemini API key:** https://ai.google.dev/
- **Supabase connection string:** Settings → Database → Connection pooling

---

## 🚀 Running the Application

```bash
streamlit run qna_system.py
```

The app will open at `http://localhost:8501`

---

## 💻 Usage Guide

### **Step 1: Upload Knowledge**
1. In the sidebar, paste any document text
2. Click **"Store in Database"**
3. View the chunks and vector embeddings under "Under the Hood"

### **Step 2: Ask Questions**
1. Type your question in the main section
2. Click **"Get Answer"**
3. View the AI answer and retrieved chunks

### **Example Input:**
```
Artificial Intelligence is transforming industries worldwide. 
Machine Learning enables computers to learn from data without explicit programming.

Deep Learning uses neural networks to process complex patterns in data.
Natural Language Processing helps computers understand human language.
```

### **Example Question:**
```
What is machine learning?
```

### **Expected Answer:**
```
Machine Learning enables computers to learn from data without explicit programming.
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                         │
│         (Upload Document | Ask Question | View Results)     │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   ┌─────────┐    ┌─────────────┐   ┌──────────┐
   │  Text   │    │ Embeddings  │   │ Context  │
   │Chunking │    │  (Gemini)   │   │Management│
   └────┬────┘    └──────┬──────┘   └────┬─────┘
        │                │               │
        └────────────────┼───────────────┘
                         ↓
        ┌────────────────────────────────┐
        │   Supabase (PostgreSQL +       │
        │         pgvector)              │
        │  (Vector Storage & Search)     │
        └────────────────────────────────┘
                         │
                         ↓
        ┌────────────────────────────────┐
        │  Google Gemini API             │
        │  (Text Generation)             │
        └────────────────────────────────┘
```

---

## 🔑 Key Components Explained

| Component | Purpose |
|-----------|---------|
| **Chunking** | Splits text into manageable pieces for embedding |
| **Embeddings** | Converts text into 768-dimensional vectors (semantic meaning) |
| **Vector DB** | Supabase (PostgreSQL + pgvector) for fast similarity search |
| **Cosine Distance** | Measure similarity between vectors (`<->` operator) |
| **Gemini API** | Generates human-like answers based on context |

---

## 🚨 Troubleshooting

### **"Database connection failed"**
- Check Supabase project is active
- Verify Supabase credentials in `.env`
- Ensure `document_chunks` table exists in Supabase
- Check if using **Connection pooling** endpoint

### **"No context found. Did you upload text first?"**
- Upload text first using the sidebar
- Wait for "Saved X chunks" confirmation

### **"GEMINI_API_KEY not found"**
- Create `.env` file in project root
- Add `GEMINI_API_KEY=your_key`
- Restart the Streamlit app

### **Slow search performance**
- Verify ivfflat index is created: `SELECT * FROM pg_indexes WHERE tablename='document_chunks';`
- Supabase free tier: limit document size or upgrade plan

---

## 📈 Performance Tips

1. **Keep chunks under 500 tokens** — Smaller chunks = better search accuracy
2. **Use meaningful paragraphs** — Split text naturally by topics
3. **Index the embeddings column** — Required for fast similarity search
4. **Batch API calls** — Process multiple documents to save API quota

---

## 💰 Cost Estimation

- **Gemini API** — Free tier (60 requests/min, embeddings free)
- **Supabase** — Free tier (excellent for this project, $25+/month for production)
- **Streamlit** — Community Cloud (free) or [Streamlit Cloud](https://streamlit.io/cloud)

---

## 🌐 Deployment

### **Option 1: Streamlit Cloud (Recommended)** ✨ **[LIVE DEMO](https://rag-basic-qna-app.streamlit.app/)**

```bash
# 1. Push code to GitHub
git push origin main

# 2. Create secrets in Streamlit Cloud
```

In Streamlit Cloud dashboard, add these secrets in **Settings → Secrets**:
```toml
GEMINI_API_KEY = "your_gemini_key"
POSTGRES_DB = "postgres"
POSTGRES_USER = "postgres.xxxxxxxx"
POSTGRES_PASSWORD = "your_supabase_password"
POSTGRES_HOST = "db.xxxxx.supabase.co"
POSTGRES_PORT = "5432"
```

---

### **Option 2: Docker (Self-Hosted)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY qna_system.py .
EXPOSE 8501

CMD ["streamlit", "run", "qna_system.py"]
```

```bash
docker build -t qna-system .
docker run -p 8501:8501 --env-file .env qna-system
```

### **Option 3: Heroku**
```bash
heroku login
heroku create your-app-name
heroku config:set GEMINI_API_KEY="your_key"
heroku config:set POSTGRES_HOST="db.xxxxx.supabase.co"
heroku config:set POSTGRES_USER="postgres.xxxxxxxx"
heroku config:set POSTGRES_PASSWORD="your_password"
heroku config:set POSTGRES_DB="postgres"
heroku config:set POSTGRES_PORT="5432"
git push heroku main
```

### **Option 4: Railway / Render**
- Connect your GitHub repo
- Set Supabase environment variables in dashboard
- Auto-deploy on push

---

## 🔐 Security Considerations

- **Never commit `.env` file** — Add to `.gitignore`
- **Use environment variables** for all sensitive data
- **Restrict database access** — Use firewall rules
- **Rate limit API calls** — Add user authentication if public
- **Validate user input** — Sanitize before processing

---

## 📚 Dependencies

```
streamlit==1.28.1
google-generativeai==0.8.6
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Found a bug or have suggestions? Feel free to improve this project!

---

## 📄 License

This project is open source. Feel free to use and modify.

---

## 📞 Support

- **Google Gemini API Docs** — https://ai.google.dev/
- **Streamlit Docs** — https://docs.streamlit.io/
- **Supabase Docs** — https://supabase.com/docs
- **pgvector Docs** — https://github.com/pgvector/pgvector

---

## 🎯 Future Enhancements

- [ ] Multi-document support
- [ ] Chat history
- [ ] Custom system prompts
- [ ] Multiple embedding models
- [ ] Query performance analytics
- [ ] User authentication & rate limiting
- [ ] Support for PDF/DOC uploads
- [ ] Document categorization & tagging

---

**Made with ❤️ using Gemini API, PostgreSQL, and Streamlit**
