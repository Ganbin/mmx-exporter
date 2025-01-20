# mmx-exporter

A Prometheus exporter for monitoring MMX (MadMax) farming operations.

## Description

This exporter collects metrics from MMX farming operations and exposes them in Prometheus format, allowing for monitoring and alerting of your farming activities.

## Features

- Basic monitoring of MMX farm status
- Prometheus metrics export
- Easy integration with existing monitoring setups

## Getting Started

1. Copy the mmx-exporter.py file to your server
2. To generate a password file, run `./build/tools/generate_passwd > RPC_PASSWD`.
3. Follow [the instruction](https://github.com/madMAx43v3r/mmx-node/blob/master/docs/RPC_protocol.md) for authentication. I recommend using the `"USER"` access level.
4. Change the `PASSWORD_FILE` variable in the mmx-exporter.py file to the path of the API token file
5. Create the service
6. Run the service.
7. Import the grafana dashboard from `mmx-grafana.json`, and you should be able to see the metrics in the dashboard.

## Service

Create the service file:

```bash
sudo nano /etc/systemd/system/mmx-exporter.service
```

Add the following content:

```ini
[Unit]
Description=MMX Exporter
After=network.target

[Service]
Type=simple
User=user
Group=user
Environment=PYTHONUNBUFFERED=1
Environment="MMX_PASSWORD_FILE=/home/user/mmx-node/RPC_PASSWD"
WorkingDirectory=/home/user/mmx-exporter
ExecStart=/usr/bin/python3 /home/user/mmx-exporter/mmx-exporter.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Reload the systemd daemon and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mmx-exporter
sudo systemctl start mmx-exporter
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Generated with the assistance of Claude on Cursor
- MMX community
- [madMAx43v3r](https://github.com/madMAx43v3r) for the MMX node and RPC protocol