Users can now upload a profile photo.

**What changed**
- `app/models.py`: `User` has a new `photo_id` field. A new `ProfilePhoto` record and a `DB["photos"]` store hold the image.
- `app/services.py`: `set_profile_photo`, `remove_profile_photo`, `get_profile_photo` and `profile_photo_url`.
  - The file type is worked out from the image's own bytes. Whatever type the client claims is ignored.
  - Location (GPS) data, other EXIF data and text metadata are removed before the photo is stored.
  - A new upload replaces the old photo.
- `app/api.py`:
  - `upload_profile_photo(current_user, data)` and `delete_profile_photo(current_user)` act only on the current user's own photo.
  - `profile_photo(current_user, user_id)` serves the photo with `nosniff` and private caching headers.
  - `me()` now includes `photo_url`. The URL changes on every upload, so browsers won't keep showing an old photo.

I checked it with a short script: PNG and JPEG uploads work and their metadata is removed, SVG and files over 5 MB are rejected, someone from another team gets a 404, and replacing or removing a photo leaves nothing behind. There are no tests in the repo yet, so I didn't add any.

**Not built (say if you want any of these):**
- Photos aren't resized or cropped and image dimensions aren't checked, because the app has no image library.
- Uploads have no rate limit.
- Photo changes aren't logged anywhere.
- Photos are kept in memory like the rest of the data, so they are lost on restart.

**Guesswork** · 6 decisions need you (1 high stakes)

1. **Profile photos are visible only to members of the same team** (high stakes · privacy)
   - **a** Keep as built
   - **b** Visible to anyone with the URL
   - **c** Also visible to customers
2. **Replacing or removing a photo deletes the old one immediately** (medium stakes · data · hard to undo)
   - **a** Keep as built
   - **b** Keep previous photos for 30 days to allow undo
3. **Location and other metadata are stripped from photos on upload** (medium stakes · privacy)
   - **a** Keep as built
   - **b** Keep the original file untouched
4. **Only the user can change or remove their own photo; admins cannot** (medium stakes · access)
   - **a** Keep as built
   - **b** Owners and admins can remove any member's photo
5. **Profile photo uploads are capped at 5 MB** (medium stakes · limits)
   - **a** Keep as built
   - **b** Cap at 2 MB
   - **c** Cap at 10 MB
6. **Profile photos must be JPEG or PNG** (medium stakes · limits)
   - **a** Keep as built
   - **b** Also accept WebP
   - **c** Also accept WebP and GIF

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Users without a photo get no placeholder; photo_url is null.
