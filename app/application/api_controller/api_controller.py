from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from app.configs.api_config import ApiConfig
from app.domain.transaction_scripts.create_audio_from_text_transaction_script import (
    CreateAudioFromTextTransactionScriptFactory,
)
from app.shared.path_utils import get_user_path_for_asset, COMBINED_WAV

config = ApiConfig()
app = FastAPI(
    title="Hermes API",
    description="Text to Speech API",
    version="1.0.0",
    root_path=config.base_url,
)

# Base directory for audio files from config
AUDIO_BASE_DIR = Path(config.audio_base_dir)


class TextToAudioRequest(BaseModel):
    text: str
    userId: str
    assetId: str


class TextToAudioResponse(BaseModel):
    file_path: str
    file_name: str


@app.post("/text-to-speech", response_model=TextToAudioResponse)
async def convert_text_to_audio(request: TextToAudioRequest):
    try:
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.host, port=config.port)
