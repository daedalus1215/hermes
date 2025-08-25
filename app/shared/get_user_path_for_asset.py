from pathlib import Path

COMBINED_WAV = 'combined.wav'

def get_user_path_for_asset(folder: str | Path, user_id: str, asset_id: str) -> Path:
    print(f"Getting path for user {user_id} and asset {asset_id} in folder {folder}")
    base_path = Path(folder)  # Convert to Path if it's a string
    return base_path / str(user_id) / str(asset_id)