Users can now upload a profile photo.

- **`app/photos.py`** (new): checks the file type from the image bytes themselves, not from the filename or the type the browser reports. It enforces the size limit and removes embedded metadata such as EXIF/GPS, XMP, comments and PNG text chunks. Only the standard library is used, with no new dependencies.
- **`app/models.py`**: new `ProfilePhoto` dataclass and a `DB["profile_photos"]` store, keyed by user.
- **`app/services.py`**: `set_profile_photo`, `remove_profile_photo`, and `get_profile_photo`, which checks that the viewer is on the photo owner's team.
- **`app/api.py`**: three new handlers. `upload_profile_photo` always acts on the current user. `delete_profile_photo` removes their photo. `profile_photo(user_id)` returns the image bytes with `nosniff` and private caching headers, or a 404. `me()` now includes a `photo_url` field.

I ran a quick in-memory check, not a server. It covered JPEG and PNG uploads with metadata removed, rejection of GIFs, files over 2 MB and truncated files, a user from another team getting a 404, and removing a photo. All of these behaved correctly. There are no automated tests in the repo yet.

The new `.guesswork/` folder holds the decision record and should be committed with the code.

**Guesswork** · 6 decisions need you (2 high stakes)

1. **Location, camera and other metadata are removed from photos on upload** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Store the file exactly as uploaded
2. **Profile photos are visible only to members of the same team** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Visible to any signed-in user
   - **c** Public URL anyone can open
3. **Replacing or removing a photo deletes the old one immediately** (medium stakes · data · hard to undo)
   - **a** Keep as built
   - **b** Keep removed photos restorable for 30 days
4. **Users can change or remove only their own photo; admins cannot remove others'** (medium stakes · access)
   - **a** Keep as built
   - **b** Owners and admins can remove any team member's photo
5. **Profile photos can be at most 2 MB** (medium stakes · limits)
   - **a** Keep as built
   - **b** Allow up to 5 MB
   - **c** Allow up to 10 MB
6. **Profile photos must be JPEG or PNG** (medium stakes · limits) · **b** Also allow WebP and HEIC · **c** Also allow GIF

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Users without a photo get no photo URL and clients show initials.
