#!/usr/bin/env python3
"""vpw2_sng2midi.py — convert VPW2 .sng sequences to Standard MIDI Files.

Faithful Python port of the "Binary Sng" path in SubDrag's N64 Soundbank
Tool / N64MidiTool (jombo23/N64-Tools, Unlicense):
  CMidiParse::SngToMidi (Binary Sng branch, magic 0x215)
  CMidiParse::ParseSngTrack (SngStyle::Normal)
  CMidiParse::WriteSngList (separateByInstrument=false, division 0x30)
  CMidiParse::WriteSngToMidiTrack (VLQ + running status)

VPW2's 19 sequences are type LZSS_0BSng in the tool's gameconfigmidi.ini
(ROM 0x272620..0x2836E4, 19 ranges); the .sng files in
teardown/virtual-pro-wrestling-2/sound/sequences/ are already
decompressed, so this tool takes them directly.

SNG ("Binary Sng") header (big-endian u32s):
  +0x00 magic 0x00000215
  +0x04 number of tracks
  +0x08 total instruments (instrument lookup table size)
  +0x0C track pointer table offset
  +0x10 volume envelope pointer table offset
  +0x14 pitch-bend envelope pointer table offset
  +0x18 ADSR table offset
  +0x1C drum table offset
  +0x20 instrument lookup table offset (u16s)
  +0x24 master track offset (tempo/effect commands; track -1)

Track events (ParseSngTrack):
  0x00-0x5F note (pitch), 0x60 rest; velocity byte (bit 0x80 = "repeat
    this velocity"); variable-length note length (1 byte < 0x80, else
    2 bytes ((b&0x7F)<<8)|next). Note number in MIDI = note + 12 +
    transpose.
  0x80 end, 0x81 instrument (lookup), 0x82 slide, 0x84 ADSR set (7B),
  0x85 tempo (BPM; master track only -> tempo map), 0x86/0x87 release
  time, 0x88/0x89 vibrato, 0x8B defined length, 0x8D transpose,
  0x8F detune, 0x90 ADSR index, 0x95 loop start, 0x96 loop back (end),
  0x97 wobble (disabled in the original), 0x99/0x9A/0x9B velocity modes,
  0x9C pan, 0x9E/0x9F drum map on/off, 0xA2 effect, 0xA3-A5 min/max,
  0xA6 volume, 0xA7 ?, 0xA8 pitch bend, 0xA9 sweep, 0xAA master effect,
  0xAB master sync, 0xAC re-enable length, 0xB0 ?.

Usage:
  vpw2_sng2midi.py <in.sng> [out.mid] [--all <sequences_dir> <out_dir>]
  Without an output path, the .mid goes next to the input.

Lane W2 (VPW2 + KoC2 RE), 2026-11-19. Original C++ by SubDrag (Unlicense).
"""
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

DIVISION = 0x30
MAXCHANNELS = 1024


def u16be(b, o):
    return struct.unpack_from(">H", b, o)[0]


def u32be(b, o):
    return struct.unpack_from(">I", b, o)[0]


def get_sng_varlen(buf, off):
    """GetSngVariableLength: 1 byte if < 0x80 else 2 bytes."""
    if buf[off] & 0x80:
        return ((buf[off] & 0x7F) << 8) | buf[off + 1]
    return buf[off]


def varlen_size(value):
    """Number of bytes a value takes in GetSngVariableLength encoding."""
    return 2 if value >= 0x80 else 1


@dataclass
class SngTimeValue:
    start: int = 0
    end: int = 0
    value: int = 0


@dataclass
class SngNoteInfo:
    start: int = 0
    end: int = 0
    note: int = 0
    velocity: int = 0
    instrument: int = 0
    pan: int = 0x40
    volume: int = 0x7F
    pitch_bend: int = 0x40
    vibrato: int = 0
    tempo: int = 0
    effect: int = 0
    track: int = 0
    uid: int = 0
    ignore_note_on: bool = False
    segment: int = 0


@dataclass
class TrackEvent:
    delta: int = 0
    type: int = 0
    contents: bytes = b""
    obsolete: bool = False


def apply_envelope(notes, envelope, attr):
    """Port of the volume/pitch-bend split loops in ParseSngTrack.

    Splits notes at envelope boundaries so each piece carries the
    envelope value active over its span.
    """
    x = 0
    while x < len(notes):
        split = False
        for env in envelope:
            n = notes[x]
            val = getattr(n, attr)
            # Envelope ends inside the note (note starts in envelope)
            if (n.start >= env.start and n.start < env.end
                    and n.end > env.end and n.end > env.start):
                if val != env.value:
                    new = SngNoteInfo(**{**n.__dict__})
                    notes[x].start = env.end
                    new.end = env.end
                    setattr(new, attr, env.value)
                    notes.append(new)
                    x -= 1
                    split = True
                    break
            # Envelope starts inside the note (note ends in envelope)
            elif (n.start < env.start and n.start < env.end
                    and n.end > env.start and n.end <= env.end):
                if val != env.value:
                    new = SngNoteInfo(**{**n.__dict__})
                    notes[x].end = env.start
                    new.start = env.start
                    setattr(new, attr, env.value)
                    notes.append(new)
                    x -= 1
                    split = True
                    break
            # Envelope completely inside the note
            elif (n.start < env.start and n.start < env.end
                    and n.end > env.start and n.end > env.end):
                if val != env.value:
                    new1 = SngNoteInfo(**{**n.__dict__})
                    new2 = SngNoteInfo(**{**n.__dict__})
                    notes[x].end = env.start
                    new1.start = env.start
                    new1.end = env.end
                    setattr(new1, attr, env.value)
                    notes.append(new1)
                    new2.start = env.end
                    notes.append(new2)
                    x -= 1
                    split = True
                    break
            # Note completely inside the envelope
            elif (n.start >= env.start and n.start < env.end
                    and n.end > env.start and n.end <= env.end):
                notes[x] = SngNoteInfo(**{**n.__dict__, attr: env.value})
        x += 1


def parse_sng_track(track_number, buf, offset, end, instrument_lookup,
                    adsr_pointer, drum_pointer, volume_env, pitchbend_env,
                    tempo_positions, uid_counter, warnings):
    """Port of CMidiParse::ParseSngTrack (SngStyle::Normal only).

    Returns (notes, number_instruments_max). tempo_positions is extended
    in place for the master track (track_number == -1). On an unknown
    command the whole track's notes are discarded, as in the original.
    """
    notes = []
    spot = offset
    command = 0x00
    use_defined_length = False
    defined_length = 0
    use_defined_velocity = False
    defined_velocity = 0x7F
    use_defined_release = False
    defined_release = 0x01
    absolute_time = 0
    current_pan = 0x80
    current_instrument = 0
    current_volume = 0x7F
    current_pitch_bend = 0x40
    current_drum_offset = -1
    current_transpose = 0
    current_effect = 0
    max_instrument = 0

    def note_number(n):
        return n + 0xC + current_transpose

    while command != 0x80 and spot < end:
        if track_number >= 0:
            current_tempo = int(60000000.0 / 120.0)
            for (t, v) in tempo_positions:
                if t <= absolute_time:
                    current_tempo = v
                else:
                    break
        else:
            current_tempo = int(60000000.0 / 120.0)
            # master track keeps its own tempo (set by 0x85 below);
            # the C++ code re-derives it only for trackNumber >= 0,
            # but the local currentTempo persists across iterations
            # for the master track via the 0x85 handler. We emulate by
            # keeping a persistent variable:
            current_tempo = parse_sng_track.master_tempo
        command = buf[spot]
        spot += 1

        if command < 0x80:  # note or rest
            note = command
            if use_defined_velocity:
                velocity = defined_velocity
            else:
                if buf[spot] & 0x80:
                    use_defined_velocity = True
                    defined_velocity = buf[spot] & 0x7F
                velocity = buf[spot] & 0x7F
                spot += 1
            if use_defined_length:
                note_length = defined_length
            else:
                note_length = get_sng_varlen(buf, spot)
                spot += varlen_size(note_length)
            if note < 0x60:
                if current_drum_offset != -1:
                    drum_off = (drum_pointer + current_drum_offset * 6
                                + note * 6)
                    inst_idx = buf[drum_off + 1]
                    pan = buf[drum_off + 4]
                    drum_note = buf[drum_off + 5]
                    instrument = instrument_lookup[inst_idx]
                    n = SngNoteInfo(
                        start=absolute_time, uid=uid_counter[0],
                        note=drum_note + 0xC + current_transpose,
                        velocity=velocity, effect=current_effect,
                        tempo=current_tempo, instrument=instrument,
                        pan=(pan >> 1) & 0xFF, pitch_bend=current_pitch_bend,
                        volume=current_volume, track=track_number)
                    uid_counter[0] += 1
                    n.end = (n.start + defined_release if use_defined_release
                             else n.start + note_length)
                    notes.append(n)
                else:
                    n = SngNoteInfo(
                        start=absolute_time, uid=uid_counter[0],
                        note=note_number(note), velocity=velocity,
                        effect=current_effect, tempo=current_tempo,
                        instrument=current_instrument,
                        pan=(current_pan >> 1) & 0xFF,
                        pitch_bend=current_pitch_bend,
                        volume=current_volume, track=track_number)
                    uid_counter[0] += 1
                    n.end = (n.start + defined_release if use_defined_release
                             else n.start + note_length)
                    notes.append(n)
            absolute_time += note_length
        else:
            if command == 0x80:
                break
            elif command == 0x81:  # instrument
                v = get_sng_varlen(buf, spot)
                spot += varlen_size(v)
                if v >= len(instrument_lookup):
                    current_instrument = v
                else:
                    current_instrument = instrument_lookup[v]
                if current_instrument > max_instrument:
                    max_instrument = current_instrument
            elif command == 0x82:  # slide
                spot += 1
            elif command == 0x83:
                pass
            elif command == 0x84:  # ADSR set
                spot += 7
            elif command == 0x85:  # tempo (BPM)
                tempo = buf[spot]
                current_tempo = int(60000000.0 / float(tempo)) if tempo else 0
                parse_sng_track.master_tempo = current_tempo
                if track_number == -1:
                    tempo_positions.append((absolute_time, current_tempo))
                spot += 1
            elif command == 0x86:  # release time
                use_defined_release = True
                defined_release = u16be(buf, spot)
                spot += 2
            elif command == 0x87:  # release time back to full
                use_defined_release = False
                spot += 1
            elif command in (0x88, 0x89):  # vibrato
                spot += 3
            elif command == 0x8A:  # solo
                pass
            elif command == 0x8B:  # defined length
                defined_length = get_sng_varlen(buf, spot)
                if defined_length == 0:
                    use_defined_length = False
                    spot += 1
                elif defined_length < 0x80:
                    use_defined_length = True
                    spot += 1
                else:
                    use_defined_length = True
                    spot += 2
            elif command == 0x8D:  # transpose
                current_transpose = buf[spot] - 256 if buf[spot] >= 0x80 else buf[spot]
                spot += 1
            elif command == 0x8F:  # detune
                spot += 1
            elif command == 0x90:  # ADSR index
                spot += 1
            elif command in (0x91, 0x92, 0x93, 0x94):  # triggers
                pass
            elif command == 0x95:  # loop start
                spot += 1
            elif command == 0x96:  # loop back -> end
                break
            elif command == 0x97:  # wobble (disabled in original)
                spot += 3
            elif command == 0x98:
                pass
            elif command == 0x99:  # re-enable velocity
                use_defined_velocity = False
            elif command == 0x9A:  # enable defined velocity
                use_defined_velocity = True
            elif command == 0x9B:  # set repeat velocity
                defined_velocity = buf[spot]
                use_defined_velocity = True
                spot += 1
            elif command == 0x9C:  # pan
                current_pan = buf[spot]
                spot += 1
            elif command == 0x9E:  # drum map on
                current_drum_offset = buf[spot]
                spot += 1
            elif command == 0x9F:  # drum map off
                current_drum_offset = -1
            elif command == 0xA2:  # effect
                current_effect = buf[spot]
                spot += 1
            elif command in (0xA3, 0xA4, 0xA5):  # min/max
                spot += 2
            elif command == 0xA6:  # note volume
                current_volume = buf[spot]
                spot += 1
            elif command == 0xA7:
                length = get_sng_varlen(buf, spot)
                spot += varlen_size(length)
            elif command == 0xA8:  # pitch bend
                current_pitch_bend = buf[spot]
                spot += 1
            elif command == 0xA9:  # stereo sweep
                spot += 1
            elif command == 0xAA:  # master effect
                spot += 1
            elif command == 0xAB:  # master sync
                spot += 1
            elif command == 0xAC:  # re-enable length
                use_defined_length = False
            elif command == 0xB0:
                spot += 1
            else:
                warnings.append(
                    f"track {track_number}: unknown command "
                    f"{command:#04x} at {spot - 1:#x}; track discarded")
                return [], max_instrument

    apply_envelope(notes, volume_env, "volume")
    apply_envelope(notes, pitchbend_env, "pitch_bend")
    return notes, max_instrument


parse_sng_track.master_tempo = int(60000000.0 / 120.0)


def parse_envelope(buf, start, end):
    """Volume / pitch-bend envelope: (value, length) pairs."""
    out = []
    absolute = 0
    spot = start
    while spot < end:
        value = buf[spot]
        single = not (value & 0x80)
        value &= 0x7F
        spot += 1
        length = 1
        if not single:
            length = get_sng_varlen(buf, spot) + 2
            spot += 1 if length < 0x80 else 2
        out.append(SngTimeValue(absolute, absolute + length, value))
        absolute += length
    return out


def sng_to_notes(buf, warnings):
    """Port of CMidiParse::SngToMidi (Binary Sng branch)."""
    if u32be(buf, 0) != 0x215 or u32be(buf, 4) == 0x215:
        raise ValueError("not a Binary Sng file (magic != 0x215)")
    n_tracks = u32be(buf, 4)
    n_instruments = u32be(buf, 8)
    track_ptr = u32be(buf, 0x0C)
    volume_ptr = u32be(buf, 0x10)
    pitchbend_ptr = u32be(buf, 0x14)
    adsr_ptr = u32be(buf, 0x18)
    drum_ptr = u32be(buf, 0x1C)
    instrument_ptr = u32be(buf, 0x20)
    master_ptr = u32be(buf, 0x24)
    lookup = [u16be(buf, instrument_ptr + 2 * i)
              for i in range(n_instruments)]
    max_inst = max(lookup) if lookup else 0
    tempo_positions = []
    uid_counter = [0]
    parse_sng_track.master_tempo = int(60000000.0 / 120.0)
    all_notes = []

    first_track = u32be(buf, track_ptr)
    master_notes, m = parse_sng_track(
        -1, buf, master_ptr, first_track, lookup, adsr_ptr, drum_ptr,
        [], [], tempo_positions, uid_counter, warnings)
    max_inst = max(max_inst, m)
    all_notes.extend(master_notes)

    for x in range(n_tracks):
        vol_ptr = u32be(buf, volume_ptr + 4 * x)
        vol_env = []
        if vol_ptr:
            vol_end = 0
            for y in range(x + 1, n_tracks):
                t = u32be(buf, volume_ptr + 4 * y)
                if t:
                    vol_end = t
                    break
            if not vol_end:
                vol_end = master_ptr
            vol_env = parse_envelope(buf, vol_ptr, vol_end)
        pb_ptr = u32be(buf, pitchbend_ptr + 4 * x)
        pb_env = []
        if pb_ptr:
            pb_end = 0
            for y in range(x + 1, n_tracks):
                t = u32be(buf, pitchbend_ptr + 4 * y)
                if t:
                    pb_end = t
                    break
            if not pb_end:
                pb_end = master_ptr
            pb_env = parse_envelope(buf, pb_ptr, pb_end)
        track_data = u32be(buf, track_ptr + 4 * x)
        track_end = len(buf)
        if x < n_tracks - 1:
            track_end = u32be(buf, track_ptr + 4 * (x + 1))
        notes, m = parse_sng_track(
            x, buf, track_data, track_end, lookup, adsr_ptr, drum_ptr,
            vol_env, pb_env, tempo_positions, uid_counter, warnings)
        max_inst = max(max_inst, m)
        all_notes.extend(notes)
    return all_notes, tempo_positions, max_inst + 1


def vlq(value):
    """Standard MIDI variable-length quantity."""
    if value == 0:
        return b"\x00"
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(out))


def write_track(events):
    """Port of WriteSngToMidiTrack: MTrk chunk with running status."""
    body = bytearray()
    prev_type = 0
    time_offset = 0
    for ev in events:
        if ev.obsolete:
            time_offset += ev.delta
            continue
        body += vlq(ev.delta + time_offset)
        time_offset = 0
        if ev.type != prev_type or ev.type >= 0xF0:
            body.append(ev.type)
        body += ev.contents
        prev_type = ev.type
    return b"MTrk" + struct.pack(">I", len(body)) + bytes(body)


def is_overlap(a_start, a_end, b_start, b_end):
    return a_end > b_start and b_end > a_start


def conflicts(a, b):
    return (a.instrument != b.instrument or a.pan != b.pan
            or a.pitch_bend != b.pitch_bend or a.volume != b.volume
            or a.effect != b.effect or a.vibrato != b.vibrato)


def write_sng_list(notes, tempo_positions, out_path):
    """Port of CMidiParse::WriteSngList (separateByInstrument=false)."""
    notes = [SngNoteInfo(**{**n.__dict__}) for n in notes]
    for n in notes:
        n.note = max(0, min(0x7F, n.note))
        n.pan = max(0, min(0x7F, n.pan))
        n.volume = max(0, min(0x7F, n.volume))
        n.effect = min(0x7F, n.effect)
        n.pitch_bend = min(0x7F, n.pitch_bend)
        n.vibrato = min(0x7F, n.vibrato)

    channels = [[] for _ in range(MAXCHANNELS)]
    num_channels = 0
    for n in notes:
        ch = n.track if n.track != -1 else 0
        if ch > MAXCHANNELS:
            raise ValueError("too many channels for midi")
        channels[ch].append(n)
        num_channels = max(num_channels, ch + 1)
    for ch in channels[:num_channels]:
        ch.sort(key=lambda n: n.start)

    # Move conflicting overlapping notes to fresh channels.
    overlapping = []
    for ci in range(num_channels):
        ch = channels[ci]
        x = 0
        while x < len(ch):
            y = x + 1
            while y < len(ch):
                a, b = ch[x], ch[y]
                if (is_overlap(a.start, a.end, b.start, b.end)
                        and conflicts(a, b)):
                    overlapping.append(ch.pop(y))
                else:
                    y += 1
            x += 1
    overlapping.sort(key=lambda n: n.start)
    start_channel = num_channels
    for n in overlapping:
        applied = -1
        for z in range(start_channel, MAXCHANNELS):
            if any(is_overlap(n.start, n.end, m.start, m.end)
                   and conflicts(n, m) for m in channels[z]):
                continue
            applied = z
            break
        if applied == -1 or applied > MAXCHANNELS:
            raise ValueError("too many channels for midi")
        channels[applied].append(n)
        num_channels = max(num_channels, applied + 1)

    if num_channels == 0:
        return []  # no notes: original deletes the output file

    out_path = Path(out_path)
    written = []
    ch = 0
    while ch < num_channels:
        if ch == 0:
            path = out_path
        else:
            midi_number = ch // 0x10
            stem = out_path.stem
            path = out_path.with_name(
                f"{stem}_AdditionalPart{midi_number}{out_path.suffix}")
        n_tracks = 0x11
        if (num_channels - ch) < 0x10:
            n_tracks = (num_channels - ch) + 1
        data = bytearray()
        data += b"MThd" + struct.pack(">IHHH", 6, 1, n_tracks, DIVISION)
        # Tempo track.
        tempo_events = []
        abs_tempo = 0
        for (t, v) in tempo_positions:
            tempo_events.append(TrackEvent(
                delta=t - abs_tempo, type=0xFF,
                contents=bytes([0x51, 0x03, (v >> 16) & 0xFF,
                                (v >> 8) & 0xFF, v & 0xFF])))
            abs_tempo = t
        tempo_events.append(TrackEvent(delta=0, type=0xFF,
                                       contents=bytes([0x2F, 0x00])))
        data += write_track(tempo_events)

        for channel in range(ch, min(ch + 0x10, num_channels)):
            controller = channel % 0x10
            events = []
            absolute = 0
            cur_pan = 0x40
            cur_inst = 0xFF
            cur_vol = 0x7F
            cur_bend = 0x40
            cur_effect = 0
            cur_vibrato = 0
            cur_segment = -1
            pending = []
            ch_notes = channels[channel]

            def emit(delta, typ, contents):
                nonlocal absolute
                events.append(TrackEvent(delta=delta, type=typ,
                                         contents=contents))
                absolute += delta

            for idx, n in enumerate(ch_notes):
                # Shut off pending notes that end before/at this start.
                while pending:
                    pending.sort(key=lambda p: p.end)
                    p = pending[0]
                    if p.end < n.start:
                        emit(p.end - absolute, 0x80 | controller,
                             bytes([p.note, p.velocity]))
                        pending.pop(0)
                    elif p.end == n.start:
                        skip = False
                        for y in range(idx, len(ch_notes)):
                            m = ch_notes[y]
                            if (p.end == m.start and p.note == m.note
                                    and p.instrument == m.instrument
                                    and p.track == m.track
                                    and p.uid == m.uid):
                                pending[0] = m
                                ch_notes[y].ignore_note_on = True
                                if y == idx:
                                    n.ignore_note_on = True
                                skip = True
                                break
                            elif p.end < m.start:
                                break
                        if not skip:
                            emit(p.end - absolute, 0x80 | controller,
                                 bytes([p.note, p.velocity]))
                            pending.pop(0)
                        else:
                            break
                    else:
                        break
                if n.segment != cur_segment:
                    events.append(TrackEvent(
                        delta=0, type=0xB0 | controller,
                        contents=bytes([104, n.segment])))
                    cur_segment = n.segment
                delta = max(0, n.start - absolute)
                if n.effect != cur_effect:
                    emit(delta, 0xB0 | controller, bytes([91, n.effect]))
                    delta = 0
                    cur_effect = n.effect
                if n.instrument != cur_inst:
                    emit(delta, 0xB0 | controller,
                         bytes([0, n.instrument // 0x8000]))
                    delta = 0
                    emit(0, 0xB0 | controller,
                         bytes([32, n.instrument // 0x80]))
                    emit(0, 0xC0 | controller,
                         bytes([n.instrument & 0x7F]))
                    cur_inst = n.instrument
                if n.pan != cur_pan:
                    emit(delta, 0xB0 | controller, bytes([10, n.pan]))
                    delta = 0
                    cur_pan = n.pan
                if n.volume != cur_vol:
                    emit(delta, 0xB0 | controller, bytes([0x07, n.volume]))
                    delta = 0
                    cur_vol = n.volume
                if n.vibrato != cur_vibrato:
                    emit(delta, 0xB0 | controller, bytes([0x01, n.vibrato]))
                    delta = 0
                    cur_vibrato = n.vibrato
                if n.pitch_bend != cur_bend:
                    emit(delta, 0xE0 | controller,
                         bytes([0x00, n.pitch_bend]))
                    delta = 0
                    cur_bend = n.pitch_bend
                if not n.ignore_note_on:
                    emit(delta, 0x90 | controller,
                         bytes([n.note, n.velocity]))
                    pending.append(n)
            pending.sort(key=lambda p: p.end)
            while pending:
                p = pending.pop(0)
                emit(max(0, p.end - absolute), 0x80 | controller,
                     bytes([p.note, p.velocity]))
            events.append(TrackEvent(delta=0, type=0xFF,
                                     contents=bytes([0x2F, 0x00])))
            data += write_track(events)
        path.write_bytes(bytes(data))
        written.append(path)
        ch += 0x10
    return written


def convert(in_path, out_path):
    buf = Path(in_path).read_bytes()
    warnings = []
    notes, tempos, n_inst = sng_to_notes(buf, warnings)
    written = write_sng_list(notes, tempos, out_path)
    return {"notes": len(notes), "tempo_changes": len(tempos),
            "instruments": n_inst, "files": [str(p) for p in written],
            "warnings": warnings}


def main():
    args = sys.argv[1:]
    if len(args) >= 3 and args[0] == "--all":
        src, dst = Path(args[1]), Path(args[2])
        dst.mkdir(parents=True, exist_ok=True)
        total_notes = 0
        for sng in sorted(src.glob("*.sng")):
            out = dst / (sng.stem + ".mid")
            try:
                r = convert(sng, out)
            except Exception as e:
                print(f"{sng.name}: FAILED ({e})")
                continue
            total_notes += r["notes"]
            print(f"{sng.name}: {r['notes']} notes, "
                  f"{r['tempo_changes']} tempo changes, "
                  f"{r['instruments']} instruments -> {out.name}")
            for w in r["warnings"]:
                print(f"  warning: {w}")
        print(f"total notes: {total_notes}")
        return
    if not args:
        print(__doc__)
        sys.exit(1)
    in_path = Path(args[0])
    out_path = Path(args[1]) if len(args) > 1 else in_path.with_suffix(".mid")
    r = convert(in_path, out_path)
    print(f"{in_path.name}: {r['notes']} notes, "
          f"{r['tempo_changes']} tempo changes, "
          f"{r['instruments']} instruments")
    for f in r["files"]:
        print(f"  wrote {f}")
    for w in r["warnings"]:
        print(f"  warning: {w}")


if __name__ == "__main__":
    main()
