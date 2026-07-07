# Move Note Audio — Implementation Checklist

## Design & Code
- [x] `move_asset_files()` added to `WriteAudioFilesRepository`
- [x] `MoveNoteAudioTransactionScript` created
- [x] `MoveNoteAudioTransactionScriptFactory` created
- [x] `__init__.py` exports the new module
- [x] `POST /move-asset-audio` endpoint added to `api_controller.py`

## Spec compliance
- [x] Move, not copy — `shutil.move`
- [x] Whole note, files kept separate — iterates all files, no concatenation
- [x] Rename on collision — `generate_timestamped_filename()` fallback
- [x] Path-safety — `relative_to(process_parent)` guard for both source and target
- [x] Self-move rejected — 400 on `source_asset_id == target_asset_id`
- [x] Empty/missing source → `{ moved: [], count: 0 }`
- [x] Source dir removed if empty — `rmdir()` with `OSError` catch
- [x] Async thread-pooled I/O — `asyncio.to_thread()`

## Testing
- [x] Server starts and endpoint responds
- [x] Basic move works — file relocated, source dir removed
- [x] Self-move returns 400
- [x] Empty source returns `{ moved: [], count: 0 }`
- [x] Collision rename test
- [ ] Path traversal test
- [ ] Multiple files in source test
