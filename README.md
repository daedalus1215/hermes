```
██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗
██║  ██║██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝
███████║█████╗  ██████╔╝██╔████╔██║█████╗  ███████╗
██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║
██║  ██║███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝

                  Messenger of the gods
```

# Hermes Backend

> **Text-to-Speech (TTS) service that converts text into WAV audio using the Kokoro pipeline.**

---

## Overview

Hermes is a small Python service that turns text into audio files. It exposes an HTTP API for on-demand TTS generation and stores results on disk using a user/asset-based folder layout.

Internally it uses the Kokoro TTS pipeline to generate one or more WAV segments, then combines them into a single `combined.wav` output per request.

### Key Features

- **TTS API**: `POST /api/v1/text-to-speech` generates audio from text
- **Audio downloads**: `GET /api/v1/download/{user_id}/{asset_id}` serves the combined WAV
- **Configurable storage**: YAML config with environment overrides
- **Clean architecture**: domain/application/infrastructure layers with transaction scripts

### Role in Chronus Ecosystem

Hermes is a standalone TTS service. Chronus will call the API to generate voice assets, or integrate via the Clio-to-Hermes pipeline folders.

---

## Prerequisites

- **Python**: 3.12.3
- **pip**: Latest compatible with Python 3.12
- **GPU (optional)**: CUDA-capable GPU for faster Kokoro inference

---

## Getting Started

### 1. Installation

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the sample config
cp app/configs/config.yaml.sample app/configs/config.yaml
```

Environment variables (optional overrides):

- `HERMES_API_HOST`
- `HERMES_API_PORT`
- `HERMES_API_BASE_URL`
- `HERMES_API_AUDIO_DIR`
- `HERMES_OUTPUT_FOLDER`

### 3. Start the API

```bash
python -m uvicorn app.application.api_controller.api_controller:app --reload
```

Custom host/port:

```bash
python -m uvicorn --host {ipAddress} --port {port} app.application.api_controller.api_controller:app --reload
```

The API runs on `http://{host}:{port}` with base path `/{base_url}` (default `/api/v1`).

---

## Common Commands

| Command | Description |
| --- | --- |
| `python -m uvicorn app.application.api_controller.api_controller:app --reload` | Start API server |

### Testing

No automated test runner is configured yet.

---

## API Endpoints

### Text to Speech

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/text-to-speech` | Generate WAV audio from text |

Request body:

```json
{
  "text": "Hello world",
  "userId": "user-123",
  "assetId": "asset-456"
}
```

Response:

```json
{
  "file_path": "../resources/hermes-process/user-123/asset-456/combined_2026-02-08_14-30-00.wav",
  "file_name": "combined_2026-02-08_14-30-00.wav"
}
```

### Download Audio

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/v1/download/{user_id}/{asset_id}` | Download audio (defaults to combined.wav) |
| `GET` | `/api/v1/download/{user_id}/{asset_id}?filename=combined_2026-02-08_14-30-00.wav` | Download specific audio file |

Query parameters:
- `filename` (optional): Specific audio file to download. If not provided, defaults to `combined.wav`.

---

## Architecture

Hermes follows a small clean architecture layout:

- **Application**: API and CLI controllers
- **Domain**: Transaction scripts and business logic
- **Infrastructure**: Repositories for file I/O and audio processing
- **Shared**: Path utilities and helpers

### Module Structure

```
app/
├── application/
│   ├── api_controller/
│   └── cli_controller.py
├── configs/
├── domain/
│   └── transaction_scripts/
├── infrastructure/
│   └── repositories/
└── shared/
```

---

## Storage Layout

For each request, Hermes creates timestamped audio files:

```
{process_folder}/{user_id}/{asset_id}/combined_2026-02-08_14-30-00.wav
{process_folder}/{user_id}/{asset_id}/combined_2026-02-08_14-35-22.wav
...
```

Individual segment files are written in the same folder before being combined. Each request generates a new audio file with a unique timestamp, allowing multiple audios per asset. Old audio files are preserved and not deleted.

---

## Troubleshooting

### Audio Generation Issues

- Ensure `kokoro` dependencies are installed and compatible with your system
- Verify GPU/CUDA availability if running on a GPU
- Check `app/configs/config.yaml` for correct folder paths

### API Issues

- Confirm `HERMES_API_HOST` and `HERMES_API_PORT` settings
- Verify the base URL matches your client requests

---