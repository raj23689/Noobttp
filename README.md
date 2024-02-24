# Noobttp
A minimalistic HTTP server implemented in python It is designed to be lightweight, simple, and easy to use for basic HTTP serving needs.


> [!CAUTION]
> This is not a **PRODUCTION** server. Proceed with caution, be ready for Negative potential consequences.

## Features

- **Simplicity**: Minimalistic design for straightforward usage.
- **Easy Setup**: Quick and easy to set up for serving static files or handling basic HTTP requests.
- **Lightweight**: Keep resource usage to a minimum.
- **Pythonic**: Written in Python for ease of understanding and modification.

## Getting Started

### Prerequisites

- Python 3.9 above

### Installation

Clone the repository:

```bash
git clone https://github.com/raj23689/Noobttp.git
cd Noobttp/
python server.py
```

#### For posting JSON data:

```bash
curl --header "Content-Type: application/json" -d '{"username":"xyz","password":"xyz"}' http://127.0.0.1:8888/

Received JSON data: {'username': 'xyz', 'password': 'xyz'} ## <- Response from Noobttp
```
#### For PATCH data:

```bash
curl -X PATCH http://127.0.0.1:8888/ -H "Content-Type: application/json" -H 'Accept: application/json' -d '{"username":"xyz","password":"xyz"}'
<h1>501 Not Implemented</h1> ## <- Response from Noobttp
```