#!/bin/bash

# Script to rebuild Docker image WITHOUT cache and redeploy to Kubernetes

echo "🧹 Cleaning up old Docker images..."
docker rmi flask-app:latest 2>/dev/null || echo "No existing image to remove"

echo ""
echo "🔨 Rebuilding Docker image (NO CACHE)..."
docker build --no-cache -t flask-app:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully"

echo ""
echo "🔄 Deleting old deployment to force recreation..."
kubectl delete deployment flask-app 2>/dev/null || echo "Deployment already deleted or doesn't exist"

echo ""
echo "⏳ Waiting a moment..."
sleep 3

echo ""
echo "🚀 Applying deployment..."
kubectl apply -f flask-deployment.yaml

echo ""
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/flask-app --timeout=5m

echo ""
echo "📊 Checking pod status..."
kubectl get pods -l app=flask

echo ""
echo "📋 Recent pod logs:"
POD_NAME=$(kubectl get pods -l app=flask -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ ! -z "$POD_NAME" ]; then
    kubectl logs $POD_NAME --tail=20
else
    echo "No pod found yet"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To view logs: kubectl logs -f deployment/flask-app"
echo "To port-forward: kubectl port-forward svc/flask-service 5000:80"

