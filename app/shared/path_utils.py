from datetime import datetime
from pathlib import Path
from typing import Union

COMBINED_WAV = "combined.wav"


def get_user_path_for_asset(
    base_path: Union[str, Path], user_id: Union[str, int], asset_id: Union[str, int]
) -> Path:
    """
    Get the path for a user's asset.

    Args:
        base_path: The base directory path
        user_id: The user ID
        asset_id: The asset ID

    Returns:
        Path: The full path to the user's asset directory
    """
    return Path(base_path) / str(user_id) / str(asset_id)


def generate_timestamped_filename() -> str:
    """
    Generate a unique filename with timestamp for audio files.

    Returns:
        str: A filename like 'combined_2026-02-08_14-30-00.wav'
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"combined_{timestamp}.wav"
