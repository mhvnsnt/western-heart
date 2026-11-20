/* facemorphs.js — Creation Suite face-morph pipeline module.
   Source: GNM Head (google/GNM, Apache-2.0) via mhvnsnt/cape-jones
   3d-assets/face-rig/ (PR #125 merged): named presets -> ~20 semantic
   params, mixed with blendPresets(). Mirrors GNM's blend_expressions. */

export const FACE_PARAMS = ["blink_L", "blink_R", "wide", "squint_L", "squint_R", "look_x", "look_y", "brow_L", "brow_R", "brow_squeeze", "jaw_open", "smile", "frown", "grimace", "smirk_L", "smirk_R", "mouth_shift_x", "tongue_out", "tongue_side", "pupil_toggle"];

export const FACE_PRESETS = {"determined_focused": {"params": {"brow_L": -0.45, "brow_R": -0.45, "brow_squeeze": 0.35}, "mouth_index": 0}, "angry_scowling": {"params": {"brow_L": -1.0, "brow_R": -1.0, "brow_squeeze": 0.7, "squint_L": 0.35, "squint_R": 0.35, "frown": 0.75, "grimace": 0.45}, "mouth_index": 15}, "intrigued_questioning": {"params": {"brow_L": 0.75, "brow_R": -0.15, "look_x": 0.55, "pupil_toggle": 1.0, "smirk_R": 0.55}, "mouth_index": 0}, "squinting_flight": {"params": {"squint_L": 1.0, "squint_R": 1.0, "brow_squeeze": 0.5, "brow_L": -0.3, "brow_R": -0.3, "frown": 0.45}, "mouth_index": 10}, "surprised_alarmed": {"params": {"wide": 1.0, "brow_L": 1.0, "brow_R": 1.0, "jaw_open": 0.85, "pupil_toggle": 1.0}, "mouth_index": 16}, "straining_grimacing": {"params": {"squint_L": 0.8, "squint_R": 0.8, "brow_squeeze": 1.0, "grimace": 1.0, "jaw_open": 0.35, "frown": 0.5}, "mouth_index": 15}, "concentrating": {"params": {"squint_L": 0.5, "squint_R": 0.5, "brow_L": -0.4, "brow_R": -0.4, "frown": 0.3}, "mouth_index": 0}, "unconscious_closed": {"params": {"blink_L": 1.0, "blink_R": 1.0, "jaw_open": 0.15}, "mouth_index": 0}, "dart_up": {"params": {"look_y": 1.0, "pupil_toggle": 1.0}, "mouth_index": 0}, "dart_left": {"params": {"look_x": -1.0, "pupil_toggle": 1.0}, "mouth_index": 0}, "dart_down": {"params": {"look_y": -1.0, "pupil_toggle": 1.0}, "mouth_index": 0}, "side_eye_suspicious": {"params": {"look_x": 1.0, "squint_L": 0.3, "squint_R": 0.3, "brow_L": -0.3, "brow_R": -0.3, "smirk_L": 0.4, "pupil_toggle": 1.0}, "mouth_index": 0}, "happy": {"params": {"smile": 1.0, "squint_L": 0.25, "squint_R": 0.25, "brow_L": 0.3, "brow_R": 0.3}, "mouth_index": 7}, "disgust": {"params": {"frown": 0.8, "grimace": 0.5, "brow_L": -0.6, "brow_R": -0.6, "brow_squeeze": 0.6, "mouth_shift_x": 0.4}, "mouth_index": 11}, "snarl": {"params": {"grimace": 0.9, "brow_L": -0.8, "brow_R": -0.8, "brow_squeeze": 0.8, "frown": 0.4}, "mouth_index": 11}, "pucker": {"params": {"jaw_open": 0.1}, "mouth_index": 13}, "blow": {"params": {"jaw_open": 0.25, "wide": 0.2}, "mouth_index": 3}, "tongue_center": {"params": {"tongue_out": 0.75, "jaw_open": 0.3}, "mouth_index": 1}, "wink_left": {"params": {"blink_L": 1.0, "smile": 0.4, "smirk_L": 0.5, "pupil_toggle": 1.0}, "mouth_index": 0}, "wink_right": {"params": {"blink_R": 1.0, "smile": 0.4, "smirk_R": 0.5, "pupil_toggle": 1.0}, "mouth_index": 0}, "smug": {"params": {"smirk_R": 0.8, "brow_R": 0.5, "brow_L": -0.2}, "mouth_index": 0}};

export const FACE_CHECKLIST = ["determined_focused", "angry_scowling", "intrigued_questioning", "squinting_flight", "surprised_alarmed", "straining_grimacing", "concentrating", "unconscious_closed"];
export const FACE_DARTS = ["dart_up", "dart_left", "dart_down", "side_eye_suspicious"];

export function presetVector(name){
  const vec = {}; for(const p of FACE_PARAMS) vec[p] = 0;
  const pr = FACE_PRESETS[name]; if(!pr) return vec;
  for(const [k,v] of Object.entries(pr.params)) vec[k] = v;
  return vec;
}

/* Mirrors GNM's blend_expressions({class: weight}) and CJ's blend_presets. */
export function blendPresets(weights){
  const vec = {}; for(const p of FACE_PARAMS) vec[p] = 0;
  const total = Object.values(weights).reduce((a,b)=>a+b,0) || 1;
  for(const [name,w] of Object.entries(weights)){
    const pv = presetVector(name);
    for(const p of FACE_PARAMS) vec[p] += pv[p] * (w/total);
  }
  return vec;
}

/* Apply a face param vector to a rigged character in three.js:
   eyes/brows -> eyelid + brow bone proxies; mouth -> jaw bone proxy. */
export function applyFaceParams(character, vec){
  const rot = (name, x, y=0, z=0)=>{
    const o = character.getObjectByName(name); if(o) o.rotation.set(x,y,z);
  };
  const blink = ((vec.blink_L||0)+(vec.blink_R||0))/2;
  const wide = vec.wide||0, squint = ((vec.squint_L||0)+(vec.squint_R||0))/2;
  rot('Head', 0, (vec.look_x||0)*0.2, 0);
  // eyelid proxy via head pitch micro-rotation (shape keys on real rigs)
  const lid = blink*0.5 - wide*0.3 + squint*0.25;
  rot('LeftEye', lid*0.4, 0, 0); rot('RightEye', lid*0.4, 0, 0);
  rot('Jaw', (vec.jaw_open||0)*0.6, (vec.mouth_shift_x||0)*0.1, 0);
  return character;
}
