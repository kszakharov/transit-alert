# TTC Alerts CLI

A command-line tool for monitoring Toronto Transit Commission (TTC) service alerts in real-time.

## Features

- Fetch and display current TTC service alerts
- Monitor alerts continuously with customizable intervals
- Output alerts in JSON format
- Configurable logging
- Support for GTFS-RT (General Transit Feed Specification - Real Time) protocol

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ttc_alerts.git
cd ttc_alerts

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Usage

### Basic Usage

```bash
# Display current alerts
ttc-alerts

# Monitor alerts continuously (checking every 5 minutes)
ttc-alerts --monitor

# Monitor with custom interval (e.g., 10 minutes)
ttc-alerts --monitor --interval 10

# Output alerts in JSON format
ttc-alerts --json

# Enable debug logging
ttc-alerts --debug

# Specify log file
ttc-alerts --log-file alerts.log
```

### Command Line Options

- `--monitor`: Monitor alerts continuously
- `--interval`: Check interval in minutes for monitoring (default: 5)
- `--json`: Output alerts in JSON format
- `--log-file`: Path to log file
- `--debug`: Enable debug logging

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=ttc_alerts
```

### Project Structure

```
ttc_alerts/
├── __init__.py
├── cli.py
├── core/
│   ├── __init__.py
│   ├── fetcher.py
│   ├── parser.py
│   └── formatter.py
├── utils/
│   ├── __init__.py
│   ├── logging.py
│   └── config.py
└── tests/
    ├── __init__.py
    ├── test_fetcher.py
    ├── test_parser.py
    └── test_formatter.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 