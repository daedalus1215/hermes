from pydantic import BaseModel


class MoveAssetAudioRequest(BaseModel):
    user_id: str
    source_asset_id: str
    target_asset_id: str
