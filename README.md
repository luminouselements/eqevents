# eqevents
Earthquake Event Monitor for Meshtastic

This script, `eqevents.py`, is a utility designed to monitor for recent earthquake events from the USGS Earthquake Hazards Program. It fetches the latest earthquake data within a specified radius and magnitude, and if an event is found, it formats a message and attempts to broadcast it via TCP on local LAN to Meshtastic Node.

## 🚀 Features

*   **USGS Integration**: Fetches real-time earthquake data from the USGS API.
*   **Deduplication**: Uses a local state file (`last_eq_id.txt`) to ensure that the same earthquake event is not broadcast multiple times.
*   **Meshtastic Broadcast**: Sends a formatted alert message over the configured Meshtastic LoRa channel.

## 🛠️ Installation

### Prerequisites

You must have Python 3 installed and a working Meshtastic radio setup connected to the specified IP address (`192.168.0.1`).

### Dependencies

The required Python packages are listed in `requirements.txt`.

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```


### 📄 Logging and Output

By default, the script logs all activity (INFO, WARNING, ERROR) directly to the console (standard error stream).

If you need to capture logs for later review, you can redirect the script's output when running it from your terminal:

```bash
python eqevents.py > eqevents.log 2>&1
```

This command redirects both standard output (`> eqevents.log`) and standard error (`2>&1`) into a file named `eqevents.log` in the current directory.

## ⚠️ Troubleshooting

*   **Meshtastic Connection Error**: Ensure your Meshtastic radio is powered on and connected to the specified `NODE_IP`.
*   **API Errors**: Check your network connection and ensure the USGS API endpoint is accessible.
*   **Deduplication**: If you need to manually force a re-broadcast of an event, delete the `last_eq_id.txt` file.

## 🔎 Example Alert Message - (200 Character Limit)
⚠️Earthquake:⚠️
ⓘ M 8.0 - 14 km SW of Pitaloza Arriba, Panama
🌊 ❌No
🔗 [https://usgs.gov](https://earthquake.usgs.gov/earthquakes/eventpage/pt26282000)
