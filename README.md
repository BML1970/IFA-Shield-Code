# FL-IFAshield Source Code
# FL-IFAshield: Federated Learning Framework for Adaptive IFA Mitigation in NDN

FL-IFAshield is a secure, decentralized, and Byzantine-robust framework designed to mitigate Interest Flooding Attacks (IFAs)—including sophisticated Collusive IFAs CIFA)—in Named Data Networking (NDN) architectures.

Rather than relying on localized simulation models (such as ndnSIM), FL-IFAshield is built and validated natively on real-world bare-metal physical routers. This repository contains the complete open-source release of the core execution daemons, native forwarding engine integration hooks, and automated topology provisioning playbooks.

---

## Architectural Overview

The framework operates symmetrically across a distributed edge computing fabric, consisting of four interdependent functional modules:
1. **Stateful Monitor:** Extracts continuous, line-rate temporal features directly from the NDN forwarding plane.
2. **Poisson-EMA Detector:** Implements dynamic local thresholding using maximum likelihood estimations to detect anomalous traffic spikes.
3. **Byzantine-Robust Secure Aggregator:** Combines local updates at the central orchestrator using Top-$k$ sparsification, Differential Privacy (DP) Gaussian noise injection, and Krum-filtering to block poisoned model updates.
4. **Three-Tier Mitigation State Machine:** Executes an escalating graduated mitigation defense policy directly inside the router kernel based on real-time anomaly scores ($p_a$).

---

## System Specifications & Environment

The experimental evaluation was benchmarked continuously for 24 hours across **100 heterogeneous physical nodes** on the open-access **FIT/IoT-LAB testbed infrastructure** (Grenoble and Lille Site Topology Clusters).

### Hardware Configuration (Per Node)
* **CPU Architecture:** ARMv8 Cortex-A53 (64-bit Core running @ 1.2 GHz)
* **Memory & Storage:** 1 GB LPDDR3 RAM / 16 GB MicroSD Card
* **Resource Footprint:** $<9\%$ Mean CPU utilization ($8.42\%$ average, $14.52\%$ worst-case peak) and $\approx 32.4 \text{ MB}$ memory footprint.

### Software Stack
* **Operating System:** Yocto Embedded Linux (Kernel v5.4.0-xilinx)
* **NDN Core Daemon:** Named Data Networking Forwarding Daemon (NFD) version 0.7.1
* **Machine Learning Stack:** Python 3.8.10, PyTorch Mobile v1.9.0, Scikit-Learn micro

### Network Table Configurations
* **Maximum PIT Capacity:** 10,000 concurrent outgoing entries per node
* **PIT Entry Lifetime ($T_{\text{life}}$):** 4.0 seconds (Drop-tail boundary)
* **PIT Replacement Policy:** Least Recently Used (LRU) with Non-Asymptotic Expiry
* **Content Store (CS) Capacity:** 2,000 Content Objects (LRU Eviction)

### FL Hyperparameters & Model Properties
* **Model Size:** 42.5 KB serialized ProtoBuf (Optimized MLP: 3 input features $\rightarrow$ 8 hidden ReLU neurons $\rightarrow$ 2 classification output classes with Softmax)
* **Synchronization Interval ($T$):** Dynamic global updates every 60 seconds
* **Local Optimization:** 3 local epochs ($E$) per cycle via Adam Optimizer ($\eta = 10^{-3}$, batch size 32)

---

## 📁 Repository Structure

```text
├── automation/
│   ├── iotlab_orchestrator.py   # Main Python script for provisioning physical nodes
│   ├── provision_edge.yml       # Ansible playbook for compiling and deploying files
│   └── traffic_generator.sh     # Benign Zipfian & malicious CIFA traffic injector
├── src/
│   ├── local_pipeline.py        # Python local training daemon & Poisson-EMA engine
│   ├── mitigation_engine.py     # Three-tier state machine mitigation system
│   └── server_aggregator.py     # Secure, Krum-filtered central aggregator
└── native-hooks/
    ├── ifashield-feature-hook.hpp  # NFD native metrics telemetry collector header
    ├── ifashield-feature-hook.cpp  # Line-rate feature gathering logic source code
    └── forwarder.cpp.patch      # Context patch line modifications for NFD v0.7.1