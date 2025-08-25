from app.configs.hermes_config import HermesConfig
from app.infrastructure.repositories.write import WriteAudioFilesRepository, CombineWavFilesRepository
from .create_audio_from_text_transaction_script import CreateAudioFromTextTransactionScript


class CreateAudioFromTextTransactionScriptFactory:
    config = HermesConfig()

    @staticmethod
    def create():
        print("Creating transaction script...")
        process_folder = (
            CreateAudioFromTextTransactionScriptFactory.config.process_folder
        )
        print(f"Using process folder: {process_folder}")
        write_repo = WriteAudioFilesRepository()
        combine_repo = CombineWavFilesRepository()
        print(f"Created repositories: {write_repo.__class__.__name__}, {combine_repo.__class__.__name__}")
        
        script = CreateAudioFromTextTransactionScript(
            writeAudioFilesRepository=write_repo,
            combineWavFilesRepository=combine_repo,
            process_folder=process_folder
        )
        print(f"Created script instance: {script.__class__.__name__}")
        return script
