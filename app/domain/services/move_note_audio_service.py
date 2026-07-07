from app.domain.transaction_scripts.move_note_audio_transaction_script.move_note_audio_transaction_script import (
    MoveNoteAudioTransactionScript,
)
from app.domain.transaction_scripts.move_note_audio_transaction_script.move_note_audio_params import (
    MoveNoteAudioParams,
)


class MoveNoteAudioService:
    """Domain service for moving note audio between assets."""

    def __init__(self, ts: MoveNoteAudioTransactionScript):
        self._ts = ts

    async def move_asset_audio(
        self, user_id: str, source_asset_id: str, target_asset_id: str
    ) -> list[dict]:
        """
        Move all audio files from source asset to target asset.
        """
        params = MoveNoteAudioParams(
            user_id=user_id,
            source_asset_id=source_asset_id,
            target_asset_id=target_asset_id,
        )
        return await self._ts.apply(params)

