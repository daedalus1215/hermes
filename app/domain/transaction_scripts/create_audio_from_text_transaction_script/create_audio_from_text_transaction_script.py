from pathlib import Path
from app.infrastructure.repositories.write import (
    WriteAudioFilesRepository,
    CombineWavFilesRepository,
)
from app.shared import get_user_path_for_asset


class CreateAudioFromTextTransactionScript:

    def __init__(
        self,
        writeAudioFilesRepository: WriteAudioFilesRepository,
        combineWavFilesRepository: CombineWavFilesRepository,
        process_folder: str | Path,
    ):
        self.writeAudioFilesRepository = writeAudioFilesRepository
        self.combineWavFilesRepository = combineWavFilesRepository
        self.process_folder = Path(process_folder)

    async def execute(self, user_id: int, asset_id: int, text: str) -> Path:
        """
        Create audio files from the given text and save them to the output folder.

        Args:
            user_id: The user's ID for folder organization
            asset_id: The asset's ID for folder organization
            text: The text to convert to audio

        Returns:
            Path: The path to the combined audio file

        Note:
            This method creates a folder structure like:
            process_folder/user_id/asset_id/
            And returns the path to combined.wav within that folder
        """
        path = get_user_path_for_asset(self.process_folder, user_id, asset_id)
        path.mkdir(parents=True, exist_ok=True)

        # Delete existing files if any
        await self.writeAudioFilesRepository.delete_files_in_folder(path)

        # Generate individual audio files
        await self.writeAudioFilesRepository.write_audio_files_repository(text, path)

        # Combine all generated files into one
        combined_path = path / "combined.wav"
        await self.combineWavFilesRepository.combine_wav_files(path, combined_path)

        return combined_path
