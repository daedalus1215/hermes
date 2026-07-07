# Move Note Audio — Implementation Prep Notes

## What was done
- Added `move_asset_files()` method to `WriteAudioFilesRepository`
- Created `MoveNoteAudioTransactionScript` + Factory
- Added `POST /move-asset-audio` endpoint to controller
- Created test HTTP file at `move-audio-test.http`

## Test setup
To test locally, you need to:
1. Start the server: `cd app/application/api_controller && python api_controller.py`
2. Create test audio files in `../resources/hermes-process/<user_id>/<asset_id>/`
3. Use the HTTP file in VS Code REST Client or httpie

## Key decisions
- Reused `WriteAudioFilesRepository` (already has `shutil` dependency) — no new repo needed
- Used `asyncio.to_thread` for all filesystem I/O (matches existing pattern)
- Factory reuses the cached `_write_repo` from `CreateAudioFromTextTransactionScriptFactory`
- Path safety guard mirrors `delete-by-path` (resolve + relative_to + 400)
- Empty source returns `{ moved: [], count: 0 }` (idempotent)
- Self-move returns 400
- Collision: generates fresh timestamped name via `generate_timestamped_filename()`

## Edge case: partial failure
If a move fails mid-loop, earlier files are already moved. The current implementation
raises on first exception (500). This is acceptable per spec — same-disk moves rarely
fail mid-batch. If needed later, can add per-file status tracking.
