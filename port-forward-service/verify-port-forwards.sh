#!/bin/bash

# Verification script for port-forward services
# Run this on your VM to diagnose connection issues

echo "=== Port-Forward Verification Script ==="
echo ""

# Check if services are running
echo "1. Checking service status..."
systemctl --user is-active prometheus-port-forward.service && echo "  ✓ Prometheus service: ACTIVE" || echo "  ✗ Prometheus service: INACTIVE"
systemctl --user is-active grafana-port-forward.service && echo "  ✓ Grafana service: ACTIVE" || echo "  ✗ Grafana service: INACTIVE"
systemctl --user is-active flask-port-forward.service && echo "  ✓ Flask service: ACTIVE" || echo "  ✗ Flask service: INACTIVE"
echo ""

# Check if ports are listening
echo "2. Checking if ports are listening..."
if command -v ss &> /dev/null; then
    LISTENING=$(ss -tlnp 2>/dev/null | grep -E "9090|3000|5000")
    if [ -n "$LISTENING" ]; then
        echo "  Listening ports found:"
        echo "$LISTENING" | sed 's/^/  /'
    else
        echo "  ✗ No processes listening on ports 9090, 3000, or 5000"
    fi
elif command -v netstat &> /dev/null; then
    LISTENING=$(netstat -tlnp 2>/dev/null | grep -E "9090|3000|5000")
    if [ -n "$LISTENING" ]; then
        echo "  Listening ports found:"
        echo "$LISTENING" | sed 's/^/  /'
    else
        echo "  ✗ No processes listening on ports 9090, 3000, or 5000"
    fi
else
    echo "  ⚠ Cannot check (ss and netstat not available)"
fi
echo ""

# Check kubectl port-forward processes
echo "3. Checking kubectl port-forward processes..."
KUBECTL_PROCESSES=$(ps aux | grep "kubectl port-forward" | grep -v grep)
if [ -n "$KUBECTL_PROCESSES" ]; then
    echo "  Active kubectl port-forward processes:"
    echo "$KUBECTL_PROCESSES" | sed 's/^/  /'
else
    echo "  ✗ No kubectl port-forward processes found"
fi
echo ""

# Test local connectivity
echo "4. Testing local connectivity..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9090 --max-time 5 | grep -q "200\|302\|301"; then
    echo "  ✓ Prometheus (localhost:9090): ACCESSIBLE"
else
    echo "  ✗ Prometheus (localhost:9090): NOT ACCESSIBLE"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 --max-time 5 | grep -q "200\|302\|301"; then
    echo "  ✓ Grafana (localhost:3000): ACCESSIBLE"
else
    echo "  ✗ Grafana (localhost:3000): NOT ACCESSIBLE"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 --max-time 5 | grep -q "200\|302\|301"; then
    echo "  ✓ Flask (localhost:5000): ACCESSIBLE"
else
    echo "  ✗ Flask (localhost:5000): NOT ACCESSIBLE"
fi
echo ""

# Check service logs for errors
echo "5. Recent service logs (last 5 lines)..."
echo "  Prometheus service:"
journalctl --user -u prometheus-port-forward.service -n 5 --no-pager 2>/dev/null | tail -3 | sed 's/^/    /' || echo "    No logs available"
echo ""
echo "  Grafana service:"
journalctl --user -u grafana-port-forward.service -n 5 --no-pager 2>/dev/null | tail -3 | sed 's/^/    /' || echo "    No logs available"
echo ""
echo "  Flask service:"
journalctl --user -u flask-port-forward.service -n 5 --no-pager 2>/dev/null | tail -3 | sed 's/^/    /' || echo "    No logs available"
echo ""

# Check if listening on 0.0.0.0 or 127.0.0.1
echo "6. Checking bind address..."
if command -v ss &> /dev/null; then
    BIND_9090=$(ss -tlnp 2>/dev/null | grep ":9090" | head -1)
    BIND_3000=$(ss -tlnp 2>/dev/null | grep ":3000" | head -1)
    BIND_5000=$(ss -tlnp 2>/dev/null | grep ":5000" | head -1)
    
    if echo "$BIND_9090" | grep -q "0.0.0.0:9090"; then
        echo "  ✓ Port 9090: Listening on 0.0.0.0 (accessible from external IP)"
    elif echo "$BIND_9090" | grep -q "127.0.0.1:9090"; then
        echo "  ✗ Port 9090: Only listening on 127.0.0.1 (NOT accessible from external IP)"
    else
        echo "  ⚠ Port 9090: Status unknown"
    fi
    
    if echo "$BIND_3000" | grep -q "0.0.0.0:3000"; then
        echo "  ✓ Port 3000: Listening on 0.0.0.0 (accessible from external IP)"
    elif echo "$BIND_3000" | grep -q "127.0.0.1:3000"; then
        echo "  ✗ Port 3000: Only listening on 127.0.0.1 (NOT accessible from external IP)"
    else
        echo "  ⚠ Port 3000: Status unknown"
    fi
    
    if echo "$BIND_5000" | grep -q "0.0.0.0:5000"; then
        echo "  ✓ Port 5000: Listening on 0.0.0.0 (accessible from external IP)"
    elif echo "$BIND_5000" | grep -q "127.0.0.1:5000"; then
        echo "  ✗ Port 5000: Only listening on 127.0.0.1 (NOT accessible from external IP)"
    else
        echo "  ⚠ Port 5000: Status unknown"
    fi
fi
echo ""

# Get external IP
echo "7. Network information..."
EXTERNAL_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "Unable to determine")
echo "  External IP: $EXTERNAL_IP"
echo ""

# Check firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    echo "8. UFW Firewall status..."
    ufw status | head -5 | sed 's/^/  /'
    echo ""
fi

echo "=== Verification Complete ==="
echo ""
echo "If ports are only listening on 127.0.0.1, the --address 0.0.0.0 flag may not be working."
echo "If ports are not listening at all, check service logs for errors."
echo "If localhost works but external IP doesn't, check firewall rules."
