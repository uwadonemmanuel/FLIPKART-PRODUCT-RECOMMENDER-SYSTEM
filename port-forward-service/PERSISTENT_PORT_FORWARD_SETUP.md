# Persistent Port-Forward Setup Guide

This guide explains how to keep `kubectl port-forward` processes running even after SSH sessions are closed.

## 🎯 Problem

When you run `kubectl port-forward` in an SSH session and disconnect, the port-forward processes are terminated, making your services inaccessible.

## ✅ Solutions

### Option 1: Using the Service Script (Quick & Simple)

This is the easiest solution using a bash script with `nohup`.

#### Setup

1. **Copy the script to your VM**:
   ```bash
   # On your local machine, copy the script to your VM
   scp port-forward-service.sh username@your-vm-ip:~/
   ```

2. **On your VM, make it executable**:
   ```bash
   chmod +x ~/port-forward-service.sh
   ```

3. **Start all port-forwards**:
   ```bash
   ~/port-forward-service.sh start
   ```

4. **Verify they're running**:
   ```bash
   ~/port-forward-service.sh status
   ```

#### Usage

```bash
# Start all services
~/port-forward-service.sh start

# Stop all services
~/port-forward-service.sh stop

# Restart all services
~/port-forward-service.sh restart

# Check status
~/port-forward-service.sh status

# Start/stop individually
~/port-forward-service.sh start-prometheus
~/port-forward-service.sh stop-prometheus
~/port-forward-service.sh start-grafana
~/port-forward-service.sh stop-grafana
~/port-forward-service.sh start-flask
~/port-forward-service.sh stop-flask
```

#### View Logs

```bash
# Prometheus logs
tail -f /tmp/prometheus-port-forward.log

# Grafana logs
tail -f /tmp/grafana-port-forward.log

# Flask logs
tail -f /tmp/flask-port-forward.log
```

---

### Option 2: Using systemd Services (Recommended for Production)

This is the most robust solution - services will automatically restart on failure and start on boot.

#### Setup

1. **Use the automated setup script** (recommended):
   ```bash
   ./setup-systemd-services.sh
   ```

   This script will:
   - Create all necessary service files
   - Set up the wrapper script
   - Enable and start the services
   - Configure user lingering

2. **Or manually copy service files to your VM**:
   ```bash
   scp prometheus-port-forward.service username@your-vm-ip:~/
   scp grafana-port-forward.service username@your-vm-ip:~/
   scp flask-port-forward.service username@your-vm-ip:~/
   ```

3. **On your VM, install the services**:
   ```bash
   # Use user systemd (no sudo needed)
   mkdir -p ~/.config/systemd/user
   cp prometheus-port-forward.service ~/.config/systemd/user/
   cp grafana-port-forward.service ~/.config/systemd/user/
   cp flask-port-forward.service ~/.config/systemd/user/
   ```

4. **Edit the service files** to replace `%i` with your username:
   ```bash
   # For user systemd
   sed -i "s/%i/$(whoami)/g" ~/.config/systemd/user/prometheus-port-forward.service
   sed -i "s/%i/$(whoami)/g" ~/.config/systemd/user/grafana-port-forward.service
   sed -i "s/%i/$(whoami)/g" ~/.config/systemd/user/flask-port-forward.service
   ```

5. **Reload systemd and enable services**:
   ```bash
   # For user systemd
   systemctl --user daemon-reload
   systemctl --user enable prometheus-port-forward.service
   systemctl --user enable grafana-port-forward.service
   systemctl --user enable flask-port-forward.service
   
   # Start the services
   systemctl --user start prometheus-port-forward.service
   systemctl --user start grafana-port-forward.service
   systemctl --user start flask-port-forward.service
   
   # Enable lingering (keeps services running after logout)
   loginctl enable-linger $(whoami)
   ```

#### Usage

```bash
# Start services
systemctl --user start prometheus-port-forward.service
systemctl --user start grafana-port-forward.service
systemctl --user start flask-port-forward.service

# Stop services
systemctl --user stop prometheus-port-forward.service
systemctl --user stop grafana-port-forward.service
systemctl --user stop flask-port-forward.service

# Restart services
systemctl --user restart prometheus-port-forward.service
systemctl --user restart grafana-port-forward.service
systemctl --user restart flask-port-forward.service

# Check status
systemctl --user status prometheus-port-forward.service
systemctl --user status grafana-port-forward.service
systemctl --user status flask-port-forward.service

# View logs
journalctl --user -u prometheus-port-forward.service -f
journalctl --user -u grafana-port-forward.service -f
journalctl --user -u flask-port-forward.service -f

# Enable on boot
systemctl --user enable prometheus-port-forward.service
systemctl --user enable grafana-port-forward.service
systemctl --user enable flask-port-forward.service
```

---

### Option 3: Using screen (Simple Alternative)

If you prefer a simpler approach without scripts:

1. **Install screen** (if not already installed):
   ```bash
   sudo apt-get update && sudo apt-get install -y screen
   ```

2. **Create screen sessions for each service**:
   ```bash
   # Prometheus
   screen -S prometheus-forward
   kubectl port-forward --address 0.0.0.0 svc/prometheus-service -n monitoring 9090:9090
   # Press Ctrl+A then D to detach
   
   # Grafana
   screen -S grafana-forward
   kubectl port-forward --address 0.0.0.0 svc/grafana-service -n monitoring 3000:3000
   # Press Ctrl+A then D to detach
   
   # Flask
   screen -S flask-forward
   kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0
   # Press Ctrl+A then D to detach
   ```

3. **Reattach to sessions**:
   ```bash
   screen -r prometheus-forward
   screen -r grafana-forward
   screen -r flask-forward
   ```

4. **List all screen sessions**:
   ```bash
   screen -ls
   ```

---

### Option 4: Using tmux (Alternative to screen)

1. **Install tmux** (if not already installed):
   ```bash
   sudo apt-get update && sudo apt-get install -y tmux
   ```

2. **Create a tmux session**:
   ```bash
   tmux new -s port-forwards
   ```

3. **Start port-forwards in separate panes**:
   - Press `Ctrl+B` then `%` to split vertically
   - Press `Ctrl+B` then `"` to split horizontally
   - Navigate between panes with `Ctrl+B` then arrow keys
   - In each pane, start a port-forward:
     ```bash
     # Pane 1: Prometheus
     kubectl port-forward --address 0.0.0.0 svc/prometheus-service -n monitoring 9090:9090
     
     # Pane 2: Grafana
     kubectl port-forward --address 0.0.0.0 svc/grafana-service -n monitoring 3000:3000
     
     # Pane 3: Flask
     kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0
     ```

4. **Detach**: Press `Ctrl+B` then `D`

5. **Reattach**:
   ```bash
   tmux attach -t port-forwards
   ```

---

## 🔍 Verification

After setting up any method, verify the services are accessible:

```bash
# Test Prometheus
curl http://localhost:9090

# Test Grafana
curl http://localhost:3000

# Test Flask
curl http://localhost:5000

# Check if ports are listening
netstat -tlnp | grep -E "9090|3000|5000"
# Or
ss -tlnp | grep -E "9090|3000|5000"
```

You can also use the verification script:
```bash
./verify-port-forwards.sh
```

---

## 🐛 Troubleshooting

### Port-forward dies after a few minutes

**Solution**: Use systemd services with `Restart=always` (Option 2)

### Can't access from external IP

**Check**:
1. Firewall rules allow the ports
2. Port-forward is using `--address 0.0.0.0`
3. Service is actually running: `ps aux | grep "kubectl port-forward"`

### Services don't start on boot

**For systemd (Option 2)**:
```bash
# Ensure lingering is enabled
loginctl enable-linger $(whoami)

# Verify services are enabled
systemctl --user list-unit-files | grep port-forward
```

### Permission denied errors

**Solution**: Ensure kubectl is accessible and you have proper permissions:
```bash
which kubectl
kubectl get pods
```

### Service not found errors

**Check that services exist in Kubernetes**:
```bash
# Check Prometheus service
kubectl get svc prometheus-service -n monitoring

# Check Grafana service
kubectl get svc grafana-service -n monitoring

# Check Flask service
kubectl get svc flask-service
```

### Minikube-specific issues

If using Minikube, run:
```bash
./fix-minikube-port-forward.sh
```

This will ensure Minikube is running and update the services accordingly.

---

## 📝 Quick Reference

### Option 1 (Script) - Quick Commands
```bash
~/port-forward-service.sh start    # Start all
~/port-forward-service.sh status   # Check status
~/port-forward-service.sh stop    # Stop all
```

### Option 2 (systemd) - Quick Commands
```bash
systemctl --user start prometheus-port-forward.service
systemctl --user start grafana-port-forward.service
systemctl --user start flask-port-forward.service
systemctl --user status prometheus-port-forward.service
```

### Option 3/4 (screen/tmux) - Quick Commands
```bash
screen -ls              # List sessions
screen -r prometheus-forward # Reattach
tmux ls                 # List sessions
tmux attach -t port-forwards
```

### Diagnostic Commands
```bash
# Check for errors
./check-port-forward-errors.sh

# Get error messages
./get-port-forward-errors.sh

# Verify everything
./verify-port-forwards.sh
```

---

## 🎯 Recommendation

- **For quick setup**: Use **Option 1** (Service Script)
- **For production**: Use **Option 2** (systemd services)
- **For temporary/testing**: Use **Option 3 or 4** (screen/tmux)

---

## 📋 Service Details

| Service | Namespace | Port Mapping | Command |
|---------|-----------|--------------|---------|
| Prometheus | monitoring | 9090:9090 | `kubectl port-forward --address 0.0.0.0 svc/prometheus-service -n monitoring 9090:9090` |
| Grafana | monitoring | 3000:3000 | `kubectl port-forward --address 0.0.0.0 svc/grafana-service -n monitoring 3000:3000` |
| Flask | default | 5000:80 | `kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0` |

---

**Last Updated**: 2025-11-23
