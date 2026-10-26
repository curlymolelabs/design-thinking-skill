Users can now upload a profile photo. I ran a quick script against the new code in memory, without a server. Uploading and replacing work, a user on another team can't see the photo, removing it works, and wrong file types and oversized files are turned away. Location data is removed from both JPEGs and PNGs.

**What I added**
- `app/api.py` has three new handlers:
  - `upload_avatar` (PUT `/me/avatar`, raw image bytes as the body)
  - `delete_avatar` (DELETE `/me/avatar`)
  - `avatar` (GET `/users/<id>/avatar`)
- `me()` now returns `avatar_url`. It is null when the user has no photo, so the front end can show initials.
- `app/services.py` does the checks and storage. It works out the file type from the file itself, not from what the browser claims. It accepts JPEG and PNG up to 2 MB, and removes metadata such as GPS location before saving.
- `app/models.py` has a new `Avatar` record and an `avatars` table in the in-memory store.
- The photo URL changes with each upload, so browsers can cache it but still pick up a new photo.

**Not built yet** (say if you want any of these):
- **Front end:** there are no front-end changes.
- **Resizing:** photos aren't resized, so a 2 MB image is sent at full size wherever it's shown.
- **Upload limits:** there's no cap on how often someone can upload.
- **Change history:** nothing records who changed a photo or when.
- **Lost on restart:** photos live in memory like the rest of the data, so a restart erases them.

I also created a `.guesswork/` folder that records these decisions; commit it with the code.

**Guesswork** · 5 decisions need you (2 high stakes)

1. **Location and camera metadata (EXIF, GPS, text chunks) is removed from uploaded photos** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Store the file exactly as uploaded
2. **Profile photos are visible only to members of the same team** (high stakes · privacy)
   - **a** Keep as built
   - **b** Visible to anyone with the link
   - **c** Visible to customers too
3. **Uploading a new photo or removing it deletes the old one immediately with no undo** (medium stakes · data · hard to undo)
   - **a** Keep as built
   - **b** Keep the previous photo for 30 days
4. **Only the user can change or remove their own photo; admins and owners cannot** (medium stakes · access)
   - **a** Keep as built
   - **b** Admins and owners can also remove members' photos
5. **Profile photos must be JPEG or PNG and 2 MB or smaller** (medium stakes · limits)
   - **a** Keep as built
   - **b** Also accept WebP and GIF
   - **c** Raise the limit to 5 MB

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Photos are stored as-is without resizing or cropping; Users without a photo get avatar_url null so clients show initials.
