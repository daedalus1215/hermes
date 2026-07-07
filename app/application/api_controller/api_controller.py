import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from app.configs.api_config import ApiConfig
from app.domain.transaction_scripts.create_audio_from_text_transaction_script import (
    CreateAudioFromTextTransactionScriptFactory,
)
from app.domain.transaction_scripts.move_note_audio_transaction_script import (
    MoveNoteAudioTransactionScriptFactory,
)
from app.shared.path_utils import get_user_path_for_asset, COMBINED_WAV
from app.infrastructure.tts_pipeline_manager import get_tts_pipeline_manager
from app.infrastructure.monitoring_middleware import PerformanceMonitoringMiddleware

config = ApiConfig()
app = FastAPI(
    title="Hermes API",
    description="Text to Speech API",
    version="1.0.0",
    root_path=config.base_url,
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMonitoringMiddleware)

# Base directory for audio files from config
AUDIO_BASE_DIR = Path(config.audio_base_dir)

# Semaphore to limit TTS processing to 1 concurrent request
# This prevents GPU/CPU contention and ensures sequential processing
_tts_semaphore = asyncio.Semaphore(1)


class TextToAudioRequest(BaseModel):
    text: str
    userId: str
    assetId: str


class TextToAudioResponse(BaseModel):
    file_path: str
    file_name: str


class MoveAssetAudioRequest(BaseModel):
    user_id: str
    source_asset_id: str
    target_asset_id: str


class MovedFile(BaseModel):
    source_path: str
    file_path: str
    file_name: str


class MoveAssetAudioResponse(BaseModel):
    moved: list[MovedFile]
    count: int


@app.post("/text-to-speech", response_model=TextToAudioResponse)
async def convert_text_to_audio(request: TextToAudioRequest):
    """
    Convert text to speech audio.

    Requests are processed sequentially to avoid GPU/CPU contention.
    Additional requests will queue and wait for the current one to complete.
    """
    try:
        # Acquire semaphore to ensure sequential processing
        async with _tts_semaphore:
            script = CreateAudioFromTextTransactionScriptFactory().create()
            output_path, file_name = await script.execute(
                user_id=str(request.userId),
                asset_id=str(request.assetId),
                text=str(request.text),
            )
            absolute_path = output_path.resolve()
            return TextToAudioResponse(
                file_path=str(absolute_path),
                file_name=file_name,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{user_id}/{asset_id}")
async def download_audio(
    user_id: str,
    asset_id: str,
    filename: str = Query(
        None,
        description="Optional specific filename to download. Defaults to combined.wav if not provided.",
    ),
):
    # Get the process folder from config
    process_folder = CreateAudioFromTextTransactionScriptFactory.config.process_folder
    # Construct the path to the audio file
    asset_path = get_user_path_for_asset(process_folder, user_id, asset_id)

    # Use the provided filename or default to combined.wav for backward compatibility
    if filename:
        file_path = asset_path / filename
    else:
        file_path = asset_path / COMBINED_WAV

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=str(file_path), media_type="audio/wav", filename=file_path.name
    )


@app.get("/download-by-path")
async def download_audio_by_path(
    file_path: str = Query(
        ...,
        description="Absolute path to the audio file. Must be within the process folder parent directory.",
    ),
):
    process_folder = CreateAudioFromTextTransactionScriptFactory.config.process_folder
    process_parent = Path(process_folder).resolve().parent
    requested_path = Path(file_path).resolve()
    try:
        requested_path.relative_to(process_parent)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not requested_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        path=str(requested_path),
        media_type="audio/wav",
        filename=requested_path.name,
    )


@app.delete("/delete-by-path")
async def delete_audio_by_path(
    file_path: str = Query(
        ...,
        description="Absolute path to the audio file to delete. Must be within the process folder parent directory.",
    ),
):
    """Delete an audio file by its absolute path."""
    process_folder = CreateAudioFromTextTransactionScriptFactory.config.process_folder
    process_parent = Path(process_folder).resolve().parent
    requested_path = Path(file_path).resolve()
    try:
        requested_path.relative_to(process_parent)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not requested_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    requested_path.unlink()
    parent_dir = requested_path.parent
    try:
        if parent_dir != process_parent and not any(parent_dir.iterdir()):
            parent_dir.rmdir()
    except OSError:
        pass
    return {"detail": "Audio file deleted successfully"}


@app.post("/move-asset-audio", response_model=MoveAssetAudioResponse)
async def move_asset_audio(request: MoveAssetAudioRequest):
    """
    Move all audio files from one asset (note) to another.

    - Moves all files from the source asset's folder to the target asset's folder
    - Renames files on collision (never overwrites)
    - Removes the source asset's folder if now empty
    - Returns details of all moved files
    """
    try:
        script = MoveNoteAudioTransactionScriptFactory().create()
        moved = await script.execute(
            user_id=str(request.user_id),
            source_asset_id=str(request.source_asset_id),
            target_asset_id=str(request.target_asset_id),
        )
        return MoveAssetAudioResponse(
            moved=[MovedFile(**m) for m in moved],
            count=len(moved),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health check endpoint that reports system status.

    Returns:
        JSON with health status, TTS model status, and queue information.
    """
    from app.infrastructure.monitoring_middleware import get_current_memory_usage

    tts_manager = get_tts_pipeline_manager()
    memory_stats = get_current_memory_usage()

    return {
        "status": "healthy",
        "tts_model": {
            "loaded": tts_manager.is_loaded,
            "idle_time_seconds": tts_manager.idle_time
            if tts_manager.is_loaded
            else None,
        },
        "queue": {
            "concurrent_limit": 1,
            "current_waiters": _tts_semaphore._value,
        },
        "memory": memory_stats,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.host, port=config.port)
