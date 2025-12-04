#!/bin/bash

# Check detailed error logs for port-forward services

echo "=== Detailed Error Analysis ==="
echo ""

echo "1. Full Prometheus service logs (last 20 lines):"
echo "----------------------------------------"
journalctl --user -u prometheus-port-forward.service -n 20 --no-pager 2>/dev/null
echo ""

echo "2. Full Grafana service logs (last 20 lines):"
echo "----------------------------------------"
journalctl --user -u grafana-port-forward.service -n 20 --no-pager 2>/dev/null
echo ""

echo "3. Full Flask service logs (last 20 lines):"
echo "----------------------------------------"
journalctl --user -u flask-port-forward.service -n 20 --no-pager 2>/dev/null
echo ""

echo "4. Testing kubectl connectivity:"
echo "----------------------------------------"
kubectl cluster-info 2>&1 | head -3
echo ""

echo "5. Checking if services exist:"
echo "----------------------------------------"
kubectl get svc prometheus-service -n monitoring 2>&1
echo ""
kubectl get svc grafana-service -n monitoring 2>&1
echo ""
kubectl get svc flask-service 2>&1
echo ""

echo "6. Testing manual port-forward (will timeout after 5 seconds):"
echo "----------------------------------------"
echo "Testing Prometheus port-forward manually..."
timeout 5 kubectl port-forward --address 0.0.0.0 svc/prometheus-service -n monitoring 9090:9090 2>&1 || echo "Manual test completed or failed"
echo ""
echo "Testing Grafana port-forward manually..."
timeout 5 kubectl port-forward --address 0.0.0.0 svc/grafana-service -n monitoring 3000:3000 2>&1 || echo "Manual test completed or failed"
echo ""
echo "Testing Flask port-forward manually..."
timeout 5 kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0 2>&1 || echo "Manual test completed or failed"
echo ""

echo "7. Checking kubectl context:"
echo "----------------------------------------"
kubectl config current-context 2>&1
echo ""

echo "8. Checking if pods are running:"
echo "----------------------------------------"
kubectl get pods -n monitoring 2>&1 | head -5
echo ""
kubectl get pods 2>&1 | head -5
echo ""
