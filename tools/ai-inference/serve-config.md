# Inference server config — game-side

## Choice (Oct 2026)

| Stage | Server | Why |
|---|---|---|
| Now (pipelines, NPC dialogue dev) | `llama-server` (llama.cpp, MIT) | One binary, GGUF-native, OpenAI-compatible, trivial on a Kaggle T4 |
| Concurrent NPCs / multi-user | vLLM (Apache-2.0) | PagedAttention + continuous batching; the 2026 default for production serving |
| Shared-prefix agent traffic | SGLang (Apache-2.0) | ~29% over vLLM when requests share long prefixes (system prompts, RAG) |

Do NOT start new work on TGI (maintenance mode; HF recommends vLLM/SGLang).
TensorRT-LLM (+30–50% throughput) is not worth its 1–2 week setup at our scale.

## llama-server (current)

```bash
# from cape-jones tools/inference/
bash kaggle-llm-server.sh   # serves default Qwen3-30B-A3B UD-IQ3_XXS on :8080
```

## vLLM (when we graduate)

```bash
pip install vllm
vllm serve <org>/<model>-AWQ \
  --host 0.0.0.0 --port 8080 \
  --quantization awq \
  --gpu-memory-utilization 0.90 \
  --max-model-len 8192 \
  --enable-prefix-caching
```

Notes:
- `--quantization` must match how the checkpoint was quantized (AWQ ≠ GPTQ).
- `--gpu-memory-utilization` is **preallocated**, not a limit — one server per GPU.
- T4 is sm_75: use AWQ/GPTQ INT4 checkpoints. **No FP8 on T4** (needs Ada sm_89+).
- Client code does not change: `inference_client.py` speaks OpenAI-compatible HTTP
  to either server (`INFERENCE_URL` env).

## Health checks for pipelines

```python
from inference_client import health, chat
assert health(), "inference server is down — start it before the pipeline runs"
```

Per the TRY-BEFORE-YOU-FLAG law: a probe saying "down" is a guess — `health()`
hitting the real endpoint is the evidence.
