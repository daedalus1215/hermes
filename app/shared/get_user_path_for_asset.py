from pathlib import Path

COMBINED_WAV = 'combined.wav'

def get_user_path_for_asset(folder: str, user_id: int, asset_id: int) -> Path:
    return folder / str(user_id) / str(asset_id)
