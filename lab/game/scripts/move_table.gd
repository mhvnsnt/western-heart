## Data-driven Tekken 3 move-table interpreter.
## Reads res://data/moves/<fighter>.json (the 7 existing T3 move files + the full
## extracted T3 rows they reference) and turns each slot into frame data at 60 fps:
##   startup  = active_first             (frames before the hit can connect)
##   active   = active_last - active_first + 1
##   recovery = stream_frames - active_last
##   damage   = T3 damage (T3 life bar = 170)
##   hit_freeze, reaction id come straight from the row.
## Hit/block reactions (Lab rule, documented in lab/README.md):
##   hitstun   = recovery + HIT_ADV[slot]   -> attacker is + on hit
##   blockstun = recovery + BLOCK_ADV[slot] -> light is safe, heavy is minus
class_name MoveTable
extends RefCounted

const SLOTS := ["light", "medium", "heavy", "grab"]
const HIT_ADV := {"light": 8, "medium": 6, "heavy": 10, "grab": 0}
const BLOCK_ADV := {"light": 1, "medium": -2, "heavy": -8, "grab": 0}
const DEFAULT_FREEZE := {"light": 6, "medium": 9, "heavy": 12, "grab": 10}  # Urban Reign 3-12f hit-freeze band
const RANGE_M := {"light": 1.15, "medium": 1.35, "heavy": 1.45, "grab": 0.95}
const KNOCKBACK_M := {"light": 0.15, "medium": 0.30, "heavy": 0.65, "grab": 0.9}

var fighter := ""
var moves := {}        # slot -> Dictionary of frame data
var attack_rows := []  # every T3 attack row (for future command-list mapping)

static func load_fighter(name: String) -> MoveTable:
	var t := MoveTable.new()
	t.fighter = name
	var f := FileAccess.open("res://data/moves/%s.json" % name, FileAccess.READ)
	assert(f != null, "missing move file for %s" % name)
	var d: Dictionary = JSON.parse_string(f.get_as_text())
	t.attack_rows = d.get("attack_rows", [])
	for slot in SLOTS:
		var s: Dictionary = d["summary"][slot]
		var row: Dictionary = d["rows"][str(int(s["t3_row"]))]
		var first := int(row["active_first"]); var last := int(row["active_last"])
		var frames := int(row["stream_frames"])
		var recovery := maxi(frames - last, 1)
		var freeze := int(row.get("hit_freeze", 0))
		if freeze <= 0: freeze = DEFAULT_FREEZE[slot]
		t.moves[slot] = {
			"slot": slot, "t3_row": int(s["t3_row"]),
			"startup": maxi(first, 1), "active": maxi(last - first + 1, 1), "recovery": recovery,
			"total": maxi(first, 1) + maxi(last - first + 1, 1) + recovery,
			"damage": int(row["damage"]), "hit_freeze": freeze, "reaction": int(row.get("reaction", 0)),
			"attack_class": int(row.get("attack_class", 0)),
			"hitstun": recovery + HIT_ADV[slot], "blockstun": maxi(recovery + BLOCK_ADV[slot], 1),
			"range": RANGE_M[slot], "knockback": KNOCKBACK_M[slot],
			"unblockable": slot == "grab", "anim": slot,
		}
	return t

func get_move(slot: String) -> Dictionary:
	return moves[slot]

## Phase of a move at frame n (1-based): "startup" | "active" | "recovery" | "done"
static func phase(m: Dictionary, n: int) -> String:
	if n <= m["startup"]: return "startup"
	if n <= m["startup"] + m["active"]: return "active"
	if n <= m["total"]: return "recovery"
	return "done"

## Normalised animation time (clips: 0.4 = contact, 0.5 = active end, 1.0 = recovered)
static func anim_time(m: Dictionary, n: int) -> float:
	var s: float = m["startup"]; var a: float = m["active"]; var r: float = m["recovery"]
	if n <= s: return 0.4 * n / s
	if n <= s + a: return 0.4 + 0.1 * (n - s) / a
	return minf(0.5 + 0.5 * (n - s - a) / r, 1.0)
