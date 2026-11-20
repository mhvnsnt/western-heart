# Sunshine + Moonlight — phone playtesting guide

**Goal:** the owner playtests builds streamed from our hardware to his phone.

## State of the stack (Oct 2026)

- **Sunshine** (host): https://github.com/LizardByte/Sunshine — self-hosted low-latency game-stream host, open implementation of NVIDIA GameStream. **GPL-3.0.** Very active: v2026.914.233613 (Sept 2026), Vulkan encoding, PipeWire/KWin capture on Linux, signed Windows/macOS installers. AMD/Intel/NVIDIA hardware encoding + software fallback.
- **Moonlight** (client): https://github.com/moonlight-stream — apps for **Android, iOS**, Windows, macOS, Linux, tvOS. **GPL-3.0.** Install from the Play Store / App Store on the phone.
- **License honesty:** GPL-3.0 on both. That is fine for OUR use — we run Sunshine on our own box and the owner installs Moonlight on his own phone; we are not linking GPL code into Western Heart or distributing either with the game. No code vendored here for that reason — install from official releases.

## When streaming is needed (and when it isn't)

| Build | Playtest path |
|---|---|
| **Web (Three.js) build — now** | **No streaming needed.** It's a web page; the owner opens the hosted artifact URL in his phone browser directly. Lower latency than any stream. |
| **Godot 4 desktop build — later** | **Sunshine → Moonlight.** Godot desktop exports can't run on a phone browser; stream the desktop build from our hardware to Moonlight on his phone. |
| Heavy editor/tooling | Sunshine desktop capture — stream a full desktop session if he ever needs to see Blender/Godot directly. |

## Setup (Godot-build playtesting, when we get there)

**On our Linux host:**
1. Install Sunshine from the official release (`.deb` via apt repo, or AppImage/Flatpak): `https://github.com/LizardByte/Sunshine/releases`
2. Open the web UI (`https://localhost:47990`), set username/password, pair Moonlight with the PIN.
3. Add an app entry pointing at the Godot build (example `apps.json` below) or use desktop capture.
4. Hardware encoding: needs a GPU on the host. **This VM has no GPU** — software encoding (x264) works for playtesting but costs CPU and adds latency. For serious playtest streaming, run Sunshine on a GPU box (his future setup, or a cloud GPU) — not this VM.

**On the owner's phone:**
1. Install **Moonlight** (Play Store / App Store).
2. Same Wi-Fi/VPN as the host (or expose the host via Tailscale — the `tailscale` connector is available; zero port-forwarding).
3. Tap the host, enter the PIN shown in Moonlight into Sunshine's web UI → paired.
4. Launch the Western Heart app entry. Touch controls: Moonlight has on-screen gamepad; for a fighter, pair a Bluetooth controller (PS/Xbox) to the phone — Moonlight forwards it.

**Example Sunshine app entry** (`~/.config/sunshine/apps.json`):
```json
{
  "apps": [
    {
      "name": "Western Heart (Godot)",
      "cmd": "/path/to/western-heart.x86_64",
      "working-dir": "/path/to/build",
      "exclude-global-prep-cmd": false
    }
  ]
}
```

## Latency reality check

Streaming adds encode + network + decode on top of game latency — typically 30–80 ms on LAN, more over the internet. For *feel* testing of a fighter's rollback netcode, direct play (web build on phone, or local Godot) is always truer. Use Sunshine/Moonlight for **content playtests** (does it look/play right), not for netcode tuning.
