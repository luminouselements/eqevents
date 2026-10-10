#!/usr/bin/env python3
import json
import logging
import os  # Required for deduplication file check
import time # Imported for the broadcast delay
from urllib.request import Request, urlopen
import meshtastic
import meshtastic.tcp_interface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Earthquake Query Configuration (Global default values RADIUS_KM = 20001.6 | MIN_MAG = 3.0)
"""
EQ_LAT = 27.9517
EQ_LON = -82.4587
EQ_RADIUS_KM = 20001.6
EQ_MIN_MAG = 3.0
"""

EQ_LAT = 27.4678
EQ_LON = -82.1336
EQ_RADIUS_KM = 600
EQ_MIN_MAG = 1.0

# Meshtastic Node Configuration
NODE_IP = "192.168.50.46"
CHANNEL_INDEX = 5  # Ensure this matches your target channel
MAX_CHARS = 200

# State Tracking (Deduplication)
STATE_FILE = "last_eq_id.txt"

def fetch_latest_earthquake():
    api_url = (
        f"https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&limit=1&orderby=time"
        f"&latitude={EQ_LAT}&longitude={EQ_LON}"
        f"&maxradiuskm={EQ_RADIUS_KM}&minmagnitude={EQ_MIN_MAG}"
    )

    logger.info(f"Fetching earthquake data (Min Mag: {EQ_MIN_MAG}, Radius: {EQ_RADIUS_KM}km)...")
    req = Request(api_url, headers={"User-Agent": "Debian-EQ-Standalone"})

    try:
        with urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            features = data.get("features", [])
            if not features:
                logger.warning("No earthquake events found matching the criteria.")
                return None, None

            # Return both the unique ID and the properties for deduplication
            latest_feature = features[0]
            return latest_feature.get("id"), latest_feature.get("properties")
    except Exception as e:
        logger.error(f"Failed to fetch API payload: {e}")
        return None, None

def main():
    logger.info("Starting Meshtastic Earthquake monitor...")

    eq_id, eq_data = fetch_latest_earthquake()
    if not eq_data or not eq_id:
        return

    # Deduplication check
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = f.read().strip()
        if eq_id == last_id:
            logger.info(f"Earthquake {eq_id} already processed. Skipping transmission.")
            return
    else:
        logger.info("No state file found. This is the first run.")

    # Grab the data for earthquake events from API payload
    title = eq_data.get("title", "Unknown Event")
    url = eq_data.get("url", "")
    eq_type = eq_data.get("type", "earthquake")
    tsunami = eq_data.get("tsunami", 0)

    # Format to display title and link on separate rows
    message = f"⚠️{eq_type.capitalize()}:⚠️\nⓘ {title}\n🌊 {'✅Yes' if tsunami == 1 else '❌No'}\n🔗 [https://usgs.gov]({url})"
    logger.info(f"Formatted message payload:\n{message}")

    if len(message) > MAX_CHARS:
        logger.warning(f"Message exceeds {MAX_CHARS} characters ({len(message)} chars). Truncating.")
        message = message[:MAX_CHARS]
    else:
        logger.info(f"Message length validation passed: {len(message)} characters.")

    logger.info(f"Connecting to Meshtastic node at TCP {NODE_IP}...")
    try:
        interface = meshtastic.tcp_interface.TCPInterface(hostname=NODE_IP)
        logger.info(f"Sending message on channel {CHANNEL_INDEX}...")
        interface.sendText(message, channelIndex=CHANNEL_INDEX)

        # Give the node 5 seconds to process and broadcast over LoRa
        logger.info("Waiting for transmission to complete...")
        time.sleep(5)

        logger.info("Message dispatched successfully.")
        interface.close()

        # Save the new ID to prevent future duplicates
        with open(STATE_FILE, "w") as f:
            f.write(eq_id)
        logger.info(f"Saved event ID {eq_id} to state file.")

    except Exception as e:
        logger.error(f"Meshtastic transmission failed: {e}")

if __name__ == "__main__":
    main()
