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
MMX_AVERAGE_TXFEE = Gauge('mmx_average_txfee', 'Average transaction fee')
MMX_BLOCK_SIZE = Gauge('mmx_block_size', 'Current block size')

# Farm block metrics
MMX_FARM_BLOCKS_COUNT = Gauge('mmx_farm_blocks_count', 'Number of blocks found in period')
MMX_FARM_BLOCKS_LAST_HEIGHT = Gauge('mmx_farm_blocks_last_height', 'Last height of found block')
MMX_FARM_BLOCKS_TOTAL_REWARDS = Gauge('mmx_farm_blocks_total_rewards', 'Total rewards value for found blocks')

# Wallet metrics
MMX_WALLET_BALANCE_TOTAL = Gauge('mmx_wallet_balance_total', 'Total wallet balance')
MMX_WALLET_BALANCE_SPENDABLE = Gauge('mmx_wallet_balance_spendable', 'Spendable wallet balance')
MMX_WALLET_BALANCE_LOCKED = Gauge('mmx_wallet_balance_locked', 'Locked wallet balance')
MMX_WALLET_BALANCE_RESERVED = Gauge('mmx_wallet_balance_reserved', 'Reserved wallet balance')

# MMX node RPC configuration
MMX_RPC_URL = "http://localhost:11380"  # Adjust this to your MMX node RPC endpoint

# Read token from file
PASSWORD_FILE = os.getenv('MMX_PASSWORD_FILE', '/home/user/mmx-node/RPC_PASSWD')
try:
    with open(PASSWORD_FILE, 'r') as f:
        API_TOKEN = f.read().strip()
    logging.info(f"Successfully loaded token from {PASSWORD_FILE}")
except Exception as e:
    logging.error(f"Failed to read token file {PASSWORD_FILE}: {e}")
    API_TOKEN = ''

def get_network_info():
    try:
        headers = {'x-api-token': API_TOKEN}
        response = requests.get(f"{MMX_RPC_URL}/wapi/node/info", headers=headers)
        logging.debug(f"Network info response: {response.text}")
        data = response.json()
        
        MMX_NODE_SYNCED.set(1 if data['is_synced'] else 0)
        MMX_BLOCK_HEIGHT.set(data['height'])
        MMX_VDF_HEIGHT.set(data['vdf_height'])
        MMX_VDF_SPEED.set(data['vdf_speed'])
        MMX_TOTAL_SUPPLY.set(float(data['total_supply']) / 1000000)  # Convert to MMX units
        MMX_BLOCK_REWARD.set(data['block_reward']['value'])
        MMX_SPACE_DIFFICULTY.set(data['space_diff'])
        MMX_AVERAGE_TXFEE.set(data['average_txfee']['value'])
        MMX_BLOCK_SIZE.set(data['block_size'])
        
    except Exception as e:
        logging.error(f"Error collecting network metrics: {e}")

def get_farm_info():
    try:
        headers = {'x-api-token': API_TOKEN}
        response = requests.get(f"{MMX_RPC_URL}/wapi/farm/info", headers=headers)
        logging.debug(f"Farm info response: {response.text}")
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
        logging.error(f"Error collecting farm info metrics: {e}")
  
def get_farm_block_summary():
    try:
        headers = {'x-api-token': API_TOKEN}
        response = requests.get(f"{MMX_RPC_URL}/wapi/farm/blocks/summary", params={'since': 10000}, headers=headers)
        logging.debug(f"Farm blocks summary response: {response.text}")
        data = response.json()
        
        MMX_FARM_BLOCKS_COUNT.set(data['num_blocks'])
        MMX_FARM_BLOCKS_LAST_HEIGHT.set(data['last_height'])
        MMX_FARM_BLOCKS_TOTAL_REWARDS.set(data['total_rewards_value'])
        
    except Exception as e:
        logging.error(f"Error collecting farm blocks summary metrics: {e}")

def get_wallet_balance():
    try:
        headers = {'x-api-token': API_TOKEN}
        response = requests.get(f"{MMX_RPC_URL}/wapi/wallet/balance", params={'index': 0}, headers=headers)
        logging.debug(f"Wallet balance response: {response.text}")
        data = response.json()
        
        # Find the MMX balance (native token)
        for balance in data['balances']:
            if balance['is_native']:
                MMX_WALLET_BALANCE_TOTAL.set(balance['total'])
                MMX_WALLET_BALANCE_SPENDABLE.set(balance['spendable'])
                MMX_WALLET_BALANCE_LOCKED.set(balance['locked'])
                MMX_WALLET_BALANCE_RESERVED.set(balance['reserved'])
                break
                
    except Exception as e:
        logging.error(f"Error collecting wallet balance metrics: {e}")

def main():
    try:
        # Start up the server to expose the metrics.
        start_http_server(9877)
        logging.info("MMX Exporter started on port 9877")

        while True:
            get_network_info()
            get_farm_info()
            get_farm_block_summary()
            get_wallet_balance()
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Exporter stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()