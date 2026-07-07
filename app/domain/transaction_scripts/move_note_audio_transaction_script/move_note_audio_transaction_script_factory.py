from app.configs.hermes_config import HermesConfig
from app.infrastructure.repositories.write import WriteAudioFilesRepository
from .move_note_audio_transaction_script import MoveNoteAudioTransactionScript


class MoveNoteAudioTransactionScriptFactory:
    config = HermesConfig()

    @classmethod
    def create(cls) -> MoveNoteAudioTransactionScript:
        from app.domain.transaction_scripts.create_audio_from_text_transaction_script.create_audio_from_text_transaction_script_factory import (
            CreateAudioFromTextTransactionScriptFactory,
        )

        process_folder = cls.config.process_folder

        # Reuse the cached write repo from the existing factory
        write_repo = CreateAudioFromTextTransactionScriptFactory._write_repo
        if write_repo is None:
            write_repo = WriteAudioFilesRepository()

        return MoveNoteAudioTransactionScript(
            writeAudioFilesRepository=write_repo,
            process_folder=process_folder,
        )
