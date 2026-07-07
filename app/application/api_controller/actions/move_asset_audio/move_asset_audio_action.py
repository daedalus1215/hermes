from fastapi import APIRouter, HTTPException

from app.domain.services import MoveNoteAudioService
from .move_asset_audio_request import MoveAssetAudioRequest
from .move_asset_audio_response import MoveAssetAudioResponse, MovedFile


def create_router(service: MoveNoteAudioService) -> APIRouter:
    """Create the router for the move-asset-audio endpoint."""
    router = APIRouter()

    @router.post("/move-asset-audio", response_model=MoveAssetAudioResponse)
    async def move_asset_audio(request: MoveAssetAudioRequest):
        """
        Move all audio files from one asset (note) to another.

        - Moves all files from the source asset's folder to the target asset's folder
        - Renames files on collision (never overwrites)
        - Removes the source asset's folder if now empty
        - Returns details of all moved files
        """
        try:
            moved = await service.move_asset_audio(
                user_id=str(request.user_id),
                source_asset_id=str(request.source_asset_id),
                target_asset_id=str(request.target_asset_id),
            )
            return MoveAssetAudioResponse(
                moved=[MovedFile(**m) for m in moved],
                count=len(moved),
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
