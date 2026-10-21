# darkedge-config-downloads

Ready-made bot profiles for the DarkEdge **Config Downloader** (Config → Config downloader in the bot).

## How the bot downloads configs

1. The bot reads the manifest `darkedge-config-downloader-manifest.json` from the gist
   https://gist.github.com/mkyriakou3/916772de5dfd2c09e965d72f1bb8c444
   (URL in `DarkEdge/Constants/DarkEdgeConfigDownloaderConstants.cs`, logic in `Modules/ConfigDownloader/ConfigDownloaderService.cs`).
2. Each manifest entry:
   ```json
   {
     "downloadUrl": "https://github.com/mkyriakou3/darkedge-config-downloads/tree/main/<folder>",
     "groupKeys": ["<group shown in the downloader table>"],
     "version": 1
   }
   ```
3. The folder's files are downloaded (GitHub contents API, `main` branch) into the bot's profile folder as
   `configs/public/<folder>_DE`, so each folder here is one profile (the `*.json` files of `bin/configs/public/<profile>`).
4. Raising `version` shows "update available" to users who already downloaded it.
5. Optional description in the downloader: translation key `ConfigDownloader_<folder with - replaced by _>_Setup`
   (e.g. `ConfigDownloader_krist_apotheosis_Setup`) in all DarkEdge translation files.

## Publishing a profile

1. Copy the profile folder from the bot, e.g.
   `project-do-unity/bin/configs/public/krist-apotheosis` → `darkedge-config-downloads/krist-apotheosis`
   (public profile settings only; never copy anything from `configs/private`).
2. Run (needs the GitHub CLI `gh` logged in with the `gist` scope, check with `gh auth status`):
   ```bash
   python publish_config.py krist-apotheosis --group kristallon-apotheosis
   ```
   This commits and pushes the folder to `main`, then adds the entry to the gist manifest (version 1),
   or bumps the version if the entry already exists. Use `--dry-run` first to preview the new manifest,
   `--no-push` to only update the gist.

## Updating a published profile

Copy the new files over the folder, then run `python publish_config.py <folder>` again: it pushes the
changes and increases the version so users get "update available".

## Manual way (without the script)

1. `git add <folder> && git commit -m "..." && git push`
2. Edit the gist file `darkedge-config-downloader-manifest.json` on github.com, add/update the entry above, save.
