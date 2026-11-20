# Getting your Tekken 7 files to the crew — 5 steps

You own Tekken 7 on Steam, so the files come from YOUR computer. We never see
or touch your Steam login — your password only gets typed into Steam's own
login box on your machine, never sent to us. Pick the path that fits you.

## Path A — Tekken 7 is already installed (fastest)

1. Open your Tekken 7 folder: in Steam, right-click TEKKEN 7 → Manage →
   Browse local files, then open `TekkenGame`, then `Content`, then `Paks`.
2. Get two small free files into that Paks folder: (a) `repak.exe` from
   https://github.com/trumank/repak/releases (Windows download, unzip it,
   copy out `repak.exe` — no install needed); (b) `t7-find-character-paks.bat`
   (we send you this file).
3. Double-click the `.bat` file — or in that folder's address bar type `cmd`,
   then run `t7-find-character-paks.bat LAW LAR`. It prints the few pak files
   that actually contain Law and Lars (takes a few minutes).
4. Zip just those pak files.
5. Upload the zip to the link we give you. Done — the crew takes it from there.

## Path B — Tekken 7 is NOT installed

1. Download DepotDownloader (free) from
   https://github.com/SteamRE/DepotDownloader/releases and unzip it anywhere.
2. We send you a small file called `t7-full-roster.txt` — put it in the same
   folder. Then open a terminal there and run:
   `DepotDownloader -app 389730 -depot 389731 -filelist t7-full-roster.txt -dir ./t7paks -username YOUR_STEAM_NAME`
   (replace YOUR_STEAM_NAME with your Steam username).
3. It will ask for YOUR Steam password, and maybe a Steam Guard code from your
   phone/email — type them on YOUR computer. We never see them.
4. When it finishes, zip the `t7paks` folder.
5. Upload the zip to the link we give you. Done.

## Good to know

- **Law and Lars first.** Their Tekken 7 models/animations/movesets unlock the
  active pull lane — if you only upload a few paks, make it theirs.
- Never paste your Steam password into chat, email, or any website for us —
  it only belongs in the Steam login prompt on your own PC.
- If the upload link caps file size, split the zip first (in 7-Zip:
  right-click → 7-Zip → "Add to archive" → "Split to volumes") and upload the
  parts; we reassemble them.
