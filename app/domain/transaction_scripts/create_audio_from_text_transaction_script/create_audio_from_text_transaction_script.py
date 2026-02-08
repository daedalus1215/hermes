from pathlib import Path
from app.infrastructure.repositories.write import (
    WriteAudioFilesRepository,
    CombineWavFilesRepository,
)
from app.shared.get_user_path_for_asset import get_user_path_for_asset
from app.shared.path_utils import generate_timestamped_filename


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

    async def execute(self, user_id: str, asset_id: str, text: str) -> tuple[Path, str]:
        """
        Create audio files from the given text and save them to the output folder.

        Args:
            user_id: The user's ID for folder organization
            asset_id: The asset's ID for folder organization
            text: The text to convert to audio

        Returns:
            tuple[Path, str]: A tuple containing the path to the combined audio file
                             and the filename (e.g., combined_2026-02-08_14-30-00.wav)

        Note:
            This method creates a folder structure like:
            process_folder/user_id/asset_id/
            And saves the audio with a timestamped filename.
            Existing audio files are preserved (not deleted).
        """

        try:
            # Ensure process_folder is a Path
            if not isinstance(self.process_folder, Path):
                self.process_folder = Path(self.process_folder)

            # Get the path for this user/asset
            path = get_user_path_for_asset(
                self.process_folder, str(user_id), str(asset_id)
            )

            # Ensure the path exists
            path.mkdir(parents=True, exist_ok=True)

            # Generate individual audio files
            await self.writeAudioFilesRepository.write_audio_files_repository(
                text, path
            )

            # Generate a timestamped filename for the combined audio
            timestamped_filename = generate_timestamped_filename()
            combined_path = path / timestamped_filename

            # Combine all generated files into one
            await self.combineWavFilesRepository.combine_wav_files(path, combined_path)

            return combined_path, timestamped_filename
        except Exception as e:
            print(f"Error in execute method: {str(e)}")
            print(f"Process folder type: {type(self.process_folder)}")
            print(f"Process folder value: {self.process_folder}")
            print(f"User ID type: {type(user_id)}, Asset ID type: {type(asset_id)}")
            raise
