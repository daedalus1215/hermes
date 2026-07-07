from pathlib import Path
from app.infrastructure.repositories.write import WriteAudioFilesRepository
from app.shared.path_utils import get_user_path_for_asset


class MoveNoteAudioTransactionScript:
    def __init__(
        self,
        writeAudioFilesRepository: WriteAudioFilesRepository,
        process_folder: str | Path,
    ):
        self.writeAudioFilesRepository = writeAudioFilesRepository
        self.process_folder = Path(process_folder)

    async def execute(
        self, user_id: str, source_asset_id: str, target_asset_id: str
    ) -> list[dict]:
        """
        Move all audio files from source asset to target asset.

        Returns list of dicts with source_path, file_path, file_name.
        Raises ValueError on self-move or path traversal.
        """
        process_folder = Path(self.process_folder)
        process_parent = process_folder.resolve().parent

        # Resolve source and target directories
        source_dir = get_user_path_for_asset(
            process_folder, str(user_id), str(source_asset_id)
        )
        target_dir = get_user_path_for_asset(
            process_folder, str(user_id), str(target_asset_id)
        )

        # Path-safety: both must resolve under process_parent
        try:
            source_dir.resolve().relative_to(process_parent)
        except ValueError:
            raise ValueError(
                f"Source path escapes allowed directory: {source_dir}"
            )

        try:
            target_dir.resolve().relative_to(process_parent)
        except ValueError:
            raise ValueError(
                f"Target path escapes allowed directory: {target_dir}"
            )

        # Reject self-move
        if source_asset_id == target_asset_id:
            raise ValueError(
                f"Cannot move audio from asset to itself: {source_asset_id}"
            )

        # Move the files
        moved = await self.writeAudioFilesRepository.move_asset_files(
            source_dir, target_dir
        )

        return moved
