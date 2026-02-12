import os
import asyncio
import shutil
from pathlib import Path
from typing import Union
from app.infrastructure.tts_pipeline_manager import get_tts_pipeline_manager
from app.infrastructure.buffered_audio_writer import BufferedAudioWriter


class WriteAudioFilesRepository:
    """
    Repository for writing audio files from text using TTS.

    Uses buffered streaming to process audio segments as they're generated,
    reducing peak memory usage while maintaining efficient I/O.
    """

    def __init__(self):
        self._tts_manager = get_tts_pipeline_manager()

    async def write_audio_files_repository(
        self, text: str, path: Union[str, Path]
    ) -> None:
        """
        Write text content to audio files in the specified output directory.

        Uses buffered streaming to minimize memory usage - processes segments
        as they're generated rather than loading all into memory at once.

        Args:
            text (str): Text to convert to audio
            path (Union[str, Path]): Directory to save audio files
        """
        path = Path(path)
        writer = BufferedAudioWriter(
            output_dir=path,
            buffer_threshold_bytes=1_048_576,  # 1MB buffer
            flush_interval_seconds=0.2,  # 200ms max delay
            sample_rate=24000,
        )

        try:
            # Get the singleton pipeline (loaded once, reused across requests)
            pipeline = await self._tts_manager.get_pipeline()

            # Process audio segments as they're generated (streaming)
            def generate_audio():
                return pipeline(text, voice="af_heart")

            # Run generator in thread pool
            generator = await asyncio.to_thread(generate_audio)

            # Process each segment as it becomes available
            for i, (gs, ps, audio) in enumerate(generator):
                await writer.add_segment(audio)

        except asyncio.CancelledError:
            # Handle cancellation gracefully
            await writer.cancel()
            raise
        except Exception as e:
            print(f"WriteAudioFilesRepository ERROR: {str(e)}")
            raise
        finally:
            # Final flush to ensure all segments are written
            await writer.close()

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
