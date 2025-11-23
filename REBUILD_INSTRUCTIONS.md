# Rebuild Docker Image - Step by Step

The Docker image still has the old code. Follow these steps to rebuild:

## Step 1: Verify Local Code is Correct

```bash
# Check the import statement
head -5 flipkart/rag_chain.py
```

You should see:
```
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
```

NOT:
```
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
```

## Step 2: Remove Old Docker Image

```bash
docker rmi flask-app:latest
```

## Step 3: Rebuild WITHOUT Cache

```bash
docker build --no-cache -t flask-app:latest .
```

**IMPORTANT**: The `--no-cache` flag is CRITICAL. Without it, Docker will reuse cached layers with the old code.

## Step 4: Verify the Image Has Correct Code

```bash
# Check what's in the image
docker run --rm flask-app:latest head -5 /app/flipkart/rag_chain.py
```

You should see `langchain_classic.chains`, NOT `langchain.chains`.

## Step 5: Delete and Redeploy

```bash
# Delete old deployment
kubectl delete deployment flask-app

# Wait a moment
sleep 5

# Apply deployment
kubectl apply -f flask-deployment.yaml

# Wait for rollout
kubectl rollout status deployment/flask-app
```

## Step 6: Check Logs

```bash
kubectl logs -f deployment/flask-app
```

## Quick One-Liner

```bash
docker rmi flask-app:latest && docker build --no-cache -t flask-app:latest . && kubectl delete deployment flask-app && sleep 5 && kubectl apply -f flask-deployment.yaml && kubectl rollout status deployment/flask-app
```

## Why This Happens

Docker caches layers. When you do `COPY . .`, Docker caches that layer. Even if you update the file locally, Docker might reuse the cached layer unless you use `--no-cache`.

