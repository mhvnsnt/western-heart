# VPW2 sequences → MIDI

All 19 VPW2 `.sng` sequences converted to Standard MIDI Files with
`tools/vpw2_sng2midi.py`, a faithful Python port of the "Binary Sng"
path in SubDrag's N64 Soundbank Tool / N64MidiTool
(jombo23/N64-Tools, Unlicense):
`CMidiParse::SngToMidi` (Binary Sng branch) +
`ParseSngTrack` (SngStyle::Normal) + `WriteSngList` +
`WriteSngToMidiTrack`.

## Source

VPW2 is type `LZSS_0BSng` in the tool's `gameconfigmidi.ini`
(ROM 0x272620..0x2836E4, 19 contiguous ranges). The `.sng` files in
`sound/sequences/` are already decompressed, so the converter takes
them directly. "Binary Sng" header (big-endian u32s): magic `0x215`,
track count, instrument count, then offsets for the track table,
volume-envelope table, pitch-bend-envelope table, ADSR table, drum
table, instrument lookup table (u16s), and master track (tempo).

## Results (2026-11-19)

19/19 sequences converted, 47,244 notes parsed, 45,600 note-ons in the
MIDIs (the difference is the original tool's merge of consecutive
same-note segments), zero warnings (no unknown commands, no discarded
tracks). Every file validates as SMF format 1, division 48, with
note-on == note-off in every track.

| File | Notes | Tempo | Length (ticks) |
|------|-------|-------|----------------|
| seq_034C.mid | 2467 | 100 BPM | 6432 |
| seq_034D.mid | 6723 | 90 BPM | 18624 |
| seq_034E.mid | 577 | 90 BPM | 2256 |
| seq_034F.mid | 1308 | 88 BPM | 3840 |
| seq_0350.mid (+AdditionalPart1) | 3620 | 120 BPM | 12094 |
| seq_0351.mid | 4581 | 100 BPM | 13632 |
| seq_0352.mid | 284 | 145 BPM | 1728 |
| seq_0353.mid | 281 | 115 BPM | 3168 |
| seq_0354.mid | 418 | 120 BPM | 1536 |
| seq_0355.mid | 474 | 140 BPM | 1728 |
| seq_0356.mid | 474 | 140 BPM | 1728 |
| seq_0357.mid | 134 | 120 BPM | 766 |
| seq_0358.mid | 427 | 120 BPM | 2304 |
| seq_0359.mid | 4721 | 105 BPM | 17280 |
| seq_035A.mid | 3877 | 150 BPM | 19968 |
| seq_035B.mid | 4110 | 80 BPM | 10560 |
| seq_035C.mid | 2605 | 90 BPM | 9984 |
| seq_035D.mid | 5206 | 90 BPM | 13824 |
| seq_035E.mid | 4957 | 95 BPM | 15456 |

seq_0350 exceeds 16 channels, so the port emits a second file
(`seq_0350_AdditionalPart1.mid`, 270 notes), exactly as the original
tool does.

## Caveats (inherited from the original tool)

- Instruments are the SNG instrument-lookup values, not GM program
  numbers — remap against the sound banks (`sound/bank1..8`) for
  playback with the right samples.
- ADSR data is parsed but not exported (the original tool does not
  support it either); some songs may need octave fixes (a known
  N64MidiTool quirk for some games).
- Loops: the SNG `0x96` loop-back command ends the track in the
  original tool, so MIDIs are one pass, not looped.
