Demo dataset.

Use this folder as the input directory when you run `python3 main.py`:

`demo_input`

What is inside:

- `demo_input/email_archive/2026-03-12_acme_followup.eml`
- `demo_input/shared_drive/contracts/acme_audio_labs_nda.txt`
- `demo_input/shared_drive/contracts/northstar_studios_msa.md`
- `demo_input/shared_drive/contracts/riverbank_media_license.txt`
- `demo_input/shared_drive/contracts/sunrise_podcast_guest_release.txt`

Suggested demo story:

1. Show that the script can scan both an email archive and a shared drive.
2. Point out that the files have different formats, but the pipeline handles them in one pass.
3. Run the script on `demo_input`.
4. Show the destination folders that get created from AI metadata.
5. Show `document_log.json` after processing.

Second demo batch:

- `demo_input_round_2/email_archive/2026-03-18_acme_amendment.eml`
- `demo_input_round_2/shared_drive/contracts/acme_audio_labs_amendment.txt`
- `demo_input_round_2/shared_drive/contracts/jordan_lee_release_addendum.txt`
- `demo_input_round_2/shared_drive/contracts/riverbank_media_license_extension.txt`
- `demo_input_round_2/shared_drive/contracts/northstar_studios_sow.md`

Use `demo_input_round_2` on a second run to show that new files get placed into preexisting folders under `organized_documents/`.
