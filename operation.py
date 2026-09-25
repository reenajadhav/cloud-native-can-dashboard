import streamlit as st
import subprocess

st.set_page_config(
    page_title="CAN Platform Operations",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 CAN Platform Operations Dashboard")

col1, col2 = st.columns(2)

# -----------------------------------------------------
# Grafana
# -----------------------------------------------------
with st.container(border=True):
    st.subheader("📊 Grafana")

    if st.button("Start Grafana"):
        subprocess.check_output([
            "kubectl",
            "port-forward",
            "-n",
            "monitoring",
            "svc/prometheus-grafana",
            "3001:80"
        ])

    st.link_button(
        "Open Grafana",
        "http://localhost:3001"
    )

# -----------------------------------------------------
# Prometheus
# -----------------------------------------------------
with st.container(border=True):
    st.subheader("📈 Prometheus")

    if st.button("Start Prometheus"):
        subprocess.check_output([
            "kubectl",
            "port-forward",
            "-n",
            "monitoring",
            "svc/prometheus-kube-prometheus-prometheus",
            "9090:9090"
        ])

    st.link_button(
        "Open Prometheus",
        "http://localhost:9090"
    )

# -----------------------------------------------------
# ArgoCD
# -----------------------------------------------------
with st.container(border=True):
    st.subheader("🚀 ArgoCD")

    if st.button("Start ArgoCD"):
        subprocess.check_output([
            "kubectl",
            "port-forward",
            "-n",
            "argocd",
            "svc/argocd-server",
            "8080:443"
        ])

    st.link_button(
        "Open ArgoCD",
        "https://localhost:8080"
    )

# -----------------------------------------------------
# Vehicle Dashboard
# -----------------------------------------------------
with st.container(border=True):
    st.subheader("🚗 Vehicle Dashboard")
    if st.button("Get Dashboard URL"):
        url = subprocess.check_output(
            [
                "minikube",
                "service",
                "dashboard-dev",
                "-n",
                "dev",
                "--url"
            ],
            text=True
        ).strip()

        st.success(url)

        st.link_button(
            "Open Dashboard",
            url
        )