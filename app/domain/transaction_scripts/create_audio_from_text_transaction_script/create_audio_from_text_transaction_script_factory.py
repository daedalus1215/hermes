from app.configs.hermes_config import HermesConfig
from app.infrastructure.repositories.write import (
    WriteAudioFilesRepository,
    CombineWavFilesRepository,
)
from .create_audio_from_text_transaction_script import (
    CreateAudioFromTextTransactionScript,
)


class CreateAudioFromTextTransactionScriptFactory:
    """
    Factory for creating transaction script instances.

    Repositories are cached as singletons to avoid recreating them on every request.
    The TTS model inside WriteAudioFilesRepository is managed by TtsPipelineManager.
    """

    config = HermesConfig()

    # Cached repository instances - created once and reused
    _write_repo: WriteAudioFilesRepository | None = None
    _combine_repo: CombineWavFilesRepository | None = None

    @classmethod
    def create(cls) -> CreateAudioFromTextTransactionScript:
        """
        Create a transaction script instance.

        Repositories are cached and reused across requests to avoid
        recreating the TTS model and other heavy resources.

        Returns:
            CreateAudioFromTextTransactionScript: Configured transaction script
        """
        process_folder = cls.config.process_folder

        # Initialize cached repositories on first call
        if cls._write_repo is None:
            cls._write_repo = WriteAudioFilesRepository()

        if cls._combine_repo is None:
            cls._combine_repo = CombineWavFilesRepository()

        script = CreateAudioFromTextTransactionScript(
            writeAudioFilesRepository=cls._write_repo,
            combineWavFilesRepository=cls._combine_repo,
            process_folder=process_folder,
        )

        return script

    @classmethod
    def reset_cache(cls) -> None:
        """
        Reset the repository cache. Useful for testing or memory management.
        """
        cls._write_repo = None
        cls._combine_repo = None
