from app.configs.hermes_config import HermesConfig
from app.infrastructure.repositories.write import WriteAudioFilesRepository, CombineWavFilesRepository
from .create_audio_from_text_transaction_script import CreateAudioFromTextTransactionScript


class CreateAudioFromTextTransactionScriptFactory:
    config = HermesConfig()

    @staticmethod
    def create():
        process_folder = (
            CreateAudioFromTextTransactionScriptFactory.config.process_folder
        )
        write_repo = WriteAudioFilesRepository()
        combine_repo = CombineWavFilesRepository()
        
        script = CreateAudioFromTextTransactionScript(
            writeAudioFilesRepository=write_repo,
            combineWavFilesRepository=combine_repo,
            process_folder=process_folder
        )

        return script
