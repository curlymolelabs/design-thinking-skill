Users can now upload a profile photo. I checked it with a quick script against the in-memory store (no server). Valid uploads, rejected uploads, replacing and removing a photo, and the team-only visibility all behaved as expected. Nothing is committed yet.

**What changed**
- `app/models.py`: users have a new `avatar_id` field. Photos are stored as `Avatar` records in a new `DB["avatars"]` table.
- `app/services.py`: added functions to set, remove and get a photo, and to build its URL. Uploads are checked here.
- `app/api.py`: three new handlers, and `me()` now returns `avatar_url`:
  - `upload_avatar(current_user, file_bytes)` (POST `/me/avatar`) returns `{"avatar_url": ...}`, or `{"status": 400, "error": ...}` if the upload is rejected.
  - `delete_avatar(current_user)` (DELETE `/me/avatar`).
  - `avatar(current_user, avatar_id)` (GET `/avatars/<id>`) returns the image bytes, content type and headers.

**Choices I made (easy to change)**
- **Only your own photo:** the upload and delete handlers act on the current user and take no user ID, so nobody can change someone else's photo.
- **Formats and size:** PNG, JPEG, WebP and GIF, up to 2 MB. The format is worked out from the file's own bytes, not from the file name or the type the browser reports.
- **No SVG:** SVG files can contain scripts that would run when the image is viewed.
- **Who can see a photo:** only members of the same team. Anyone else gets a 404, as if the photo didn't exist.
- **New URL on every upload:** each upload gets a fresh random URL and the old photo is deleted. Browsers can cache images indefinitely and still pick up a changed photo straight away.

**Worth knowing**
- **Images aren't resized or re-encoded.** A 2 MB photo is served at 2 MB, and any embedded metadata stays in, including the GPS location some phones add. If that matters, the next step is to add Pillow and re-save each upload as a fixed-size image, which also strips the metadata.
- **Photos are kept in memory, like the rest of the data.** For production they should move to disk or object storage such as S3.
- **The handlers still need connecting to your routing.** The HTTP methods and paths in the docstrings (like POST `/me/avatar`) are suggestions, since the app has no routing layer yet.
- **There's no upload screen or client code yet,** only these handlers.
