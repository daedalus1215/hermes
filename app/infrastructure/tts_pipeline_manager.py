"""
TTS Pipeline Manager - Singleton with TTL
Manages KPipeline instance lifecycle to avoid reloading model on every request.
"""

import asyncio
import time
from typing import Optional
from kokoro.pipeline import KPipeline


class TtsPipelineManager:
    """
    Singleton manager for TTS pipeline with TTL (time-to-live).

    The pipeline is lazily loaded on first use and stays in memory.
    After a period of inactivity (TTL), the pipeline is unloaded to free memory.
    """

    _instance: Optional["TtsPipelineManager"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls) -> "TtsPipelineManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ttl_seconds: float = 300.0, lang_code: str = "a"):
        """
        Initialize the pipeline manager.

        Args:
            ttl_seconds: Time-to-live in seconds. Pipeline unloads after this
                        period of inactivity. Default: 5 minutes.
            lang_code: Language code for the pipeline. Default: 'a' (American English)
        """
        if self._initialized:
            return

        self._ttl_seconds = ttl_seconds
        self._lang_code = lang_code
        self._pipeline: Optional[KPipeline] = None
        self._last_used: float = 0.0
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = True

    async def get_pipeline(self) -> KPipeline:
        """
        Get the TTS pipeline, loading it if necessary.

        Returns:
            KPipeline: The loaded TTS pipeline instance
        """
        async with self._lock:
            # Load pipeline if not exists
            if self._pipeline is None:
                self._pipeline = await self._load_pipeline()

            # Update last used timestamp
            self._last_used = time.time()

            # Ensure cleanup task is running
            if self._cleanup_task is None or self._cleanup_task.done():
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())

            return self._pipeline

    async def _load_pipeline(self) -> KPipeline:
        """
        Load the KPipeline in a thread pool to avoid blocking.

        Returns:
            KPipeline: Newly loaded pipeline instance
        """

        def _create():
            return KPipeline(lang_code=self._lang_code)

        return await asyncio.to_thread(_create)

    async def _cleanup_loop(self) -> None:
        """
        Background task that monitors usage and unloads pipeline after TTL.
        """
        while True:
            await asyncio.sleep(10.0)  # Check every 10 seconds

            async with self._lock:
                if self._pipeline is None:
                    return  # Already cleaned up

                idle_time = time.time() - self._last_used
                if idle_time >= self._ttl_seconds:
                    # Unload pipeline to free memory
                    self._pipeline = None
                    return  # Exit cleanup loop

    async def unload(self) -> None:
        """
        Explicitly unload the pipeline and stop cleanup task.
        """
        async with self._lock:
            self._pipeline = None
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
                self._cleanup_task = None

    @property
    def is_loaded(self) -> bool:
        """
        Check if pipeline is currently loaded.

        Returns:
            bool: True if pipeline is loaded and ready
        """
        return self._pipeline is not None

    @property
    def idle_time(self) -> float:
        """
        Get time since last use in seconds.

        Returns:
            float: Seconds since last use, or infinity if never used
        """
        if self._last_used == 0.0:
            return float("inf")
        return time.time() - self._last_used


def get_tts_pipeline_manager() -> TtsPipelineManager:
    """
    Get the singleton TTS pipeline manager instance.

    Returns:
        TtsPipelineManager: The singleton instance
    """
    return TtsPipelineManager()
