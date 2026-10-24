## Headless test: godot --headless --path lab/game -s res://tests/test_move_table.gd
extends SceneTree

func _init() -> void:
	var fails := 0
	for name in ["king", "jin", "bryan", "heihachi", "xiaoyu", "yoshimitsu", "gunjack"]:
		var t := MoveTable.load_fighter(name)
		var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/moves/%s.json" % name))
		for slot in MoveTable.SLOTS:
			var m := t.get_move(slot)
			var row: Dictionary = raw["rows"][str(m["t3_row"])]
			var ok: bool = m["startup"] == maxi(int(row["active_first"]), 1) and m["damage"] == int(row["damage"]) \
				and m["total"] >= m["startup"] + m["active"] and MoveTable.phase(m, m["startup"] + 1) == "active" \
				and MoveTable.phase(m, m["total"] + 1) == "done" and absf(MoveTable.anim_time(m, m["startup"]) - 0.4) < 1e-4
			if not ok:
				fails += 1; printerr("FAIL ", name, " ", slot, " ", m)
		var l := t.get_move("light")
		print("%-10s light s%d a%d r%d dmg%d | medium s%d dmg%d | heavy s%d a%d r%d dmg%d | %d attack rows" % [name,
			l["startup"], l["active"], l["recovery"], l["damage"], t.get_move("medium")["startup"], t.get_move("medium")["damage"],
			t.get_move("heavy")["startup"], t.get_move("heavy")["active"], t.get_move("heavy")["recovery"], t.get_move("heavy")["damage"], t.attack_rows.size()])
	print("MOVE TABLE TESTS: ", "PASS" if fails == 0 else "FAIL (%d)" % fails)
	quit(1 if fails else 0)
