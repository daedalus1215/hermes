class MoveNoteAudioParams:
    """Input params for MoveNoteAudioTS."""

    def __init__(self, user_id: str, source_asset_id: str, target_asset_id: str):
        self.user_id = user_id
        self.source_asset_id = source_asset_id
        self.target_asset_id = target_asset_id
