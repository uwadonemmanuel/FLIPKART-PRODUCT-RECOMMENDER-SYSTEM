#!/bin/bash

# Port Forward Service Script
# This script manages kubectl port-forward processes for Prometheus, Grafana, and Flask

PROMETHEUS_PID_FILE="/tmp/prometheus-port-forward.pid"
GRAFANA_PID_FILE="/tmp/grafana-port-forward.pid"
FLASK_PID_FILE="/tmp/flask-port-forward.pid"

start_prometheus() {
    if [ -f "$PROMETHEUS_PID_FILE" ] && kill -0 $(cat "$PROMETHEUS_PID_FILE") 2>/dev/null; then
        echo "Prometheus port-forward is already running (PID: $(cat $PROMETHEUS_PID_FILE))"
        return 1
    fi
    
    nohup kubectl port-forward --address 0.0.0.0 svc/prometheus-service -n monitoring 9090:9090 > /tmp/prometheus-port-forward.log 2>&1 &
    echo $! > "$PROMETHEUS_PID_FILE"
    echo "Prometheus port-forward started (PID: $(cat $PROMETHEUS_PID_FILE))"
}

stop_prometheus() {
    if [ -f "$PROMETHEUS_PID_FILE" ]; then
        PID=$(cat "$PROMETHEUS_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "Prometheus port-forward stopped (PID: $PID)"
        else
            echo "Prometheus port-forward process not found"
        fi
        rm -f "$PROMETHEUS_PID_FILE"
    else
        echo "Prometheus port-forward is not running"
    fi
}

start_grafana() {
    if [ -f "$GRAFANA_PID_FILE" ] && kill -0 $(cat "$GRAFANA_PID_FILE") 2>/dev/null; then
        echo "Grafana port-forward is already running (PID: $(cat $GRAFANA_PID_FILE))"
        return 1
    fi
    
    nohup kubectl port-forward --address 0.0.0.0 svc/grafana-service -n monitoring 3000:3000 > /tmp/grafana-port-forward.log 2>&1 &
    echo $! > "$GRAFANA_PID_FILE"
    echo "Grafana port-forward started (PID: $(cat $GRAFANA_PID_FILE))"
}

stop_grafana() {
    if [ -f "$GRAFANA_PID_FILE" ]; then
        PID=$(cat "$GRAFANA_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "Grafana port-forward stopped (PID: $PID)"
        else
            echo "Grafana port-forward process not found"
        fi
        rm -f "$GRAFANA_PID_FILE"
    else
        echo "Grafana port-forward is not running"
    fi
}

start_flask() {
    if [ -f "$FLASK_PID_FILE" ] && kill -0 $(cat "$FLASK_PID_FILE") 2>/dev/null; then
        echo "Flask port-forward is already running (PID: $(cat $FLASK_PID_FILE))"
        return 1
    fi
    
    nohup kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0 > /tmp/flask-port-forward.log 2>&1 &
    echo $! > "$FLASK_PID_FILE"
    echo "Flask port-forward started (PID: $(cat $FLASK_PID_FILE))"
}

stop_flask() {
    if [ -f "$FLASK_PID_FILE" ]; then
        PID=$(cat "$FLASK_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "Flask port-forward stopped (PID: $PID)"
        else
            echo "Flask port-forward process not found"
        fi
        rm -f "$FLASK_PID_FILE"
    else
        echo "Flask port-forward is not running"
    fi
}

status() {
    echo "=== Port-Forward Status ==="
    if [ -f "$PROMETHEUS_PID_FILE" ] && kill -0 $(cat "$PROMETHEUS_PID_FILE") 2>/dev/null; then
        echo "Prometheus: Running (PID: $(cat $PROMETHEUS_PID_FILE))"
    else
        echo "Prometheus: Not running"
    fi
    
    if [ -f "$GRAFANA_PID_FILE" ] && kill -0 $(cat "$GRAFANA_PID_FILE") 2>/dev/null; then
        echo "Grafana: Running (PID: $(cat $GRAFANA_PID_FILE))"
    else
        echo "Grafana: Not running"
    fi
    
    if [ -f "$FLASK_PID_FILE" ] && kill -0 $(cat "$FLASK_PID_FILE") 2>/dev/null; then
        echo "Flask: Running (PID: $(cat $FLASK_PID_FILE))"
    else
        echo "Flask: Not running"
    fi
}

case "$1" in
    start)
        start_prometheus
        start_grafana
        start_flask
        ;;
    stop)
        stop_prometheus
        stop_grafana
        stop_flask
        ;;
    restart)
        stop_prometheus
        stop_grafana
        stop_flask
        sleep 2
        start_prometheus
        start_grafana
        start_flask
        ;;
    status)
        status
        ;;
    start-prometheus)
        start_prometheus
        ;;
    stop-prometheus)
        stop_prometheus
        ;;
    start-grafana)
        start_grafana
        ;;
    stop-grafana)
        stop_grafana
        ;;
    start-flask)
        start_flask
        ;;
    stop-flask)
        stop_flask
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|start-prometheus|stop-prometheus|start-grafana|stop-grafana|start-flask|stop-flask}"
        exit 1
        ;;
esac

exit 0
