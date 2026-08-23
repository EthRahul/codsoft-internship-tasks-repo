#!/bin/bash
# alert_responder.sh
# Basic automated response action: watches Suricata's eve.json log in real
# time, and whenever a new alert event appears, prints a formatted warning
# and appends it to a persistent incident log.
#
# Usage: ./alert_responder.sh

tail -Fn0 /var/log/suricata/eve.json | while read line; do
    if echo "$line" | grep -q '"event_type":"alert"'; then
        msg=$(echo "$line" | grep -oP '(?<="signature":")[^"]*')
        src=$(echo "$line" | grep -oP '(?<="src_ip":")[^"]*')
        echo "[ALERT] $(date '+%H:%M:%S') - $msg from $src" | tee -a ~/incident_log.txt
    fi
done
