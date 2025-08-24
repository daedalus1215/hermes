import os
import asyncio
import shutil
from pathlib import Path
from typing import Union
from kokoro import KPipeline
import soundfile as sf


class WriteAudioFilesRepository:
    def __init__(self):
        self._pipeline = KPipeline(lang_code="a")

    async def write_audio_files_repository(self, text: str, path: Union[str, Path]) -> None:
        """
        Write text content to audio files in the specified output directory.

        Args:
            text (str): Text to convert to audio
            path (Union[str, Path]): Directory to save audio files
        """
        path = Path(path)
        
        # Convert synchronous generator to async operation
        def run_pipeline():
            return list(self._pipeline(text, voice="af_heart"))
            
        # Run the pipeline in a thread pool to avoid blocking
        results = await asyncio.to_thread(run_pipeline)
        
        # Save files
        for i, (gs, ps, audio) in enumerate(results):
            # Write the file in a thread pool since it's I/O bound
            await asyncio.to_thread(
                sf.write,
                path / f"{i}.wav",
                audio,
                24000
            )

    async def delete_files_in_folder(self, path: Union[str, Path]) -> None:
        """
        Delete all files in the specified folder.
        
        Args:
            path (Union[str, Path]): Directory to clean up and recreate
        """
        path = Path(path)
        if path.exists():
            await asyncio.to_thread(shutil.rmtree, path)
        await asyncio.to_thread(os.makedirs, path)
