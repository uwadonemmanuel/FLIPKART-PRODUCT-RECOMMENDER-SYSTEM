# VM Setup Guide - Port Forward Services

This guide shows you how to set up and run the port-forward services on your VM.

## 🚀 Quick Start (Method 1: Simple Script)

This is the fastest way to get started.

### Step 1: Transfer Files to VM

From your local machine, copy the script to your VM:

```bash
# Replace with your VM details
VM_USER="your-username"
VM_IP="your-vm-ip-address"

# Copy the main script
scp port-forward-service/port-forward-service.sh ${VM_USER}@${VM_IP}:~/
```

### Step 2: On Your VM

SSH into your VM:

```bash
ssh ${VM_USER}@${VM_IP}
```

Then run:

```bash
# Make the script executable
chmod +x ~/port-forward-service.sh

# Start all port-forwards
~/port-forward-service.sh start

# Check status
~/port-forward-service.sh status
```

### Step 3: Verify It's Working

```bash
# Check if ports are listening
ss -tlnp | grep -E "9090|3000|5000"

# Or test with curl
curl http://localhost:9090  # Prometheus
curl http://localhost:3000  # Grafana
curl http://localhost:5000  # Flask
```

### Usage Commands

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

### View Logs

```bash
# Prometheus logs
tail -f /tmp/prometheus-port-forward.log

# Grafana logs
tail -f /tmp/grafana-port-forward.log

# Flask logs
tail -f /tmp/flask-port-forward.log
```

---

## 🔧 Production Setup (Method 2: systemd Services)

This method provides automatic restart and boot-time startup.

### Step 1: Transfer All Files to VM

From your local machine:

```bash
VM_USER="your-username"
VM_IP="your-vm-ip-address"

# Create a temporary directory on VM
ssh ${VM_USER}@${VM_IP} "mkdir -p ~/port-forward-setup"

# Copy all necessary files
scp port-forward-service/setup-systemd-services.sh ${VM_USER}@${VM_IP}:~/port-forward-setup/
scp port-forward-service/port-forward-wrapper.sh ${VM_USER}@${VM_IP}:~/port-forward-setup/
scp port-forward-service/prometheus-port-forward.service ${VM_USER}@${VM_IP}:~/port-forward-setup/
scp port-forward-service/grafana-port-forward.service ${VM_USER}@${VM_IP}:~/port-forward-setup/
scp port-forward-service/flask-port-forward.service ${VM_USER}@${VM_IP}:~/port-forward-setup/
```

### Step 2: On Your VM - Run Setup Script

SSH into your VM:

```bash
ssh ${VM_USER}@${VM_IP}
```

Then:

```bash
cd ~/port-forward-setup

# Make setup script executable
chmod +x setup-systemd-services.sh

# Run the setup (this will create and start all services)
./setup-systemd-services.sh
```

The setup script will:
- ✅ Create systemd service files
- ✅ Set up the wrapper script
- ✅ Enable services to start on boot
- ✅ Start all services immediately
- ✅ Configure user lingering (keeps services running after logout)

### Step 3: Verify Services Are Running

```bash
# Check service status
systemctl --user status prometheus-port-forward.service
systemctl --user status grafana-port-forward.service
systemctl --user status flask-port-forward.service

# Or check all at once
systemctl --user list-units | grep port-forward
```

### Usage Commands

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

# View logs (follow mode)
journalctl --user -u prometheus-port-forward.service -f
journalctl --user -u grafana-port-forward.service -f
journalctl --user -u flask-port-forward.service -f

# View recent logs
journalctl --user -u prometheus-port-forward.service -n 50
```

### Enable/Disable on Boot

```bash
# Enable services to start on boot
systemctl --user enable prometheus-port-forward.service
systemctl --user enable grafana-port-forward.service
systemctl --user enable flask-port-forward.service

# Disable services from starting on boot
systemctl --user disable prometheus-port-forward.service
systemctl --user disable grafana-port-forward.service
systemctl --user disable flask-port-forward.service
```

---

## 🐛 Troubleshooting

### If Using Minikube

If you're using Minikube, you may need to run the Minikube fix script:

```bash
# Transfer the fix script
scp port-forward-service/fix-minikube-port-forward.sh ${VM_USER}@${VM_IP}:~/

# On VM
chmod +x ~/fix-minikube-port-forward.sh
./fix-minikube-port-forward.sh
```

### Check for Errors

Transfer the diagnostic scripts:

```bash
scp port-forward-service/verify-port-forwards.sh ${VM_USER}@${VM_IP}:~/
scp port-forward-service/check-port-forward-errors.sh ${VM_USER}@${VM_IP}:~/
scp port-forward-service/get-port-forward-errors.sh ${VM_USER}@${VM_IP}:~/
```

On VM:

```bash
chmod +x ~/verify-port-forwards.sh
chmod +x ~/check-port-forward-errors.sh
chmod +x ~/get-port-forward-errors.sh

# Run diagnostics
./verify-port-forwards.sh
./check-port-forward-errors.sh
./get-port-forward-errors.sh
```

### Common Issues

1. **Services not found in Kubernetes**
   ```bash
   # Check if services exist
   kubectl get svc prometheus-service -n monitoring
   kubectl get svc grafana-service -n monitoring
   kubectl get svc flask-service
   ```

2. **Ports already in use**
   ```bash
   # Check what's using the ports
   sudo lsof -i :9090
   sudo lsof -i :3000
   sudo lsof -i :5000
   ```

3. **Can't access from external IP**
   ```bash
   # Verify ports are listening on 0.0.0.0
   ss -tlnp | grep -E "9090|3000|5000"
   # Should show 0.0.0.0:PORT, not 127.0.0.1:PORT
   ```

4. **Services stop after logout**
   ```bash
   # Enable lingering (for systemd method)
   sudo loginctl enable-linger $(whoami)
   ```

---

## 📋 Quick Reference

### Method 1 (Simple Script)
```bash
# One-time setup
scp port-forward-service/port-forward-service.sh user@vm:~
ssh user@vm "chmod +x ~/port-forward-service.sh"

# Daily usage
ssh user@vm "~/port-forward-service.sh start"
ssh user@vm "~/port-forward-service.sh status"
```

### Method 2 (systemd - Recommended)
```bash
# One-time setup
scp -r port-forward-service/* user@vm:~/port-forward-setup/
ssh user@vm "cd ~/port-forward-setup && chmod +x setup-systemd-services.sh && ./setup-systemd-services.sh"

# Services will auto-start on boot and restart on failure
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Prometheus accessible at `http://VM_IP:9090`
- [ ] Grafana accessible at `http://VM_IP:3000`
- [ ] Flask accessible at `http://VM_IP:5000`
- [ ] Services survive SSH disconnect (for systemd method)
- [ ] Services restart automatically on failure (for systemd method)
- [ ] Services start on boot (for systemd method)

---

**Last Updated**: 2025-11-23

