"""
Buffered Audio Writer

Implements buffered streaming for TTS audio generation.
Accumulates audio segments in memory and writes to disk in batches
to balance memory usage and I/O efficiency.
"""

import asyncio
import time
from pathlib import Path
from typing import List, Tuple, Any
import numpy as np
import soundfile as sf


class BufferedAudioWriter:
    """
    Buffered writer for audio segments.

    Accumulates audio segments in memory up to a threshold,
    then writes them to disk. Also flushes on a timer to
    ensure timely writes.

    Args:
        output_dir: Directory to write audio files
        buffer_threshold_bytes: Buffer size threshold (default: 1MB)
        flush_interval_seconds: Timer-based flush interval (default: 0.2s)
        sample_rate: Audio sample rate (default: 24000)
    """

    def __init__(
        self,
        output_dir: Path,
        buffer_threshold_bytes: int = 1_048_576,  # 1MB
        flush_interval_seconds: float = 0.2,
        sample_rate: int = 24000,
    ):
        self._output_dir = output_dir
        self._buffer_threshold = buffer_threshold_bytes
        self._flush_interval = flush_interval_seconds
        self._sample_rate = sample_rate

        self._buffer: List[Tuple[int, np.ndarray]] = []
        self._buffer_size = 0
        self._last_flush_time = time.time()
        self._segment_counter = 0
        self._is_cancelled = False
        self._write_lock = asyncio.Lock()

    def _get_audio_size_bytes(self, audio: np.ndarray) -> int:
        """Calculate size of audio array in bytes."""
        return audio.nbytes

    async def add_segment(self, audio: np.ndarray) -> None:
        """
        Add an audio segment to the buffer.

        Args:
            audio: Audio data as numpy array
        """
        if self._is_cancelled:
            return

        segment_size = self._get_audio_size_bytes(audio)

        async with self._write_lock:
            # Check if we should flush before adding
            should_flush = (
                self._buffer_size + segment_size >= self._buffer_threshold
                or (time.time() - self._last_flush_time) >= self._flush_interval
            )

            if should_flush and self._buffer:
                await self._flush_buffer()

            # Add segment to buffer
            self._buffer.append((self._segment_counter, audio))
            self._buffer_size += segment_size
            self._segment_counter += 1

    async def _flush_buffer(self) -> None:
        """Flush all buffered segments to disk."""
        if not self._buffer:
            return

        segments_to_write = self._buffer.copy()
        self._buffer = []
        self._buffer_size = 0
        self._last_flush_time = time.time()

        # Write segments in thread pool to avoid blocking
        def _write_segments():
            for segment_id, audio in segments_to_write:
                output_path = self._output_dir / f"{segment_id}.wav"
                sf.write(output_path, audio, self._sample_rate)

        await asyncio.to_thread(_write_segments)

    async def close(self) -> int:
        """
        Final flush and cleanup.

        Returns:
            int: Total number of segments written
        """
        async with self._write_lock:
            await self._flush_buffer()
            return self._segment_counter

    async def cancel(self) -> None:
        """
        Cancel writing and discard any buffered data.
        """
        self._is_cancelled = True
        async with self._write_lock:
            self._buffer = []
            self._buffer_size = 0
