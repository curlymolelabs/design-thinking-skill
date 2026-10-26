Users can now upload a profile photo. I checked it with a quick script: uploading, replacing, removing, a teammate viewing it, someone from another team getting a 404, a GIF being rejected, a file over 2 MB being rejected, and location data being stripped all behaved as expected. There are no test files in the project, and I didn't run a server.

**How it works**
- **Upload:** a user uploads a photo for themselves only (`PUT /me/photo`). Each user has one photo, and uploading a new one replaces the old one. Removing it is `DELETE /me/photo`.
- **Checks:** the app checks the file contents, not the file name, to confirm it's a JPEG or PNG. Files over 2 MB are rejected with a clear error.
- **Privacy:** location (GPS) and other hidden text data are removed from the photo before it's saved. Phone photos often carry where they were taken.
- **Viewing:** the photo is served at `/users/<id>/photo`, and only members of the same team can see it. Everyone else gets "not found."
- **Profile response:** `GET /me` now includes `photo_url`, which is empty when there's no photo. The address changes whenever the photo changes, so browsers don't keep showing the old one.

The changes are in `app/models.py`, `app/services.py` and `app/api.py`.

**Not built yet:**
- Photos aren't resized or cropped, so a large image is stored and sent at full size. This needs an image library such as Pillow.
- Photos are kept in memory with the rest of the data, so they're lost on restart. They'll need real file storage before launch.
- There's no limit on how often someone can upload, and no record of who changed a photo or when.

I made the choices below without you. They're recorded in a new `.guesswork/` folder, which should be committed with the code.

**Guesswork** · 5 decisions need you (2 high stakes)

1. **Location and other EXIF/text metadata are stripped from photos on upload** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Store the file exactly as uploaded
2. **Profile photos are visible only to members of the same team** (high stakes · privacy)
   - **a** Keep as built
   - **b** Visible to any signed-in user
   - **c** Public URL anyone can open
3. **Replacing or removing a photo deletes the old image immediately** (medium stakes · data · hard to undo)
   - **a** Keep as built
   - **b** Keep the previous photo for 30 days
4. **Only users can change or remove their own photo; admins cannot** (medium stakes · access)
   - **a** Keep as built
   - **b** Owners and admins can remove a member's photo
5. **Photos must be JPEG or PNG and at most 2 MB** (medium stakes · limits)
   - **a** Keep as built
   - **b** Also accept WebP and GIF
   - **c** Allow up to 5 MB
   - **d** Allow up to 10 MB and resize

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
