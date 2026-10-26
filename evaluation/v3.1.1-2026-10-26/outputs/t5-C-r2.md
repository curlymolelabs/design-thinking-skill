Users can now upload a profile photo. I checked it with a quick in-memory script (no server): uploading, replacing, removing, the team visibility check, rejecting files that are the wrong type or too large, and stripping metadata all worked.

- **`app/models.py`**: `User` has a new `photo_id` field, and there is a new `Photo` record kept in `DB["photos"]`.
- **`app/services.py`**: there are three new functions:
  - `set_profile_photo` checks the real file type from the file's contents, not the name the browser sends. It enforces the size limit, strips metadata from JPEG and PNG files using only the standard library, and replaces any earlier photo.
  - `remove_profile_photo` deletes the user's photo.
  - `get_profile_photo` only returns a photo when the viewer is on the same team as its owner.
- **`app/api.py`**: there are three new handlers:
  - `upload_photo` (PUT /me/photo) returns a plain 400 message when a file is rejected.
  - `delete_photo` (DELETE /me/photo).
  - `user_photo` (GET /users/<id>/photo) returns 404 to anyone outside the photo owner's team.
  - `me()` now includes `photo_url`, which is `null` when the user has no photo.

The decisions I made are recorded in the new `.guesswork/` folder, which should be committed with the code.

**Guesswork** · 6 decisions need you (1 high stakes)

1. **Profile photos are visible only to members of the same team** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Visible to anyone with the link
   - **c** Visible to the user and admins only
2. **Replacing or removing a photo deletes the old photo immediately, with no undo** (medium stakes · data · hard to undo)
   - **a** Keep as built
   - **b** Keep the previous photo restorable for 30 days
3. **Location and other EXIF/text metadata are stripped from uploaded photos** (medium stakes · privacy)
   - **a** Keep as built
   - **b** Store photos exactly as uploaded
4. **Only users can change or remove their own photo; admins cannot remove members' photos** (medium stakes · access)
   - **a** Keep as built
   - **b** Owners and admins can remove any member's photo
5. **Photos are stored and served at the uploaded size, not resized or cropped** (medium stakes · performance)
   - **a** Keep as built
   - **b** Resize to 512x512 square on upload (adds Pillow)
6. **Profile photos can be at most 2 MB** (medium stakes · limits) · **b** Allow up to 5 MB · **c** Allow up to 10 MB

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Profile photos must be JPEG or PNG.
