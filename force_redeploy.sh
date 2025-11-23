#!/bin/bash

# Force Kubernetes to use the new Docker image

echo "🔄 Forcing Kubernetes to use new image..."

# Check if using minikube
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "📦 Detected minikube - loading image into minikube..."
    minikube image load flask2-app:latest
else
    echo "ℹ️  Not using minikube, using local Docker"
fi

echo ""
echo "🗑️  Deleting all existing pods to force recreation..."
kubectl delete pods -l app=flask --force --grace-period=0

echo ""
echo "🔄 Restarting deployment..."
kubectl rollout restart deployment/flask2-app

echo ""
echo "⏳ Waiting for new pods..."
sleep 5

echo ""
echo "📊 Pod status:"
kubectl get pods -l app=flask

echo ""
echo "📋 Checking logs (waiting 10 seconds for pod to start)..."
sleep 10
POD_NAME=$(kubectl get pods -l app=flask -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ ! -z "$POD_NAME" ]; then
    kubectl logs $POD_NAME --tail=30
else
    echo "No pod found yet"
fi

