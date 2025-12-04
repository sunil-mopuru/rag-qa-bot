# Quick Start Guide - RAG Q&A Support Bot

## ✅ Setup Complete!

Your RAG Q&A Support Bot project is ready to use. Here's how to get started:

## 📝 Prerequisites Met

- ✓ Python 3.14.1 installed
- ✓ Virtual environment (`venv`) created
- ✓ All dependencies installed
- ✓ Configuration files ready

## 🚀 Next Steps

### 1. Configure Your OpenAI API Key

Edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Crawl and Index a Website

Run the crawling script to index content from a website:

```powershell
python crawl_and_index.py https://docs.python.org/3/tutorial/
```

**Note**: Start with a small documentation site to test. The crawler respects the `MAX_PAGES` setting in your `.env` file (default: 50 pages).

### 3. Start the API Server

```powershell
python main.py
```

The API will be available at `http://localhost:8000`

### 4. Test Your Bot

#### Using the test script:

```powershell
python test_bot.py "What is Python?"
```

#### Using PowerShell to make API requests:

```powershell
$body = @{
    question = "How do I install Python?"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/ask" -Body $body -ContentType "application/json"
```

#### Using curl:

```powershell
curl -X POST "http://localhost:8000/api/ask" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"What is Python?\"}'
```

## 📚 API Documentation

Once the server is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🏗️ Project Structure

```
D:\AirTribe\AI\
├── config.py              # Configuration settings
├── crawler.py             # Web crawler module
├── text_processor.py      # Text chunking and processing
├── embeddings.py          # Embeddings generation
├── vector_db.py           # Vector database interface
├── simple_vector_db.py    # Fallback vector database
├── rag_pipeline.py        # RAG pipeline implementation
├── main.py                # FastAPI application
├── crawl_and_index.py     # Indexing script
├── test_bot.py            # Testing utility
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md              # Full documentation
```

## 🔧 Troubleshooting

### If the server doesn't start:

1. Ensure your virtual environment is activated: `.\venv\Scripts\Activate.ps1`
2. Check that all dependencies are installed: `pip list`
3. Verify your `.env` file has the correct API key

### If crawling fails:

1. Check your internet connection
2. Ensure the URL is accessible
3. Try a smaller website first (e.g., a single documentation page)

### If embeddings fail:

1. Verify your OpenAI API key is valid
2. Check your OpenAI account has credits
3. The system automatically falls back to sentence-transformers if OpenAI fails

## 🎯 Example Workflow

```powershell
# 1. Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# 2. Crawl Python documentation
python crawl_and_index.py https://docs.python.org/3/tutorial/

# 3. Start API server (in a new terminal)
python main.py

# 4. Test the bot (in another terminal)
python test_bot.py "How do I use Python lists?"
```

## 📖 Additional Resources

- Full documentation: See `README.md`
- API docs: http://localhost:8000/docs (when server is running)
- Configuration: Edit `config.py` or `.env`

## 🎉 You're All Set!

Your RAG Q&A Support Bot is ready to use. Start by crawling a website and asking questions!
