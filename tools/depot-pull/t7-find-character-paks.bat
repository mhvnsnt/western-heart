@echo off
REM t7-find-character-paks.bat — find which TEKKEN 7 pak files hold a character's assets.
REM
REM Tekken 7's paks are SHARED numbered chunks, not per-character files, so this
REM script scans each pak's file list for the character's 3-letter code folder
REM (LAW = Marshall Law, LAR = Lars, MAR = Marduk, ...).
REM
REM USAGE:  copy this file + repak.exe into your TekkenGame\Content\Paks folder,
REM         then run:   t7-find-character-paks.bat LAW LAR
REM
REM NEEDS:  repak.exe in this same folder — free, no install:
REM         https://github.com/trumank/repak/releases  (Windows x86_64 build,
REM         unzip and copy repak.exe next to this .bat)
REM
REM Tekken 7's paks are NOT encrypted, so no key is needed.

setlocal EnableDelayedExpansion

if "%~1"=="" (
  echo Usage: %~nx0 CODE [CODE ...]
  echo Example: %~nx0 LAW LAR
  echo.
  echo Character codes: LAW = Marshall Law, LAR = Lars, MAR = Marduk.
  echo Full list: https://github.com/CDDTreborn/Tekken7_PC-Modding-Guides/wiki/Tekken-7-Basic-Modding-Information
  exit /b 1
)

where repak.exe >nul 2>nul
if errorlevel 1 (
  echo repak.exe not found in this folder.
  echo Download it from https://github.com/trumank/repak/releases
  echo ^(Windows x86_64^), unzip, and copy repak.exe next to this .bat file.
  exit /b 1
)

echo Scanning pak files for character codes: %*
echo ^(this takes a few minutes — one pass per pak file^)
echo.

for %%P in (*.pak) do (
  set "HITS="
  for %%C in (%*) do (
    repak list "%%P" 2>nul | findstr /I /C:"/%%C/" >nul
    if not errorlevel 1 set "HITS=!HITS! %%C"
  )
  if defined HITS echo %%~nxP  --!HITS!
)

echo.
echo Done. Zip ONLY the pak files listed above and upload them.
echo ^(Law + Lars are the priority — their Tekken 7 data unlocks the pull lane.^)
