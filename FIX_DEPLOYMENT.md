# Fix Deployment - Rebuild Docker Image

The error shows the Docker container still has the old code. The container is trying to import from `langchain.chains` but the updated code uses `langchain_classic.chains`.

## Solution: Rebuild Docker Image Without Cache

### Step 1: Rebuild Docker Image (No Cache)

```bash
docker build --no-cache -t flask-app:latest .
```

This will:
- Ignore all cached layers
- Rebuild everything from scratch
- Include the updated `flipkart/rag_chain.py` with correct imports

### Step 2: Verify the Image Has Correct Code (Optional)

You can verify the image has the correct code by checking it:

```bash
# Create a temporary container to check
docker run --rm flask-app:latest head -5 /app/flipkart/rag_chain.py
```

You should see:
```
from langchain_groq import ChatGroq
# Langchain 1.0+ imports - handle different version structures
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
```

### Step 3: Delete Old Deployment and Redeploy

```bash
# Delete the old deployment
kubectl delete deployment flask-app

# Wait a moment
sleep 3

# Apply the deployment again
kubectl apply -f flask-deployment.yaml

# Wait for it to be ready
kubectl rollout status deployment/flask-app
```

### Step 4: Check Pod Status and Logs

```bash
# Check pod status
kubectl get pods -l app=flask

# Check logs
kubectl logs -f deployment/flask-app
```

## Quick Script

Or use the provided script:

```bash
./rebuild_no_cache.sh
```

This script will:
1. Remove old Docker image
2. Rebuild without cache
3. Delete and recreate the deployment
4. Show logs

## Why This Happened

The Docker image was built with the old code before you updated `flipkart/rag_chain.py`. Docker caches layers, so even after updating the file, if you didn't rebuild with `--no-cache`, it might use cached layers that contain the old code.

## Expected Result

After rebuilding, the logs should show the app starting successfully without the `ModuleNotFoundError`.

