# Flipkart Product Recommendation System

An AI-powered product recommendation system that provides personalized product suggestions to users, enhancing the shopping experience and boosting sales by helping users discover relevant items they are likely to purchase.

## 🎯 Overview

The Flipkart Product Recommendation System is an artificial intelligence (AI) powered mechanism that analyzes user behavior, product data, and reviews to deliver personalized product recommendations. The system utilizes advanced machine learning techniques, including Retrieval-Augmented Generation (RAG), to provide intelligent and context-aware suggestions.

## ✨ Features

- **Personalized Recommendations**: Tailored product suggestions based on user queries and preferences
- **Real-time Responses**: Fast, interactive recommendations powered by Groq's LLM
- **Vector-based Search**: Efficient semantic search using embeddings and vector databases
- **Conversational Interface**: Natural language interaction with chat history support
- **Product Review Analysis**: Leverages customer reviews and product data for better recommendations
- **Monitoring & Observability**: Built-in Prometheus metrics and Grafana dashboards
- **Scalable Architecture**: Containerized deployment with Kubernetes support

## 🏗️ How It Works

The system utilizes various machine learning techniques to analyze user data and predict preferences:

### Data Collection and Analysis
The system collects extensive user behavior data, including:
- Browsing history
- Past purchases
- Items in the shopping cart
- Product reviews and ratings

### Filtering Mechanisms
Flipkart primarily uses a hybrid approach combining two main types of filtering:

1. **Content-based Filtering**: Recommends products based on the features of items a user has shown interest in previously (e.g., if a user buys a formal shirt, the system might suggest formal trousers).

2. **Collaborative Filtering**: Recommends products based on the preferences and behaviors of similar users (e.g., if users with similar tastes to you liked a particular watch, that watch might be recommended to you).

### Real-time and Batch Recommendations
- The system can provide real-time updates to recommendations as a user adds or removes items from their cart
- Also generates recommendations in batches for improved performance

### Personalization
The system tailors suggestions to each individual user, offering a highly relevant and personalized shopping experience.

## 🛠️ Technology Stack

- **Framework**: Flask (Python web framework)
- **LLM**: Groq (Llama 3.1 8B Instant)
- **Embeddings**: HuggingFace (BAAI/bge-base-en-v1.5)
- **Vector Database**: DataStax Astra DB
- **ML/AI Libraries**: LangChain, LangGraph
- **Monitoring**: Prometheus, Grafana
- **Deployment**: Docker, Kubernetes

## 📋 Prerequisites

- Python 3.12+
- DataStax Astra DB account (free tier available)
- HuggingFace account and API token
- Groq API key (free tier available)
- Docker (for containerized deployment)
- Kubernetes (optional, for production deployment)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd FLIPKART-PRODUCT-RECOMMENDER-SYSTEM
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install the package in editable mode:

```bash
pip install -e .
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp env_template.txt .env
```

Edit `.env` and fill in your credentials:

```env
# DataStax Astra DB Configuration
ASTRA_DB_APPLICATION_TOKEN="AstraCS:your-token-here"
ASTRA_DB_KEYSPACE="default_keyspace"
ASTRA_DB_API_ENDPOINT="https://your-database-id.region.apps.astra.datastax.com"

# HuggingFace Token
HF_TOKEN="hf_your-token-here"

# Groq API Key
GROQ_API_KEY="gsk_your-api-key-here"
```

#### Getting Your Credentials:

- **Astra DB**: 
  1. Sign up at [https://astra.datastax.com/](https://astra.datastax.com/)
  2. Create a Vector database
  3. Get credentials from the "Connect" tab

- **HuggingFace**: 
  1. Sign up at [https://huggingface.co/](https://huggingface.co/)
  2. Create token at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

- **Groq**: 
  1. Sign up at [https://console.groq.com/](https://console.groq.com/)
  2. Create API key at [https://console.groq.com/keys](https://console.groq.com/keys)

## 📊 Data Ingestion

The system uses product review data stored in `data/flipkart_product_review.csv`. To ingest data into the vector database:

```python
from flipkart.data_ingestion import DataIngestor

ingestor = DataIngestor()
# Set load_existing=False to ingest new data
vector_store = ingestor.ingest(load_existing=False)
```

## 🎮 Usage

### Running the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Enter your product query in the chat interface
3. Get personalized product recommendations based on your query

### API Endpoints

#### GET `/`
- Returns the main web interface

#### POST `/get`
- **Request**: `{"msg": "your product query"}`
- **Response**: Product recommendation text

#### GET `/metrics`
- Returns Prometheus metrics for monitoring

### Example Queries

- "I'm looking for a good smartphone under 20000"
- "Show me wireless headphones with good bass"
- "What are the best laptops for gaming?"
- "Recommend me a formal shirt"

## 📁 Project Structure

```
FLIPKART-PRODUCT-RECOMMENDER-SYSTEM/
├── app.py                      # Flask application entry point
├── setup.py                    # Package setup configuration
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (create this)
├── data/
│   └── flipkart_product_review.csv  # Product review dataset
├── flipkart/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── data_converter.py      # Data preprocessing
│   ├── data_ingestion.py      # Vector store ingestion
│   └── rag_chain.py           # RAG chain builder
├── templates/
│   └── index.html             # Web interface template
├── static/
│   └── style.css              # Styling
├── utils/
│   ├── logger.py              # Logging utilities
│   └── custom_exception.py    # Custom exceptions
├── prometheus/                 # Prometheus configuration
├── grafana/                    # Grafana dashboards
├── Dockerfile                  # Docker configuration
└── flask-deployment.yaml       # Kubernetes deployment
```

## 🔧 Configuration

### Models

The system uses the following models (configurable in `flipkart/config.py`):

- **Embedding Model**: `BAAI/bge-base-en-v1.5` (HuggingFace)
- **RAG Model**: `llama-3.1-8b-instant` (Groq)

### Vector Store Settings

- **Collection Name**: `flipkart_database`
- **Search Results**: Top 3 most relevant products (k=3)
- **Keyspace**: `default_keyspace` (configurable)

## 📈 Monitoring

### Prometheus Metrics

The application exposes metrics at `/metrics` endpoint:

- `http_requests_total`: Total HTTP requests counter

### Accessing Metrics

```bash
# View metrics
curl http://localhost:5000/metrics
```

### Grafana Dashboard

For production deployments, Grafana dashboards are available in the `grafana/` directory. See `FULL DOCUMENTATION.md` for setup instructions.

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t flipkart-recommender:latest .
```

### Run Container

```bash
docker run -p 5000:5000 --env-file .env flipkart-recommender:latest
```

## ☸️ Kubernetes Deployment

See `FULL DOCUMENTATION.md` for detailed Kubernetes deployment instructions.

Quick start:

```bash
# Create secrets
kubectl create secret generic llmops-secrets \
  --from-literal=GROQ_API_KEY="your-key" \
  --from-literal=ASTRA_DB_APPLICATION_TOKEN="your-token" \
  --from-literal=ASTRA_DB_KEYSPACE="default_keyspace" \
  --from-literal=ASTRA_DB_API_ENDPOINT="your-endpoint" \
  --from-literal=HF_TOKEN="your-token"

# Deploy application
kubectl apply -f flask-deployment.yaml

# Port forward
kubectl port-forward svc/flask-service 5000:80
```

## 🧪 Testing

Test the configuration:

```python
from flipkart.config import Config

print("ASTRA_DB_API_ENDPOINT:", Config.ASTRA_DB_API_ENDPOINT)
print("ASTRA_DB_KEYSPACE:", Config.ASTRA_DB_KEYSPACE)
print("Models configured:", Config.EMBEDDING_MODEL, Config.RAG_MODEL)
```

## 🎯 Benefits

### Improved User Experience
It helps users easily find products they need or might like, reducing the difficulty of searching through millions of items.

### Increased Sales and Engagement
By suggesting relevant items, the system increases the likelihood of additional purchases, thereby boosting sales and customer engagement.

### Enhanced Product Discovery
The system aids in the discovery of new or complementary products, expanding the user's exposure to the extensive catalog.

## 🔍 Troubleshooting

### Common Issues

1. **Connection Errors to Astra DB**
   - Verify your `ASTRA_DB_API_ENDPOINT` and `ASTRA_DB_APPLICATION_TOKEN`
   - Ensure the database is fully provisioned
   - Check network connectivity

2. **HuggingFace Model Access**
   - Verify your `HF_TOKEN` is valid
   - Some models may require accepting terms of use on HuggingFace

3. **Groq API Errors**
   - Check your `GROQ_API_KEY` is correct
   - Verify you haven't exceeded rate limits

4. **Vector Store Issues**
   - Ensure data has been ingested: `ingestor.ingest(load_existing=False)`
   - Check the collection name matches in `data_ingestion.py`

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [DataStax Astra DB Docs](https://docs.datastax.com/en/astra/)
- [Groq API Documentation](https://console.groq.com/docs)
- [HuggingFace Documentation](https://huggingface.co/docs)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

[Add your license information here]

## 👥 Authors

- **Sudhanshu** - Initial work

## 🙏 Acknowledgments

- Flipkart for the product recommendation concept
- LangChain community for excellent tooling
- DataStax for Astra DB
- Groq for fast LLM inference
- HuggingFace for embeddings and models

---

**Note**: This is an educational project demonstrating the implementation of a product recommendation system using modern AI/ML techniques. For production use, additional considerations around scalability, security, and performance optimization should be addressed.

