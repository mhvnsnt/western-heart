/* ============================================================
   WESTERN HEART — Local-LLM NPC dialogue pattern (U7)
   Pattern source: LLM Game (RezixDev/llm-game, local LLM via
   LM Studio, Llama 3.2) — dynamic NPC dialogue, merchant haggling,
   battle taunts. WH uses: Trader dialogue in Heart and Mind
   Within (Trader is canon), dynamic versus banter (versus-
   banter.js stays the canned fallback). Local LLM = no API cost,
   no API keys, no network dependency in the game loop.
   This module builds prompts + parses responses ONLY. It makes
   no network call itself: the caller posts to its own local
   endpoint (default LM Studio http://localhost:1234/v1/chat/
   completions, caller-supplied — never a remote key service).
   If the service is unavailable, the caller MUST fall back to
   the canned banter lines — never block a fight on an LLM.
   All characters are adults; Trader/NPC prompts carry no
   personal data, only game state (souls, stage, matchup).
   ============================================================ */

export const LLM_NPC_DEFAULT_ENDPOINT = 'http://localhost:1234/v1/chat/completions';

export function traderPrompt({ souls = 0, stage = 'the crossroads', inventory = [] } = {}) {
  return [
    'You are the Trader of the Western Heart: a wandering merchant at a crossroads between realms. ' +
    'Speak in short, sly, trading terms. Never break character. Never mention you are an AI.',
    `The traveler stands at ${stage} carrying ${souls} souls. Their goods: ${inventory.join(', ') || 'nothing yet'}. ` +
    'Offer a trade: one useful thing for one soul, or refuse a bad bargain with wit. Keep it under 40 words.',
  ].join('\n');
}

export function banterPrompt({ speaker = 'fighter', foe = 'rival', event = 'round-start', hp = 1 } = {}) {
  return [
    `You are ${speaker}, a fighter in the Western Heart, facing ${foe}. ` +
    'Speak one short battle taunt in character. No profanity, no real-world references. Under 20 words.',
    `Moment: ${event}. Your health: ${Math.round(hp * 100)}%.`,
  ].join('\n');
}

// Build a chat-completions request body (OpenAI-compatible shape
// that LM Studio serves locally). No keys are ever attached here.
export function buildChatRequest(systemAndUser, { model = 'local-model', temperature = 0.8, maxTokens = 120 } = {}) {
  const [system, user] = systemAndUser;
  return {
    model, temperature, max_tokens: maxTokens,
    messages: [
      { role: 'system', content: system },
      { role: 'user', content: user },
    ],
  };
}

// Parse a chat-completions response (or a plain { text } object).
// Returns the text, or null when nothing usable came back — the
// caller then uses the canned fallback line.
export function parseChatResponse(json) {
  if (!json || typeof json !== 'object') return null;
  const text = json.choices && json.choices[0] && json.choices[0].message && json.choices[0].message.content;
  if (typeof text === 'string' && text.trim()) return text.trim();
  if (typeof json.text === 'string' && json.text.trim()) return json.text.trim();
  return null;
}
