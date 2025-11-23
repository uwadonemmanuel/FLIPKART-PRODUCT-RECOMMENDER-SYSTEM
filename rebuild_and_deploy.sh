#!/bin/bash

# Script to rebuild Docker image and redeploy to Kubernetes

echo "🔨 Rebuilding Docker image (no cache)..."
docker build --no-cache -t flask2-app:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully"

echo ""
echo "🔄 Updating Kubernetes deployment..."
kubectl rollout restart deployment/flask2-app

echo ""
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/flask2-app

echo ""
echo "📊 Checking pod status..."
kubectl get pods -l app=flask

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To view logs: kubectl logs -f deployment/flask2-app"
echo "To port-forward: kubectl port-forward svc/flask-service 5000:80"

