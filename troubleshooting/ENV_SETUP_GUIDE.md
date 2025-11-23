# Environment Variables Setup Guide

This guide explains how to obtain and configure all required environment variables for the Flipkart Product Recommender System.

## Required Environment Variables

1. **ASTRA_DB_APPLICATION_TOKEN** - DataStax Astra DB authentication token
2. **ASTRA_DB_API_ENDPOINT** - DataStax Astra DB API endpoint URL
3. **ASTRA_DB_KEYSPACE** - Database keyspace name (default: "default_keyspace")
4. **HF_TOKEN** - HuggingFace API token for accessing models
5. **GROQ_API_KEY** - Groq API key for LLM inference

---

## Step-by-Step Setup

### 1. DataStax Astra DB Setup

#### Create an Astra DB Account
1. Go to [https://astra.datastax.com/](https://astra.datastax.com/)
2. Sign up for a free account (or log in if you already have one)
3. Complete the registration process

#### Create a Database
1. Click **"Create Database"** or **"Add Database"**
2. Choose a database name (e.g., "flipkart-recommender")
3. Select a provider and region (choose the closest to you)
4. Select the **"Vector"** database type (for vector search capabilities)
5. Click **"Create Database"**
6. Wait for the database to be created (usually 2-3 minutes)

#### Get Your Credentials
1. Once the database is created, click on it to open the dashboard
2. Go to the **"Connect"** tab
3. You'll see:
   - **Application Token**: Click **"Generate Token"** → Select **"Database Administrator"** role → Copy the token (starts with `AstraCS:`)
   - **API Endpoint**: Copy the URL (looks like `https://xxxxx-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx.xx-xxxx-x.apps.astra.datastax.com`)
   - **Keyspace**: Usually `default_keyspace` (or the one you created)

#### Add to .env file:
```bash
ASTRA_DB_APPLICATION_TOKEN="AstraCS:your-token-here"
ASTRA_DB_API_ENDPOINT="https://your-database-id.region.apps.astra.datastax.com"
ASTRA_DB_KEYSPACE="default_keyspace"
```

---

### 2. HuggingFace Token Setup

#### Create a HuggingFace Account
1. Go to [https://huggingface.co/](https://huggingface.co/)
2. Sign up for a free account (or log in)

#### Generate an Access Token
1. Click on your profile picture (top right) → **Settings**
2. Go to **"Access Tokens"** in the left sidebar
3. Click **"New token"**
4. Give it a name (e.g., "flipkart-recommender")
5. Select **"Read"** permission (sufficient for downloading models)
6. Click **"Generate token"**
7. **Copy the token immediately** (starts with `hf_`)

#### Add to .env file:
```bash
HF_TOKEN="hf_your-token-here"
```

---

### 3. Groq API Key Setup

#### Create a Groq Account
1. Go to [https://console.groq.com/](https://console.groq.com/)
2. Sign up for a free account (or log in)
3. Groq offers free tier with generous limits

#### Generate an API Key
1. Once logged in, go to **"API Keys"** in the dashboard
2. Click **"Create API Key"**
3. Give it a name (e.g., "flipkart-recommender")
4. Click **"Submit"**
5. **Copy the API key immediately** (starts with `gsk_`)

#### Add to .env file:
```bash
GROQ_API_KEY="gsk_your-api-key-here"
```

---

## Creating Your .env File

### Option 1: Copy from Example (Recommended)
```bash
cp .env.example .env
```

Then edit `.env` and fill in your actual values:
```bash
nano .env
# or
vim .env
# or use any text editor
```

### Option 2: Create Manually
Create a file named `.env` in the project root directory:

```bash
touch .env
```

Add the following content (replace with your actual values):
```bash
# DataStax Astra DB Configuration
ASTRA_DB_APPLICATION_TOKEN="AstraCS:your-token-here"
ASTRA_DB_KEYSPACE="default_keyspace"
ASTRA_DB_API_ENDPOINT="https://your-database-id.region.apps.astra.datastax.com"

# HuggingFace Token
HF_TOKEN="hf_your-token-here"

# Groq API Key
GROQ_API_KEY="gsk_your-api-key-here"
```

---

## Verify Your Setup

### Test the Configuration
1. Make sure your `.env` file is in the project root directory
2. The `python-dotenv` package (already in requirements) will automatically load it
3. Run a test script:

```python
from flipkart.config import Config

print("ASTRA_DB_API_ENDPOINT:", Config.ASTRA_DB_API_ENDPOINT)
print("ASTRA_DB_APPLICATION_TOKEN:", Config.ASTRA_DB_APPLICATION_TOKEN[:20] + "..." if Config.ASTRA_DB_APPLICATION_TOKEN else "Not set")
print("ASTRA_DB_KEYSPACE:", Config.ASTRA_DB_KEYSPACE)
print("GROQ_API_KEY:", Config.GROQ_API_KEY[:10] + "..." if Config.GROQ_API_KEY else "Not set")
print("HF_TOKEN:", Config.HF_TOKEN[:10] + "..." if Config.HF_TOKEN else "Not set")
```

---

## Security Best Practices

### ⚠️ Important Security Notes:

1. **Never commit `.env` to Git**
   - The `.env` file should already be in `.gitignore`
   - Only commit `.env.example` (without real values)

2. **Keep tokens secure**
   - Don't share tokens in chat, email, or public forums
   - Rotate tokens if they're accidentally exposed
   - Use different tokens for development and production

3. **Token Permissions**
   - Use the minimum required permissions
   - For HuggingFace: "Read" is usually sufficient
   - For Astra DB: "Database Administrator" for full access, or create custom roles

4. **Environment-specific values**
   - Use different tokens/endpoints for development, staging, and production
   - Consider using environment variable management tools for production

---

## Troubleshooting

### Issue: "ASTRA_DB_API_ENDPOINT is not set"
- **Solution**: Make sure your `.env` file is in the project root
- Check that variable names match exactly (case-sensitive)
- Verify the file is named `.env` (not `.env.txt` or `env`)

### Issue: "Invalid token" or "Authentication failed"
- **Solution**: 
  - Verify you copied the entire token (they're long!)
  - Check for extra spaces or quotes
  - Regenerate the token if needed

### Issue: "Database not found" or "Keyspace not found"
- **Solution**:
  - Verify the API endpoint URL is correct
  - Check that the database is fully created (not still provisioning)
  - Ensure the keyspace name matches what's in Astra DB

### Issue: "Model not found" (HuggingFace)
- **Solution**:
  - Verify your HF_TOKEN is valid
  - Check that the token has "Read" permissions
  - Some models may require accepting terms of use on HuggingFace

---

## Quick Reference

| Variable | Where to Get | Format | Example |
|----------|-------------|--------|---------|
| `ASTRA_DB_APPLICATION_TOKEN` | [astra.datastax.com](https://astra.datastax.com/) → Database → Connect | `AstraCS:...` | `AstraCS:abc123...` |
| `ASTRA_DB_API_ENDPOINT` | [astra.datastax.com](https://astra.datastax.com/) → Database → Connect | `https://...apps.astra.datastax.com` | `https://12345-67890...us-east1.apps.astra.datastax.com` |
| `ASTRA_DB_KEYSPACE` | [astra.datastax.com](https://astra.datastax.com/) → Database → Connect | String | `default_keyspace` |
| `HF_TOKEN` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | `hf_...` | `hf_abc123...` |
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) | `gsk_...` | `gsk_abc123...` |

---

## Next Steps

Once you've set up all environment variables:

1. **Test the connection**:
   ```bash
   python -c "from flipkart.config import Config; print('Config loaded successfully!')"
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Verify data ingestion** (if needed):
   ```python
   from flipkart.data_ingestion import DataIngestor
   ingestor = DataIngestor()
   ingestor.ingest(load_existing=False)  # Set to False to ingest data
   ```

---

## Need Help?

- **Astra DB Docs**: [https://docs.datastax.com/en/astra/](https://docs.datastax.com/en/astra/)
- **HuggingFace Docs**: [https://huggingface.co/docs](https://huggingface.co/docs)
- **Groq Docs**: [https://console.groq.com/docs](https://console.groq.com/docs)

