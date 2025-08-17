from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from kokoro import KPipeline
import soundfile as sf
import os

app = FastAPI()

# Base directory for audio files
AUDIO_BASE_DIR = Path("generated_audio")

class TextToAudioRequest(BaseModel):
    text: str
    userId: str
    assetId: str

class TextToAudioResponse(BaseModel):
    file_path: str

@app.post("/text-to-speech", response_model=TextToAudioResponse)
async def convert_text_to_audio(request: TextToAudioRequest):
    try:
        # Create folder structure
        user_dir = AUDIO_BASE_DIR / request.userId
        asset_dir = user_dir / request.assetId
        asset_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the pipeline
        pipeline = KPipeline(lang_code='a')
        
        # Generate audio
        output_file = asset_dir / "audio.wav"
        generator = pipeline(request.text, voice='af_heart')
        
        # We'll take the first generated audio segment
        for i, (gs, ps, audio) in enumerate(generator):
            if i == 0:  # Only save the first segment
                sf.write(str(output_file), audio, 24000)
                break

        return TextToAudioResponse(file_path=str(output_file))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)