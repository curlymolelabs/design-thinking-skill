I added profile photo uploads. Users can upload, replace or remove their own photo, and teammates can see it. I tested it with a quick script that called the handlers directly. I didn't run a server, since you asked me not to.

**What's new**
- `app/api.py`:
  - `upload_profile_photo(current_user, file_bytes)` (POST `/me/photo`)
  - `delete_profile_photo(current_user)` (DELETE `/me/photo`)
  - `profile_photo(current_user, user_id)` (GET `/users/<id>/photo`), which returns the image bytes and headers
  - `me()` now includes a `photo_url`. It is `None` if the user has no photo.
- `app/services.py`: functions to set, remove and fetch a photo and to build its URL. The validation lives here too.
- `app/models.py`: a new `ProfilePhoto` model, a `photo_id` field on `User`, and a new `DB["photos"]` store. Photos are kept in memory like everything else in the app.

**Choices I made**
- **Who can do what:** the upload and delete handlers have no user parameter, so users can only change their own photo. Only members of the same team can view a photo; anyone else gets a 404.
- **Accepted files:** PNG, JPEG and WebP, up to 2 MB. The app checks the file's actual bytes to work out the type and ignores the filename and the type the browser reports. SVG is rejected because it can contain scripts that would run on our domain. The image is served with `X-Content-Type-Options: nosniff`, which stops browsers from guessing a different file type.
- **Replacing a photo:** each upload gets a new random ID that is also part of the URL, so browsers don't keep showing the old image after a change. The old photo is deleted.

**Worth knowing**
- **Location data in photos:** I don't strip EXIF metadata. Phone photos often include GPS location, which teammates could read from the original file. Fixing this properly means re-encoding the image with a library like Pillow. I'd add that before launch if users will upload photos straight from their phones.
- **Storage:** because photos are stored in memory with the rest of the app's data, they disappear on restart. When you move to a real database, they should go to file or object storage (for example S3) rather than into database rows.
- **Wiring up:** the new handlers aren't connected to any router yet, because the app doesn't have one. The routes listed above are the paths I'd suggest.
