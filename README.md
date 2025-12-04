# RAG Q&A Support Bot

A Question & Answer support bot built using Retrieval Augmented Generation (RAG) that crawls websites, generates embeddings, stores them in a vector database, and provides accurate answers based only on the crawled content.

## 🚀 Features

- **Web Crawling**: Automatically crawls websites and extracts clean text content
- **Text Processing**: Intelligent chunking and preprocessing of text for optimal embeddings
- **Embeddings Generation**: Local sentence-transformers (FREE) or OpenAI embeddings
- **Vector Storage**: Simple vector database with NumPy for efficient similarity search
- **RAG Pipeline**: Retrieval-augmented generation for accurate, context-aware answers
- **FREE Local LLM**: Uses Ollama (completely free, no API key needed!)
- **REST API**: FastAPI-based API for easy integration
- **Source Attribution**: Always cites sources for transparency

## 📋 Prerequisites

- Python 3.8 or higher
- Ollama (free, local LLM) - **Recommended**
  - Download from: https://ollama.ai/download
- OR OpenAI API key (optional, paid alternative)
- Internet connection for web crawling

## 🛠️ Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment (recommended)**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

   ```powershell
   pip install -r requirements.txt
   ```

4. **Install Ollama (FREE option - Recommended)**

   - Download from: https://ollama.ai/download
   - Install and run:

   ```powershell
   ollama pull llama3.2
   ```

5. **Set up environment variables**

   Copy the `.env.example` file to `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```

   The default configuration uses FREE Ollama (no API key needed!):

   ```
   USE_OLLAMA=true
   OLLAMA_MODEL=llama3.2
   ```

   **Optional**: To use OpenAI instead, edit `.env`:

   ```
   USE_OLLAMA=false
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## 📖 Usage

### Quick Start with Sample Data (Recommended for Testing)

To quickly test the system without crawling:

```powershell
python test_simple.py
```

This adds 5 sample Python documentation snippets to your database (~30 seconds).

### Step 1: Crawl and Index a Website (Optional)

Run the crawling script to index a website:

```powershell
python crawl_and_index.py https://example.com
```

This will:

1. Crawl the website (respecting max depth and page limits)
2. Clean and chunk the text
3. Generate embeddings for each chunk
4. Store everything in the vector database

**Example with a documentation site:**

```powershell
python crawl_and_index.py https://docs.python.org/3/
```

**Note**: Crawling can take several minutes. Use `test_simple.py` for quick testing!

### Step 2: Start the API Server

```powershell
python main.py
```

The API server will start at `http://localhost:8000`

### Step 3: Test the Bot

**Using the test script:**

```powershell
python test_bot.py "How do I install Python?"
```

**Using curl:**

```powershell
curl -X POST "http://localhost:8000/api/ask" `
  -H "Content-Type: application/json" `
  -d '{"question": "How do I get started?"}'
```

**Using PowerShell:**

```powershell
$body = @{
    question = "What are the main features?"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/ask" -Body $body -ContentType "application/json"
```

## 🔌 API Endpoints

### Health Check

```
GET /health
```

Returns the health status and document count.

**Response:**

```json
{
  "status": "healthy",
  "vector_db_count": 150
}
```

### Ask a Question

```
POST /api/ask
```

**Request Body:**

```json
{
  "question": "How do I reset my password?",
  "top_k": 3
}
```

**Response:**

```json
{
  "answer": "To reset your password, follow these steps...",
  "sources": [
    {
      "title": "Password Reset Guide",
      "url": "https://example.com/help/password",
      "snippet": "Step 1: Navigate to the login page..."
    }
  ]
}
```

### Statistics

```
GET /api/stats
```

Returns statistics about the vector database.

## 📁 Project Structure

```
.
├── crawler.py              # Web crawling functionality
├── text_processor.py       # Text cleaning and chunking
├── embeddings.py          # Embedding generation
├── vector_db.py           # Vector database operations
├── rag_pipeline.py        # RAG orchestration
├── main.py               # FastAPI application
├── config.py             # Configuration management
├── crawl_and_index.py    # Script to crawl and index websites
├── test_bot.py           # Testing script
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore patterns
└── README.md            # This file
```

## ⚙️ Configuration

Edit `.env` to configure the bot:

| Variable          | Description             | Default                  |
| ----------------- | ----------------------- | ------------------------ |
| `OPENAI_API_KEY`  | Your OpenAI API key     | (required)               |
| `CHROMA_DB_PATH`  | Path to vector database | `./data/chroma_db`       |
| `MAX_CRAWL_DEPTH` | Maximum crawl depth     | `3`                      |
| `MAX_PAGES`       | Maximum pages to crawl  | `50`                     |
| `CHUNK_SIZE`      | Text chunk size         | `1000`                   |
| `CHUNK_OVERLAP`   | Overlap between chunks  | `200`                    |
| `EMBEDDING_MODEL` | OpenAI embedding model  | `text-embedding-ada-002` |
| `LLM_MODEL`       | LLM for generation      | `gpt-3.5-turbo`          |
| `MAX_TOKENS`      | Max tokens in response  | `500`                    |
| `TEMPERATURE`     | Generation temperature  | `0.7`                    |

## 🧪 Testing

### Manual Testing with Postman

1. Import the following collection or create requests:

   - GET `http://localhost:8000/health`
   - POST `http://localhost:8000/api/ask`
   - GET `http://localhost:8000/api/stats`

2. For POST requests, use this body:
   ```json
   {
     "question": "Your question here",
     "top_k": 3
   }
   ```

### Automated Testing

Run the test script:

```powershell
python test_bot.py
```

Or with a custom question:

```powershell
python test_bot.py "What is Python?"
```

## 🔍 How It Works

1. **Crawling**: The `WebCrawler` class recursively crawls web pages, respecting domain boundaries and depth limits.

2. **Text Processing**: Raw HTML is cleaned and split into chunks using `RecursiveCharacterTextSplitter` for optimal embedding size.

3. **Embeddings**: Each chunk is converted to a vector embedding using OpenAI's embedding API.

4. **Vector Storage**: Embeddings are stored in ChromaDB with metadata (URL, title, etc.) for retrieval.

5. **Retrieval**: When a question is asked, it's converted to an embedding and similar chunks are retrieved via cosine similarity.

6. **Generation**: Retrieved chunks are used as context for the LLM to generate an accurate, source-based answer.

## 🚧 Troubleshooting

### "No module named 'openai'"

```powershell
pip install -r requirements.txt
```

### "RAG pipeline not initialized"

Check that your `.env` file exists and contains a valid `OPENAI_API_KEY`.

### "No data was crawled"

- Verify the URL is accessible
- Check if the website blocks crawlers (robots.txt)
- Try increasing `MAX_PAGES` in `.env`

### Port 8000 already in use

Change the port in `.env`:

```
API_PORT=8080
```

## 📝 Best Practices

1. **Website Selection**: Choose websites with well-structured content and clear text
2. **Chunk Size**: Adjust based on your content (larger for technical docs, smaller for FAQs)
3. **Top K Results**: Use 3-5 for balanced context without overwhelming the LLM
4. **Rate Limiting**: Add delays in crawler to respect website resources
5. **Monitoring**: Check vector database count regularly to ensure proper indexing

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the bot!

## 📄 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

- OpenAI for embeddings and LLM APIs
- ChromaDB for vector storage
- FastAPI for the web framework
- BeautifulSoup for web scraping

## 📮 Support

For issues or questions:

1. Check the troubleshooting section
2. Review the code comments
3. Test each component independently

---

**Built with ❤️ using Retrieval Augmented Generation**
