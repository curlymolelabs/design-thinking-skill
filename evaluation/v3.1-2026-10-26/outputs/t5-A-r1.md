Users can now upload a profile photo. Each person can change only their own photo, and only people on their team can see it.

**What I added**
- **Upload:** `api.upload_avatar(current_user, file_bytes)` (meant for `PUT /me/avatar`). It accepts PNG or JPEG files up to 2 MB and returns the photo's URL. A wrong type, an oversized file or a corrupt file gets a 400 with a message the user can read.
- **Remove:** `api.delete_avatar(current_user)` (`DELETE /me/avatar`).
- **View:** `api.avatar(current_user, user_id)` (`GET /users/<id>/avatar`) returns the image bytes and their type. Someone from another team gets the same 404 as for a user who doesn't exist, so the endpoint can't be used to find out who is on other teams.
- **`me()`** now includes `avatar_url`. It's `None` when there's no photo, otherwise something like `/users/1/avatar?v=3`. The `?v=` number changes with each upload, so browsers can cache the photo for a long time and still show a new one straight away.

**Choices I made without checking with you**
- **The file type comes from the file's contents,** not from its name or what the browser says it is. Only PNG and JPEG get through. SVG is blocked on purpose because it can carry scripts. Responses also send `nosniff`.
- **Hidden photo details are removed before saving.** Phone photos often contain the GPS location where they were taken, and other teammates would see these photos. I strip the EXIF, XMP and comment data from JPEGs and the EXIF and text data from PNGs. One side effect: a phone photo with a rotation tag in that data may show up sideways. If that's a problem, the fix is to add Pillow and re-encode each photo, which also lets us resize it.
- **Photos are kept in memory** in a new `DB["avatars"]` table, like the rest of the app's data. In production you'd want object storage such as S3; only `set_avatar`, `get_avatar` and `remove_avatar` would need to change.
- **There's no resizing or cropping,** because that would need an image library. The 2 MB limit keeps file sizes reasonable for now.
- **Admins and owners can't change other people's photos.** Tell me if they should be able to.

**Files changed:** `app/models.py` (a new `User.avatar_version` field and an `Avatar` record), `app/services.py` (checking, stripping, saving and URL logic) and `app/api.py` (the three new handlers and `me()`). I didn't start a server. I ran a quick throwaway script against the handlers: a valid upload, a viewer from another team, SVG and oversized files, a corrupt JPEG, metadata removal and photo removal all behaved as expected. There's no test suite in the repo, so I didn't add one. Nothing is committed.
