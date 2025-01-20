# mmx-exporter

A Prometheus exporter for monitoring MMX (MadMax) farming operations.

## Description

This exporter collects metrics from MMX farming operations and exposes them in Prometheus format, allowing for monitoring and alerting of your farming activities.

## Features

- Basic monitoring of MMX farm status
- Prometheus metrics export
- Easy integration with existing monitoring setups

## Service
```ini
[Unit]
Description=MMX Exporter
After=network.target

[Service]
Type=simple
User=user
Group=user
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=/home/user/mmx-exporter
ExecStart=/usr/bin/python3 /home/user/mmx-exporter/mmx-exporter.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Generated with the assistance of Claude on Cursor
- MMX farming community


