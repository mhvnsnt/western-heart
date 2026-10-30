export function scaledAi(c, d) {
  const b = c.ai || {};
  return { aggression: b.aggression ?? 0.6, grabBias: 0.15, reaction: b.reaction ?? 0.55 };
}
