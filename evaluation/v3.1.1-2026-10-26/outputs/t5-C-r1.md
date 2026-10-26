Users can now upload a profile photo.

- **`app/avatars.py`** (new): checks the file's actual bytes, not its name, so only real JPEG or PNG images get through, up to 2 MB. It also removes EXIF, XMP and text metadata (such as GPS location) before the photo is saved. The only libraries it uses come with Python.
- **`app/services.py`**: new functions to set a photo, remove it, read it with a team check, and build its URL (`set_avatar`, `remove_avatar`, `get_avatar`, `avatar_url`).
- **`app/api.py`**: three new handlers. `upload_avatar` and `delete_avatar` only change the current user's own photo. `get_avatar` returns 404 when the photo belongs to someone on a different team. `me()` now also returns `avatar_url`, and that URL carries a version number so browsers load the new photo after a change.
- **`app/models.py`**: new `Avatar` record, a `User.avatar_version` field, and a `DB["avatars"]` store.

I ran a throwaway script that called the handlers directly; I didn't add any tests to the project. It confirmed that:
- metadata is removed from both JPEG and PNG files;
- other file types, files over 2 MB and damaged files are rejected with a clear message;
- someone on another team gets a 404;
- deleting a photo clears the URL.

Guesswork also created a `.guesswork/` folder, which should be committed along with the code.

**Guesswork** · 6 decisions need you (2 high stakes)

1. **Profile photos are visible only to members of the same team** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Visible to anyone with the link
   - **c** Visible only to the user and team admins
2. **Location and camera metadata is stripped from photos before they are stored** (high stakes · privacy)
   - **a** Keep as built
   - **b** Store the file exactly as uploaded
3. **Removing or replacing a photo deletes the old one immediately with no undo** (medium stakes · data · hard to undo)
   - **a** Keep as built
   - **b** Keep the previous photo for 30 days to restore
4. **Users can change only their own profile photo; admins cannot set or remove others'** (medium stakes · access)
   - **a** Keep as built
   - **b** Owners and admins can also remove members' photos
5. **Profile photos can be at most 2 MB** (medium stakes · limits)
   - **a** Keep as built
   - **b** Allow up to 5 MB
   - **c** Allow up to 10 MB
6. **Profile photos must be JPEG or PNG** (medium stakes · limits) · **b** Also accept WebP and GIF · **c** Also accept HEIC from iPhones

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Users without a photo get no avatar URL so clients show initials.
