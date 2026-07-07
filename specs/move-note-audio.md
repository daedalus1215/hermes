# Spec — Move a Note's Audio Between Assets

**Status:** Draft — requirements captured, ready to implement
**Repo:** Hermes (this project)
**Driven by:** Chronus "merge notes" — a future merge version (v2/v3) needs to **carry a
note's audio over to the merge target** instead of deleting it.
**Author:** daedalus1215 + Claude

---

## Why

Chronus stores audio metadata (one row per file) and points at Hermes files by path; the
bytes live here on disk. When Chronus merges note B into note A, B's audio must travel to A.
Today Hermes can create, download, and **delete** audio, but it **cannot move** a file from
one note's folder to another's — so the current merge plan deletes B's audio. This spec adds
the missing **move** capability so a later merge can preserve audio.

> Chronus is intentionally out of scope here. A separate **Chronus tie-in spec** will be
> written later to consume this endpoint (update each `note_audios` row's `note_id` +
> `file_path` from the move result). Not part of this spec.

## Decisions (from requirements pass)

- **Move, not copy.** The source note's folder gives the file up; no duplication.
  (Copy was considered for un-merge/restore friendliness but rejected for now — noted as a
  possible v-next if restore ever needs it.)
- **Whole note, files kept separate.** A note can have **many** audio files. The move
  relocates **all** of a note's files and keeps them as distinct files at the destination —
  it does **not** concatenate or combine them.
- **Rename on collision, never overwrite.** If the destination already has a file of the same
  name, generate a fresh timestamped name; existing audio is never clobbered.

## Hermes as-is (context for the implementer)

- **Storage layout:** `{audio_base_dir}/{user_id}/{asset_id}/{filename}` where `asset_id` is
  the Chronus note id and filenames are timestamped (`combined_YYYY-MM-DD_HH-MM-SS.wav`).
  See `app/shared/path_utils.py` (`get_user_path_for_asset`, `generate_timestamped_filename`,
  `COMBINED_WAV`).
- **Existing endpoints** (`app/application/api_controller/api_controller.py`):
  `POST /text-to-speech`, `GET /download/{user_id}/{asset_id}`, `GET /download-by-path`,
  `DELETE /delete-by-path`, `GET /health`. **No move/copy.**
- **Path-safety pattern to reuse:** each path endpoint does
  `requested_path.resolve().relative_to(process_parent)` and 400s on `ValueError`. The move
  must apply this to **both** source and destination dirs.
- **Empty-dir cleanup pattern to reuse:** `delete-by-path` removes the parent dir when it
  becomes empty (`rmdir` guarded by `iterdir()`), swallowing `OSError`.
- **Architecture:** controller route → `*TransactionScript` (+ `*Factory`) → write repository
  under `app/infrastructure/repositories/write/`. `shutil` is already used
  (`write_audio_files_repository.py`), so `shutil.move` is the tool.

## Proposed endpoint

```
POST /move-asset-audio
body: {
  user_id: str,
  source_asset_id: str,
  target_asset_id: str
}
→ 200 {
  moved: [ { source_path: str, file_path: str, file_name: str } ],   # file_path = new absolute path
  count: int
}
```

Single `user_id` because merge is always same-user (source and target notes share the owner).
If a cross-user move is ever needed, add `target_user_id` later.

### Behavior
1. Resolve `source_dir = get_user_path_for_asset(process_folder, user_id, source_asset_id)`
   and `target_dir = ... target_asset_id`. Assert both resolve under `process_parent`
   (reuse the existing guard); 400 on violation.
2. Reject `source_asset_id == target_asset_id` with 400 (nonsensical self-move).
3. If `source_dir` is missing or empty → return `{ moved: [], count: 0 }` (idempotent
   success — nothing to move is not an error; merge flows and retries stay clean).
4. `os.makedirs(target_dir, exist_ok=True)`.
5. For each file in `source_dir`:
   - Destination name = the file's name, unless `target_dir/<name>` already exists → use
     `generate_timestamped_filename()` (never overwrite).
   - `shutil.move(src_file, target_dir/<final_name>)` (run via `asyncio.to_thread` to match
     the async, thread-pooled I/O style).
   - Record `{ source_path, file_path: <new abs path>, file_name: <final_name> }`.
6. Remove `source_dir` if now empty (mirror `delete-by-path` cleanup, swallow `OSError`).
7. Return the collected list + count.

### Implementation shape (match existing conventions)
- Controller route in `app/application/api_controller/api_controller.py`.
- `MoveNoteAudioTransactionScript` (+ `MoveNoteAudioTransactionScriptFactory`) under
  `app/domain/transaction_scripts/move_note_audio_transaction_script/`.
- A write-repo method, e.g. `move_asset_files(source_dir, target_dir) -> list[dict]` on a
  repository under `app/infrastructure/repositories/write/`.

## Edge cases
- **Source folder missing/empty:** success with empty result (see step 3).
- **Self-move (`source == target`):** 400.
- **Collision:** rename, never overwrite (timestamped).
- **Partial failure mid-loop:** filesystem moves aren't a transaction. If a later file fails
  after earlier ones moved, the earlier ones stay moved. Return a 500 but include what was
  already moved so the caller can reconcile — OR (implementer's call) attempt best-effort and
  report per-file status. Flag for review; low risk since same-disk moves rarely fail
  mid-batch.
- **Same-disk assumption:** `shutil.move` is a cheap rename within one filesystem; if
  `audio_base_dir` ever spans mounts, moves become copy+unlink (slower) but still correct.

## Auth
Parity with existing endpoints — Hermes is an internal, unauthenticated service and Chronus
is the only caller. No new auth in this spec (revisit if/when Hermes adds an auth layer for
its mutating endpoints, which would also cover `delete-by-path`).

## Tests (establish pytest location — `__specs__/` is currently empty)
- Moves every file from source→target folder; returns new paths; source folder removed.
- Multiple files in a note all move and remain distinct at the destination.
- Collision at destination → renamed, existing file untouched.
- Missing/empty source → `{ moved: [], count: 0 }`.
- Self-move → 400. Path outside `process_parent` (source or target) → 400.

## Follow-ups / linked specs
- **Chronus tie-in (future):** consume `POST /move-asset-audio` in the merge flow to move
  source audios to the target note and update `note_audios` rows. To be specced Chronus-side.
- The Chronus repo has a companion note at `chronus-react-nestjs/specs/hermes-audio-move.md`
  (earlier draft covering the Chronus-consumption angle); this Hermes-repo spec is the
  authoritative description of the endpoint.
