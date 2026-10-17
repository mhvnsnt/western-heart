## Headless test: godot --headless --path lab/game -s res://tests/test_height_scale.gd
## Scales the real Lab models to every known height and checks the measured mesh height.
extends SceneTree

func _init() -> void:
	var fails := 0; var n := 0
	var db: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(HeightScale.DATA))
	for glb in ["res://assets/t3_king.glb", "res://assets/pantera_leoman.glb"]:
		var model: Node3D = (load(glb) as PackedScene).instantiate()
		root.add_child(model)
		for id in db["characters"]:
			var want := HeightScale.height_cm(id)
			var got := HeightScale.apply(model, id)
			var meas := HeightScale.measure(model) * 100.0
			n += 1
			if want <= 0.0:
				if got != 0.0: fails += 1; printerr("FAIL null height changed ", id)
				continue
			if absf(meas - want) > 0.5:
				fails += 1; printerr("FAIL %s %s want %.1f got %.1f" % [glb, id, want, meas])
		model.queue_free()
	print("HEIGHT SCALE TESTS (%d cases): %s" % [n, "PASS" if fails == 0 else "FAIL (%d)" % fails])
	quit(1 if fails else 0)
