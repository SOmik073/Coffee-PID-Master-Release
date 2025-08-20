# Coffee-PID-Master-Release

A Python-based PID (Proportional-Integral-Derivative) controller for coffee brewing temperature control.

## Features

- Real-time temperature control using PID algorithm
- SQLite database logging for temperature history
- Simple command-line interface
- Web API interface (simulated)
- Configuration management

## Usage

```bash
python main.py
```

## Commands

- `start` - Start the PID controller
- `stop` - Stop the PID controller  
- `status` - Get current temperature and status
- `set_temp <value>` - Set target temperature
- `quit` - Exit the application

## Configuration

Edit `config.py` to modify PID parameters and system settings.

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)