#!/bin/bash

# Get actual error messages from port-forward services

echo "=== Prometheus Port-Forward Errors ==="
journalctl --user -u prometheus-port-forward.service --since "5 minutes ago" --no-pager | grep -i "error\|fail\|unable\|cannot" | tail -10
echo ""

echo "=== Full Prometheus Log (last 10 lines) ==="
journalctl --user -u prometheus-port-forward.service -n 10 --no-pager
echo ""

echo "=== Grafana Port-Forward Errors ==="
journalctl --user -u grafana-port-forward.service --since "5 minutes ago" --no-pager | grep -i "error\|fail\|unable\|cannot" | tail -10
echo ""

echo "=== Full Grafana Log (last 10 lines) ==="
journalctl --user -u grafana-port-forward.service -n 10 --no-pager
echo ""

echo "=== Flask Port-Forward Errors ==="
journalctl --user -u flask-port-forward.service --since "5 minutes ago" --no-pager | grep -i "error\|fail\|unable\|cannot" | tail -10
echo ""

echo "=== Full Flask Log (last 10 lines) ==="
journalctl --user -u flask-port-forward.service -n 10 --no-pager
echo ""

echo "=== Testing kubectl connectivity ==="
kubectl get svc prometheus-service -n monitoring 2>&1
echo ""
kubectl get svc grafana-service -n monitoring 2>&1
echo ""
kubectl get svc flask-service 2>&1
echo ""

echo "=== Testing manual port-forward (5 seconds) ==="
echo "Testing Prometheus..."
timeout 5 kubectl port-forward --address 0.0.0.0 svc/prometheus-service -n monitoring 9090:9090 2>&1 &
PF_PID=$!
sleep 3
kill $PF_PID 2>/dev/null
wait $PF_PID 2>/dev/null
echo ""

echo "Testing Grafana..."
timeout 5 kubectl port-forward --address 0.0.0.0 svc/grafana-service -n monitoring 3000:3000 2>&1 &
PF_PID=$!
sleep 3
kill $PF_PID 2>/dev/null
wait $PF_PID 2>/dev/null
echo ""

echo "Testing Flask..."
timeout 5 kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0 2>&1 &
PF_PID=$!
sleep 3
kill $PF_PID 2>/dev/null
wait $PF_PID 2>/dev/null
