#!/usr/bin/env python3
from prometheus_client import start_http_server, Gauge
import requests
import time
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define Prometheus metrics
# Node metrics
MMX_NODE_SYNCED = Gauge('mmx_node_synced', 'Whether the node is synced (1) or not (0)')
MMX_BLOCK_HEIGHT = Gauge('mmx_block_height', 'Current blockchain height')
MMX_VDF_HEIGHT = Gauge('mmx_vdf_height', 'Current VDF height')
MMX_VDF_SPEED = Gauge('mmx_vdf_speed', 'Current VDF speed')

# Farm metrics
MMX_PLOT_COUNT = Gauge('mmx_plot_count', 'Total number of plots')
MMX_FARM_SIZE_TB = Gauge('mmx_farm_size_tb', 'Total farm size in terabytes')
MMX_FARM_SIZE_EFFECTIVE_TB = Gauge('mmx_farm_size_effective_tb', 'Total effective farm size in terabytes')

# Network metrics
MMX_TOTAL_SUPPLY = Gauge('mmx_total_supply', 'Total supply of MMX')
MMX_BLOCK_REWARD = Gauge('mmx_block_reward', 'Current block reward')
MMX_SPACE_DIFFICULTY = Gauge('mmx_space_difficulty', 'Current space difficulty')

# MMX node RPC configuration
MMX_RPC_URL = "http://localhost:11380"  # Adjust this to your MMX node RPC endpoint
session = requests.Session()  # Create a session object to maintain cookies

# Read password from file
PASSWORD_FILE = os.getenv('MMX_PASSWORD_FILE', '/home/user/mmx-node/PASSWD')
try:
    with open(PASSWORD_FILE, 'r') as f:
        MMX_RPC_PASSWORD = f.read().strip()
    logging.info(f"Successfully loaded password from {PASSWORD_FILE}")
except Exception as e:
    logging.error(f"Failed to read password file {PASSWORD_FILE}: {e}")
    MMX_RPC_PASSWORD = ''

def login():
    try:
        response = session.get(f"{MMX_RPC_URL}/server/login", params={
            'user': 'mmx-admin',
            'passwd_plain': MMX_RPC_PASSWORD
        })
        if response.status_code == 200:
            logging.info("Successfully logged in to MMX node")
            logging.debug(f"Session cookies: {session.cookies}")
            return True
        else:
            logging.error(f"Failed to login: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return False

def get_network_info():
    try:
        if not login():
            return
        
        response = session.get(f"{MMX_RPC_URL}/api/node/get_network_info")
        logging.info(f"Network info response: {response.text}")
        data = response.json()
        
        MMX_NODE_SYNCED.set(1 if data['is_synced'] else 0)
        MMX_BLOCK_HEIGHT.set(data['height'])
        MMX_VDF_HEIGHT.set(data['vdf_height'])
        MMX_VDF_SPEED.set(data['vdf_speed'])
        MMX_TOTAL_SUPPLY.set(data['total_supply'] / 1000000)  # Convert to MMX units
        MMX_BLOCK_REWARD.set(data['block_reward'] / 1000000)  # Convert to MMX units
        MMX_SPACE_DIFFICULTY.set(data['space_diff'])
        
    except Exception as e:
        logging.error(f"Error collecting network metrics: {e}")

def get_farm_info():
    try:
        if not login():
            return
            
        response = session.get(f"{MMX_RPC_URL}/api/harvester/get_farm_info")
        logging.info(f"Farm info response: {response.text}")
        data = response.json()
        
        # Calculate total plots from plot_count array
        total_plots = sum(count for _, count in data['plot_count'])
        MMX_PLOT_COUNT.set(total_plots)
        
        # Convert bytes to TB
        farm_size_tb = data['total_bytes'] / (1024**4)  # Convert to TB
        farm_size_effective_tb = data['total_bytes_effective'] / (1024**4)  # Convert to TB
        
        MMX_FARM_SIZE_TB.set(farm_size_tb)
        MMX_FARM_SIZE_EFFECTIVE_TB.set(farm_size_effective_tb)
        
    except Exception as e:
        logging.error(f"Error collecting farm metrics: {e}")

def main():
    # Start up the server to expose the metrics.
    start_http_server(9877)
    print("MMX Exporter started on port 9877")

    while True:
        get_network_info()
        get_farm_info()
        time.sleep(10)

if __name__ == '__main__':
    main()