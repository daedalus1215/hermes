from pydantic import BaseModel


class MovedFile(BaseModel):
    source_path: str
    file_path: str
    file_name: str


class MoveAssetAudioResponse(BaseModel):
    moved: list[MovedFile]
    count: int
