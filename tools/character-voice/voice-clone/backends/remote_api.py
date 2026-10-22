"""Serverless inference backend — Chatterbox via HTTPS, zero local weights.

Weights live on the provider's infra (Replicate / fal.ai / HF Inference).
This module only does HTTPS in/out: text + voice params in, WAV bytes out.
No model downloads, no GPU, no disk bloat.

Config (env):
    WH_VOICE_API_URL    endpoint, e.g.
                        https://api.replicate.com/v1/models/resemble-ai/chatterbox/predictions
                        https://fal.run/fal-ai/chatterbox/text-to-speech
    WH_VOICE_API_KEY    bearer token
    WH_VOICE_MODEL      provider-specific model id (optional, for fal-style routing)
    WH_VOICE_POLL_S     max seconds to poll an async prediction (default 300)

Payload convention: Chatterbox-compatible fields
    { text, reference_audio_url|reference_audio_b64, exaggeration,
      cfg_weight, temperature, seed }
Provider adapters normalize the two known-good shapes (replicate-style
predictions API, fal-style queue API). Unknown providers: subclass and
override _request().
"""
import base64
import json
import os
import time
import urllib.request
import urllib.error


class RemoteApiError(Exception):
    pass


def _env(name, default=None, required=False):
    v = os.environ.get(name, default)
    if required and not v:
        raise RemoteApiError(
            f"{name} is not set — the serverless backend needs an API key. "
            "See docs/VOICE-CLONING-PIPELINE.md §3 (no key = no generation run).")
    return v


class RemoteApiBackend:
    name = "remote_api"

    def __init__(self):
        self.url = _env("WH_VOICE_API_URL", required=True)
        self.key = _env("WH_VOICE_API_KEY", required=True)
        self.model = _env("WH_VOICE_MODEL")
        self.poll_s = int(_env("WH_VOICE_POLL_S", "300"))

    def _headers(self):
        h = {"Content-Type": "application/json",
             "User-Agent": "WH-voice-clone/1.0"}
        # fal.ai uses `Key <k>`; replicate/HF use Bearer — try Bearer, fall
        # back is the provider's problem to document; both are tried.
        h["Authorization"] = f"Bearer {self.key}"
        return h

    def _post(self, url, payload, extra_headers=None):
        body = json.dumps(payload).encode()
        headers = self._headers()
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.build_opener().open(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            raise RemoteApiError(f"API POST {url} -> HTTP {e.code}: {detail}")

    def _get(self, url):
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.build_opener().open(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            raise RemoteApiError(f"API GET {url} -> HTTP {e.code}: {detail}")

    def _download(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": "WH-voice-clone/1.0"})
        with urllib.request.build_opener().open(req, timeout=120) as r:
            return r.read()

    def generate(self, text, ref_audio, params):
        """Run one line through the remote Chatterbox endpoint. Returns WAV bytes."""
        payload = self._chatterbox_payload(text, ref_audio, params)
        if "replicate.com" in self.url:
            return self._replicate_flow(payload)
        if "fal.run" in self.url or "fal.ai" in self.url:
            return self._fal_flow(payload)
        # Generic: assume sync endpoint returning {audio_url} or {audio_b64}
        return self._generic_flow(payload)

    def _chatterbox_payload(self, text, ref_audio, params):
        p = {
            "text": text,
            "exaggeration": float(params.get("exaggeration", 0.5)),
            "cfg_weight": float(params.get("cfg_weight", 0.5)),
            "temperature": float(params.get("temperature", 0.8)),
        }
        seed = params.get("seed")
        if seed is not None:
            p["seed"] = int(seed)
        if ref_audio:
            if ref_audio.startswith(("http://", "https://")):
                p["reference_audio_url"] = ref_audio
            elif os.path.isfile(ref_audio):
                with open(ref_audio, "rb") as f:
                    p["reference_audio_b64"] = base64.b64encode(f.read()).decode()
            else:
                raise RemoteApiError(f"reference_audio not found: {ref_audio}")
        if self.model:
            p["model"] = self.model
        return p

    def _replicate_flow(self, payload):
        pred = self._post(self.url, {"input": payload})
        status_url = pred.get("urls", {}).get("get")
        if not status_url:
            raise RemoteApiError(f"replicate: no status URL in {str(pred)[:200]}")
        deadline = time.time() + self.poll_s
        while time.time() < deadline:
            s = self._get(status_url)
            st = s.get("status")
            if st == "succeeded":
                out = s.get("output")
                audio_url = out[0] if isinstance(out, list) else out
                if not audio_url:
                    raise RemoteApiError("replicate: succeeded but no audio output")
                return self._download(audio_url)
            if st in ("failed", "canceled"):
                raise RemoteApiError(f"replicate: prediction {st}: {str(s.get('error'))[:300]}")
            time.sleep(4)
        raise RemoteApiError("replicate: poll timed out")

    def _fal_flow(self, payload):
        # fal queue API: POST -> status_url, poll -> response_url
        res = self._post(self.url, payload)
        status_url = res.get("status_url") or res.get("response_url")
        if not status_url:
            # some fal endpoints are sync
            audio = res.get("audio") or res.get("audio_url")
            if audio:
                url = audio.get("url") if isinstance(audio, dict) else audio
                return self._download(url)
            raise RemoteApiError(f"fal: unexpected response {str(res)[:200]}")
        deadline = time.time() + self.poll_s
        while time.time() < deadline:
            s = self._get(status_url)
            st = s.get("status")
            if st == "COMPLETED":
                audio = (s.get("response") or {}).get("audio") or s.get("audio")
                url = audio.get("url") if isinstance(audio, dict) else audio
                if not url:
                    raise RemoteApiError("fal: completed but no audio URL")
                return self._download(url)
            if st in ("FAILED", "CANCELLED"):
                raise RemoteApiError(f"fal: {st}: {str(s.get('error'))[:300]}")
            time.sleep(4)
        raise RemoteApiError("fal: poll timed out")

    def _generic_flow(self, payload):
        res = self._post(self.url, payload)
        if res.get("audio_b64"):
            return base64.b64decode(res["audio_b64"])
        if res.get("audio_url"):
            return self._download(res["audio_url"])
        raise RemoteApiError(f"generic: unexpected response {str(res)[:200]}")
