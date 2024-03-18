
import glob
import json
import time
import re
import warnings

dict_actions_v = {}
dict_predicates_v = {}
dict_objects_v =  {}

dict_actions_v['move'] = (
    ["pos", "pos"],
    ["at-robot 0", "connected 0 1"],
    ["at-robot 1", "visited 1"],
    ["at-robot 0"]
)
dict_predicates_v["connected"] = (["ob", "pos"], ["ob", "pos"])
dict_predicates_v["place"] = (["ob"])
dict_predicates_v["at-robot"] = (["ob", "pos"])
dict_predicates_v["visited"] = (["ob", "pos"])

dict_objects_v["pos"] = ["loc-x-y"]


dict_actions_l = {}
dict_predicates_l = {}
dict_objects_l =  {}
dict_actions_l['load-truck'] = (
    ["package", "truck", "place"],
    ["at 0 2", "at 1 2"],
    ["in 0 1"],
    ["at 0 2"]
)
dict_actions_l['load-airplane'] = (
    ["package", "airplane", "airport"],
    ["at 0 2", "at 1 2"],
    ["in 0 1"],
    ["at 0 2"]
)
dict_actions_l['unload-truck'] = (
    ["package", "truck", "place"],
    ["at 1 2", "in 0 1"],
    ["at 0 2"],
    ["in 0 1"],
)
dict_actions_l['unload-airplane'] = (
    ["package", "airplane", "airport"],
    ["at 1 2", "in 0 1"],
    ["at 0 2"],
    ["in 0 1"]
)
dict_actions_l['drive-truck'] = (
    ["truck", "place", "place", "city"],
    ["at 0 1", "in-city 1 3", "in-city 2 3"],
    ["at 0 2"],
    ["at 0 1"]
)
dict_actions_l['fly-airplane'] = (
    ["airplane", "airport", "airport"],
    ["at 0 1"],
    ["at 0 2"],
    ["at 0 1"]
)

dict_predicates_l["at"] = (
    ["package", "airplane", "truck"],
    ["place", "airport"]
    )
dict_predicates_l["in-city"] = (
    ["place", "airport", "package", "airplane", "truck"],
    ["city"]
)
dict_predicates_l["in"] = (
    ["package",],
    ["airplane", "truck"]
)


dict_predicates_l["location"] = (["ob"])
dict_predicates_l["city"] = (["ob"])
dict_predicates_l["airport"] = (["ob"])
dict_predicates_l["truck"] = (["ob"])
dict_predicates_l["airplane"] = (["ob"])
dict_predicates_l["package"] = (["ob"])
dict_predicates_l["obj"] = (["ob"])
dict_predicates_l["vehicle"] = (["ob"])


dict_objects_l["package"] = ["obj"]
dict_objects_l["airplane"] = ["apn"]
dict_objects_l["truck"] = ["tru"]
dict_objects_l["city"] = ["cit"]
dict_objects_l["place"] = ["l", "pos", "apt"]
dict_objects_l["airport"] = ["l","pos", "apt"]

dict_actions_dr = {}
dict_predicates_dr = {}
dict_objects_dr =  {}
dict_actions_dr['load-truck'] = (
    ["obj", "truck", "location"],
    ["at 0 2", "at 1 2"],
    ["in 0 1"],
    ["at 0 2"]
)
dict_actions_dr['unload-truck'] = (
    ["obj", "truck", "location"],
    ["at 1 2", "in 0 1"],
    ["at 0 2"],
    ["in 0 1"]
)
dict_actions_dr['board-truck'] = (
    ["driver", "truck", "location"],
    ["at 1 2", "at 0 2", "empty 1"],
    ["driving 0 1"],
    ["at 0 2", "empty 1"]
)
dict_actions_dr['disembark-truck'] = (
    ["driver", "truck", "location"],
    ["at 1 2", "driving 0 1"],
    ["at 0 2", "empty 1"],
    ["driving 0 1"]
)
dict_actions_dr['drive-truck'] = (
    ["truck", "location", "location", "driver"],
    ["at 0 1", "driving 3 0", "link 1 2"],
    ["at 0 2"],
    ["at 0 1"]
)
dict_actions_dr['walk'] = (
    ["driver", "location", "location"],
    ["at 0 1", "path 1 2"],
    ["at 0 2"],
    ["at 0 1"]
)

dict_predicates_dr["at"] = (
    ["obj", "airplane", "truck"],
    ["location"]
    )
dict_predicates_dr["in"] = (
    ["obj"],
    ["truck"]
    )
dict_predicates_dr["driving"] = (
    ["driver"],
    ["truck"]
    )
dict_predicates_dr["link"] = (
    ["location"],
    ["location"]
    )
dict_predicates_dr["path"] = (
    ["location"],
    ["location"]
    )
dict_predicates_dr["empty"] = (
    ["truck"],
    )

dict_predicates_dr["location"] = (["ob"])
dict_predicates_dr["obj"] = (["ob"])
dict_predicates_dr["driver"] = (["ob"])
dict_predicates_dr["truck"] = (["ob"])

dict_objects_dr["location"] = ["s","p-", "p"]
dict_objects_dr["locatable"] = ["driver", "truck", "package"]
dict_objects_dr["driver"] = ["driver"]
dict_objects_dr["truck"] = ["truck"]
dict_objects_dr["obj"] = ["package"]

dict_actions_z = {}
dict_predicates_z = {}
dict_objects_z =  {}

dict_actions_z['board'] = (
    ["person", "aircraft", "city"],
    ["at 0 2", "at 1 2"],
    ["in 0 1"],
    ["at 0 2"]
)
dict_actions_z['debark'] = (
    ["person", "aircraft", "city"],
    ["in 0 1", "at 1 2"],
    ["at 0 2"],
    ["in 0 1"]
)
dict_actions_z['fly'] = (
    ["aircraft", "city", "city", "flevel", "flevel"],
    ["at 0 1", "fuel-level 0 3", "next 4 3"],
    ["at 0 2", "fuel-level 0 4"],
    ["at 0 1", "fuel-level 0 3"]
)
dict_actions_z['zoom'] = (
    ["aircraft", "city", "city", "flevel", "flevel", "flevel"],
    ["at 0 1", "fuel-level 0 3", "next 4 3", "next 5 4"],
    ["at 0 2", "fuel-level 0 5"],
    ["at 0 1", "fuel-level 0 3"]
)
dict_actions_z['refuel'] = (
    ["aircraft", "city", "flevel", "flevel"],
    ["fuel-level 0 2", "next 2 3", "at 0 1"],
    ["fuel-level 0 3"],
    ["fuel-level 0 2"]
)

dict_predicates_z["at"] = (
    ["person", "aircraft"],
    ["city"]
)
dict_predicates_z["in"] = (
    ["person"],
    ["aircraft"]
)
dict_predicates_z["fuel-level"] = (
    ["flevel"],
    ["aircraft"]
)
dict_predicates_z["next"] = (
    ["flevel"],
    ["flevel"]
)

dict_predicates_z["aircraft"] = (["ob"])
dict_predicates_z["person"] = (["ob"])
dict_predicates_z["city"] = (["ob"])
dict_predicates_z["flevel"] = (["ob"])

dict_objects_z["aircraft"] = ["plane"]
dict_objects_z["person"] = ["person"]
dict_objects_z["city"] = ["city"]
dict_objects_z["flevel"] = ["fl"]

dict_actions_de = {}
dict_predicates_de = {}
dict_objects_de =  {}

dict_actions_de['drive'] = (
    ["truck", "place", "place"],
    ["at 0 1"],
    ["at 0 2"],
    ["at 0 1"]
)
dict_actions_de['lift'] = (
    ["hoist", "crate", "surface", "place"],
    ["at 0 3", "available 0", "at 1 3", "on 1 2", "clear 1"],
    ["lifting 0 1", "clear 2"],
    ["at 1 3", "clear 1", "available 0", "on 1 2"]
)
dict_actions_de['drop'] = (
    ["hoist", "crate", "surface", "place"],
    ["at 0 3", "at 2 3", "clear 2", "lifting 0 1"],
    ["available 0", "at 1 3", "clear 1", "on 1 2"],
    ["lifting 0 1", "clear 2"]
)
dict_actions_de['load'] = (
    ["hoist", "crate", "truck", "place"],
    ["at 0 3", "at 2 3", "lifting 0 1"],
    ["in 1 2", "available 0"],
    ["lifting 0 1"]
)
dict_actions_de['unload'] = (
    ["hoist", "crate", "truck", "place"],
    ["at 0 3", "at 2 3", "available 0", "in 1 2"],
    ["lifting 0 1"],
    ["in 1 2", "available 0"]
)

dict_predicates_de["at"] = (
    ["truck","hoist", "pallet", "crate"],
    ["distributor", "depot"]
)
dict_predicates_de["on"] = (
    ["crate"],
    ["pallet", "crate"]
)
dict_predicates_de["in"] = (
    ["crate"],
    ["truck"]
)
dict_predicates_de["lifting"] = (
    ["hoist"],
    ["crate"]
)
dict_predicates_de["available"] = (
    ["hoist"],
)
dict_predicates_de["clear"] = (
    ["pallet", "crate"]
)
dict_predicates_de['hoist'] = (['ob'])
dict_predicates_de['truck'] = (['ob'])
dict_predicates_de['pallet'] = (['ob'])
dict_predicates_de['crate'] = (['ob'])
dict_predicates_de['distributor'] = (['ob'])
dict_predicates_de['depot'] = (['ob'])


dict_objects_de["place"] = ["distributor", "depot"]
dict_objects_de["locatable"] = ["truck","hoist", "pallet", "crate"]
dict_objects_de["object"] = ["distributor", "depot", "truck", "hoist", "pallet", "crate"]
dict_objects_de["surface"] = ["pallet", "crate"]
dict_objects_de["truck"] = ["truck"]
dict_objects_de["hoist"] = ["hoist"]
dict_objects_de["pallet"] = ["pallet"]
dict_objects_de["crate"] = ["crate"]
dict_objects_de["distributor"] = ["distributor"]
dict_objects_de["depot"] = ["depot"]

dict_actions_b = {}
dict_predicates_b = {}
dict_objects_b =  {}

dict_actions_b['pickup'] = (
    ["ob"],
    ["clear 0", "on-table 0", "arm-empty"],
    ["holding 0"],
    ["clear 0", "on-table 0", "arm-empty"]
)
dict_actions_b['putdown'] = (
    ["ob"],
    ["holding 0"],
    ["clear 0", "on-table 0", "arm-empty"],
    ["holding 0"]
)
dict_actions_b['stack'] = (
    ["ob", "ob"],
    ["clear 1", "holding 0"],
    ["clear 0", "on 0 1", "arm-empty"],
    ["clear 1", "holding 0"]
)
dict_actions_b['unstack'] = (
    ["ob", "ob"],
    ["clear 0", "on 0 1", "arm-empty"],
    ["clear 1", "holding 0"],
    ["clear 0", "on 0 1", "arm-empty"]
)

dict_predicates_b["clear"] = (
    ["ob"],
)
dict_predicates_b["on-table"] = (
    ["ob"],
)
dict_predicates_b["holding"] = (
    ["ob"],
)
dict_predicates_b["on"] = (
    ["ob", "ob"],
)
dict_predicates_b["arm-empty"] = (
    [""],
)


#dict_objects_b["ob"] = ["a", "b", "c", "d", "e", "f", "g", "h", "i","j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
#                        "w", "x", "y", "z"]
dict_objects_b["ob"] = ["b"]


dict_actions_s_invariant = {}
dict_actions_s_normal = {}
dict_predicates_s = {}
dict_objects_s =  {}

dict_actions_s_invariant['turn-to'] = (
    ["ob", "ob", "ob"],
    ["satellite 0", "direction 1", "direction 2", "pointing 0 2"],
    ["pointing 0 1"],
    ["pointing 0 2"]
)
dict_actions_s_invariant['switch-on'] = (
    ["ob", "ob"],
    ["instrument 0", "satellite 1", "on-board 0 1", "power-avail 1"],
    ["power-on 0"],
    ["power-avail 1", "calibrated 0"]
)
dict_actions_s_invariant['switch-off'] = (
    ["ob", "ob"],
    ["instrument 0", "satellite 1", "on-board 0 1", "power-on 0"],
    ["power-avail 1"],
    ["power-on 0"]
)
dict_actions_s_invariant['calibrate'] = (
    ["ob", "ob", "ob"],
    ["satellite 0", "instrument 1", "direction 2", "on-board 1 0", "calibration-target 1 2", "pointing 0 2", "power-on 1"],
    ["calibrated 1"],
    [""]
)
dict_actions_s_invariant['take-image'] = (
    ["ob", "ob", "ob", "ob"],
    ["satellite 0", "direction 1", "instrument 2", "mode 3", "calibrated 2", "on-board 2 0", "supports 2 3", "power-on 2", "pointing 0 1"],
    ["have-image 1 3"],
    [""]
)

dict_actions_s_normal['turn-to'] = (
    ["ob", "ob", "ob"],
    ["pointing 0 2"],
    ["pointing 0 1"],
    ["pointing 0 2"]
)
dict_actions_s_normal['switch-on'] = (
    ["ob", "ob"],
    ["on-board 0 1", "power-avail 1"],
    ["power-on 0"],
    ["power-avail 1", "calibrated 0"]
)
dict_actions_s_normal['switch-off'] = (
    ["ob", "ob"],
    ["on-board 0 1", "power-on 0"],
    ["power-avail 1"],
    ["power-on 0"]
)
dict_actions_s_normal['calibrate'] = (
    ["ob", "ob", "ob"],
    ["on-board 1 0", "calibration-target 1 2", "pointing 0 2", "power-on 1"],
    ["calibrated 1"],
    [""]
)
dict_actions_s_normal['take-image'] = (
    ["ob", "ob", "ob", "ob"],
    ["calibrated 2", "on-board 2 0", "supports 2 3", "power-on 2", "pointing 0 1"],
    ["have-image 1 3"],
    [""]
)

dict_predicates_s["on-board"] = (
    ["ob", "ob"],
)
dict_predicates_s["supports"] = (
    ["ob", "ob"],
)
dict_predicates_s["pointing"] = (
    ["ob", "ob"],
)
dict_predicates_s["have-image"] = (
    ["ob", "ob"],
)
dict_predicates_s["calibration-target"] = (
    ["ob", "ob"],
)
dict_predicates_s["power-avail"] = (
    ["ob"],
)
dict_predicates_s["power-on"] = (
    ["ob"],
)
dict_predicates_s["calibrated"] = (
    ["ob"],
)
dict_predicates_s["satellite"] = (
    ["ob"],
)
dict_predicates_s["direction"] = (
    ["ob"],
)
dict_predicates_s["instrument"] = (
    ["ob"],
)
dict_predicates_s["mode"] = (
    ["ob"],
)

convert_action_s = {}
convert_action_s['switch_on'] = 'switch-on'
convert_action_s['switch_off'] = 'switch-off'
convert_action_s['take_image'] = 'take-image'
convert_action_s['turn_to'] = 'turn-to'

dict_objects_s["ob"] = ["satellite","instrument", "direction", "mode"]


# Sokoban

dict_actions_so = {}
dict_predicates_so = {}
dict_objects_so =  {}

dict_objects_so["loc"] = ["f-f"]
dict_objects_so["dir"] = ["down", "up", "left", "right"]
dict_objects_so["box"] = ["box"]

dict_predicates_so["at-robot"] = (
    ["loc"]
    )
dict_predicates_so["at"] = (
    ["box"],
    ["loc"]
)
dict_predicates_so["clear"] = (
    ["loc"]
    )
dict_predicates_so["adjacent"] = (
    ["loc"],
    ["loc"],
    ["dir"]
)

dict_actions_so['move'] = (
    ["loc", "loc", "dir"], #oggetti
    ["at-robot 0", "clear 1", "adjacent 0 1 2"],  #precondizioni
    ["at-robot 1"], #addtitivi
    ["at-robot 0"] #sottrattivi
)

dict_actions_so['push'] = (
    ["loc", "loc", "loc", "dir", "box"], #oggetti
    ["at-robot 0", "at 4 1", "clear 2", "adjacent 0 1 3", "adjacent 1 2 3"],
    ["at-robot 1", "at 4 2", "clear 1"],
    ["at-robot 0", "at 4 1", "clear 2"]
)

dict_predicates_so["loc"] = (["ob"])
dict_predicates_so["dir"] = (["ob"])
dict_predicates_so["box"] = (["ob"])

# Floortile

dict_actions_f = {}
dict_predicates_f = {}
dict_objects_f =  {}

dict_objects_f["tile"] = ["tile--"]
dict_objects_f["robot"] = ["robot"]
dict_objects_f["color"] = ["white", "black"]

dict_predicates_f["robot-at"] = (
    ["robot"],
    ["tile"]
    )
dict_predicates_f["up"] = (
    ["tile"],
    ["tile"]
    )
dict_predicates_f["down"] = (
    ["tile"],
    ["tile"]
    )
dict_predicates_f["right"] = (
    ["tile"],
    ["tile"]
    )
dict_predicates_f["left"] = (
    ["tile"],
    ["tile"]
    )
dict_predicates_f["clear"] = (
    ["tile"],
)
dict_predicates_f["painted"] = (
    ["tile"],
    ["color"]
    )
dict_predicates_f["robot-has"] = (
    ["robot"],
    ["color"],
)
dict_predicates_f["available-color"] = (
    ["color"],
)
dict_predicates_f["free-color"] = (
    ["robot"],
)

dict_predicates_f["robot"] = (["robot"])
dict_predicates_f["tile"] = (["tile"])
dict_predicates_f["color"] = (["color"])

dict_actions_f['change-color'] = (
    ["robot", "color", "color"], #oggetti
    ["robot-has 0 1", "available-color 2"],  #precondizioni
    ["robot-has 0 2"], #addtitivi
    ["robot-has 0 1"] #sottrattivi
)

dict_actions_f['paint-up'] = (
    ["robot", "tile", "tile", "color"], #oggetti
    ["robot-has 0 3", "robot-at 0 2", "up 1 2", "clear 1"],
    ["painted 1 3"],
    ["clear 1"]
)

dict_actions_f['paint-down'] = (
    ["robot", "tile", "tile", "color"], #oggetti
    ["robot-has 0 3", "robot-at 0 2", "down 1 2", "clear 1"],
    ["painted 1 3"],
    ["clear 1"]
)

dict_actions_f['move-up'] = (
    ["robot", "tile", "tile"], #oggetti
    ["robot-at 0 1", "up 2 1", "clear 2"],
    ["robot-at 0 2", "clear 1"],
    ["robot-at 0 1", "clear 2"]
)

dict_actions_f['move-down'] = (
    ["robot", "tile", "tile"], #oggetti
    ["robot-at 0 1", "down 2 1", "clear 2"],
    ["robot-at 0 2", "clear 1"],
    ["robot-at 0 1", "clear 2"]
)

dict_actions_f['move-right'] = (
    ["robot", "tile", "tile"], #oggetti
    ["robot-at 0 1", "right 2 1", "clear 2"],
    ["robot-at 0 2", "clear 1"],
    ["robot-at 0 1", "clear 2"]
)

dict_actions_f['move-left'] = (
    ["robot", "tile", "tile"], #oggetti
    ["robot-at 0 1", "left 2 1", "clear 2"],
    ["robot-at 0 2", "clear 1"],
    ["robot-at 0 1", "clear 2"]
)

# ChildSnack

dict_actions_c = {}
dict_predicates_c = {}
dict_objects_c =  {}

dict_objects_c["child"] = ["child"]
dict_objects_c["bread-portion"] = ["bread"]
dict_objects_c["content-portion"] = ["content"]
dict_objects_c["place"] = ["table", "kitchen"]
dict_objects_c["tray"] = ["tray"]
dict_objects_c["sandwich"] = ["sandw"]

dict_predicates_c["at-kitchen-bread"] = (
    ["bread-portion"]
    )
dict_predicates_c["at-kitchen-content"] = (
    ["content-portion"]
    )
dict_predicates_c["at-kitchen-sandwich"] = (
    ["sandwich"]
    )
dict_predicates_c["no-gluten-bread"] = (
    ["bread-portion"]
    )
dict_predicates_c["no-gluten-content"] = (
    ["content-portion"]
    )
dict_predicates_c["no-gluten-sandwich"] = (
    ["sandwich"]
    )
dict_predicates_c["ontray"] = (
    ["sandwich"],
    ["tray"]
    )
dict_predicates_c["allergic-gluten"] = (
    ["child"]
    )
dict_predicates_c["not-allergic-gluten"] = (
    ["child"]
    )
dict_predicates_c["served"] = (
    ["child"]
    )
dict_predicates_c["waiting"] = (
    ["child"],
    ["place"]
    )
dict_predicates_c["at"] = (
    ["tray"],
    ["place"]
    )
dict_predicates_c["notexist"] = (
    ["sandwich"],
    )
#dict_predicates_c["kitchen"] = (["tray"],)

dict_predicates_c["child"] = (["child"])
dict_predicates_c["tray"] = (["tray"])
dict_predicates_c["place"] = (["place", "table", "kitchen"])
dict_predicates_c["sandwich"] = (["sandwich"])
dict_predicates_c["content-portion"] = (["content-portion"])
dict_predicates_c["bread-portion"] = (["bread-portion"])

dict_actions_c['make-sandwich-no-gluten'] = (
    ["sandwich", "bread-portion", "content-portion"], #oggetti
    ["at-kitchen-bread 1", "at-kitchen-content 2", "no-gluten-bread 1", "no-gluten-content 2", "notexist 0"],  #precondizioni
    ["at-kitchen-sandwich 0", "no-gluten-sandwich 0"], #addtitivi
    ["at-kitchen-bread 1", "at-kitchen-content 2", "notexist 0"] #sottrattivi
)

dict_actions_c['make-sandwich'] = (
    ["sandwich", "bread-portion", "content-portion"], #oggetti
    ["at-kitchen-bread 1", "at-kitchen-content 2", "notexist 0"],  #precondizioni
    ["at-kitchen-sandwich 0"], #addtitivi
    ["at-kitchen-bread 1", "at-kitchen-content 2", "notexist 0"] #sottrattivi
)

dict_actions_c['put-on-tray'] = (
    ["sandwich", "tray",], #oggetti
    ["at-kitchen-sandwich 0"],
    #["at-kitchen-sandwich 0", "at 1 2"],  #precondizioni
    ["ontray 0 1"], #addtitivi
    ["at-kitchen-sandwich 0"] #sottrattivi
)

dict_actions_c["serve-sandwich-no-gluten"] = (
    ["sandwich", "child", "tray", "place"], #oggetti
    ["allergic-gluten 1", "ontray 0 2", "waiting 1 3", "no-gluten-sandwich 0", "at 2 3"],  #precondizioni
    ["served 1"], #addtitivi
    ["ontray 0 2"] #sottrattivi
)

dict_actions_c["serve-sandwich"] = (
    ["sandwich", "child", "tray", "place"], #oggetti
    ["not-allergic-gluten 1", "ontray 0 2", "waiting 1 3", "at 2 3"],  #precondizioni
    ["served 1"], #addtitivi
    ["ontray 0 2"] #sottrattivi
)

dict_actions_c["move-tray"] = (
    ["tray", "place", "place"], #oggetti
    ["at 0 1"],  #precondizioni
    ["at 0 2"], #addtitivi
    ["at 0 1"] #sottrattivi
)

#### ROVERS
dict_actions_r = {}
dict_predicates_r = {}
dict_objects_r =  {}

dict_objects_r["rover"] = ["rover"]
dict_objects_r["waypoint"] = ["waypoint"]
dict_objects_r["store"] = ["store"]
dict_objects_r["camera"] = ["camera"]
dict_objects_r["mode"] = ["mode", "high-res", "low-res", "colour"]
dict_objects_r["lander"] = ["lander", "general"]
dict_objects_r["objective"] = ["objective"]

dict_predicates_r["rover"] = (["rover"])
dict_predicates_r["waypoint"] = (["waypoint"])
dict_predicates_r["store"] = (["store"])
dict_predicates_r["camera"] = (["camera"])
dict_predicates_r["mode"] = (["mode"])
dict_predicates_r["lander"] = (["lander"])
dict_predicates_r["objective"] = (["objective"])

dict_predicates_r["at"] = ( #at_rover?
    ["rover"], ["waypoint"])
dict_predicates_r["at-lander"] = (
    ["lander"], ["waypoint"])
dict_predicates_r["can-traverse"] = (
    ["rover"], ["waypoint"], ["waypoint"])
dict_predicates_r["equipped-for-soil-analysis"] = (
    ["rover"])
dict_predicates_r["equipped-for-rock-analysis"] = (
    ["rover"])
dict_predicates_r["equipped-for-imaging"] = (
    ["rover"])
dict_predicates_r["empty"] = (
    ["store"])
dict_predicates_r["full"] = (
    ["store"])
dict_predicates_r["have-rock-analysis"] = (
    ["rover"], ["waypoint"])
dict_predicates_r["have-soil-analysis"] = (
    ["rover"], ["waypoint"])
dict_predicates_r["calibrated"] = (
    ["camera"], ["rover"])
dict_predicates_r["supports"] = (
    ["camera"], ["mode"])
dict_predicates_r["visible"] = (
    ["waypoint"], ["waypoint"])
dict_predicates_r["have-image"] = (
    ["rover"], ["objective"], ["mode"])
dict_predicates_r["communicated-soil-data"] = (
    ["waypoint"])
dict_predicates_r["communicated-rock-data"] = (
    ["waypoint"])
dict_predicates_r["communicated-image-data"] = (
    ["objective"], ["mode"])
dict_predicates_r["at-soil-sample"] = (
    ["waypoint"])
dict_predicates_r["at-rock-sample"] = (
    ["waypoint"])
dict_predicates_r["visible-from"] = (
    ["objective"], ["waypoint"])
dict_predicates_r["store-of"] = (
    ["store"], ["rover"])
dict_predicates_r["calibration-target"] = (
    ["camera"], ["objective"])
dict_predicates_r["on-board"] = (
    ["camera"], ["rover"])

dict_actions_r["navigate"] = (
    ["rover", "waypoint", "waypoint"], #oggetti
    ["can-traverse 0 1 2", "at 0 1", "visible 1 2"],  #precondizioni
    ["at 0 2"], #addtitivi
    ["at 0 1"] #sottrattivi
)
dict_actions_r["sample-soil"] = (
    ["rover", "store", "waypoint"], #oggetti
    ["at 0 2", "at-soil-sample 2", "equipped-for-soil-analysis 0", "store-of 1 0", "empty 1"],  #precondizioni
    ["full 1", "have-soil-analysis 0 2"], #addtitivi
    ["empty 1", "at-soil-sample 2"] #sottrattivi
)
dict_actions_r["sample-rock"] = (
    ["rover", "store", "waypoint"], #oggetti
    ["at 0 2", "at-rock-sample 2", "equipped-for-rock-analysis 0", "store-of 1 0", "empty 1"],  #precondizioni
    ["full 1", "have-rock-analysis 0 2"], #addtitivi
    ["empty 1", "at-rock-sample 2"] #sottrattivi
)
dict_actions_r["drop"] = (
    ["rover", "store"], #oggetti
    ["store-of 1 0", "full 1"], #precondizioni
    ["empty 1"], #additivi
    ["full 1"] #sottrattivi
)
dict_actions_r["calibrate"] = (
    ["rover", "camera", "objective", "waypoint"], #oggetti
    ["equipped-for-imaging 0", "calibration-target 1 2", "at 0 3", "visible-from 2 3", "on-board 1 0"], #precondizioni
    ["calibrated 1 0"], #additivi
    [] #sottrattivi
)
dict_actions_r["take-image"] = (
    ["rover", "waypoint", "objective", "camera", "mode"], #oggetti
    ["calibrated 3 0", "on-board 3 0", "equipped-for-imaging 0", "supports 3 4", "visible-from 2 1", "at 0 1"], #precondizioni
    ["have-image 0 2 4"], #additivi
    ["calibrated 3 0"] #sottrattivi
)
dict_actions_r["communicate-soil-data"] = (
    ["rover", "lander", "waypoint", "waypoint", "waypoint"], #oggetti
    ["at 0 3", "at-lander 1 4", "have-soil-analysis 0 2", "visible 3 4"], #precondizioni
    ["communicated-soil-data 2"], #additivi
    [] #sottrattivi
)
dict_actions_r["communicate-rock-data"] = (
    ["rover", "lander", "waypoint", "waypoint", "waypoint"], #oggetti
    ["at 0 3", "at-lander 1 4", "have-rock-analysis 0 2", "visible 3 4"], #precondizioni
    ["communicated-rock-data 2"], #additivi
    [] #sottrattivi
)
dict_actions_r["communicate-image-data"] = (
    ["rover", "lander", "objective", "mode", "waypoint", "waypoint"], #oggetti
    ["at 0 4", "at-lander 1 5", "have-image 0 2 3", "visible 4 5"], #precondizioni
    ["communicated-image-data 2 3"], #additivi
    [] #sottrattivi
)

dict_actions_domain = {}
dict_predicates_domain = {}
dict_objects_domain =  {}
convert_action_domain = {}

dict_actions_domain['logistics'] = dict_actions_l
dict_predicates_domain['logistics'] = dict_predicates_l
dict_objects_domain['logistics'] = dict_objects_l
convert_action_domain['logistics'] = {}

dict_actions_domain['driverlog'] = dict_actions_dr
dict_predicates_domain['driverlog'] = dict_predicates_dr
dict_objects_domain['driverlog'] = dict_objects_dr
convert_action_domain['driverlog'] = {}

dict_actions_domain['zenotravel'] = dict_actions_z
dict_predicates_domain['zenotravel'] = dict_predicates_z
dict_objects_domain['zenotravel'] = dict_objects_z
convert_action_domain['zenotravel'] = {}

dict_actions_domain['blocksworld'] = dict_actions_b
dict_predicates_domain['blocksworld'] = dict_predicates_b
dict_objects_domain['blocksworld'] = dict_objects_b
convert_action_domain['blocksworld'] = {}

dict_actions_domain['depots'] = dict_actions_de
dict_predicates_domain['depots'] = dict_predicates_de
dict_objects_domain['depots'] = dict_objects_de
convert_action_domain['depots'] = {}

dict_actions_domain['satellite'] = dict_actions_s_invariant
dict_predicates_domain['satellite'] = dict_predicates_s
dict_objects_domain['satellite'] = dict_objects_s
convert_action_domain['satellite'] = convert_action_s


dict_actions_domain['sokoban'] = dict_actions_so
dict_predicates_domain['sokoban'] = dict_predicates_so
dict_objects_domain['sokoban'] = dict_objects_so
convert_action_domain['sokoban'] = {}

dict_actions_domain['floortile'] = dict_actions_f
dict_predicates_domain['floortile'] = dict_predicates_f
dict_objects_domain['floortile'] = dict_objects_f
convert_action_domain['floortile'] = {}

dict_actions_domain['childsnack'] = dict_actions_c
dict_predicates_domain['childsnack'] = dict_predicates_c
dict_objects_domain['childsnack'] = dict_objects_c
convert_action_domain['childsnack'] = {}


dict_actions_domain['visitall'] = dict_actions_v
dict_predicates_domain['visitall'] = dict_predicates_v
dict_objects_domain['visitall'] = dict_objects_v
convert_action_domain['visitall'] = {}

dict_actions_domain['rovers'] = dict_actions_r
dict_predicates_domain['rovers'] = dict_predicates_r
dict_objects_domain['rovers'] = dict_objects_r
convert_action_domain['rovers'] = {}

def unite_actions(input, keywords, domain, separator="_"):
    for conversion in convert_action_domain[domain].keys():
        input = input.replace(conversion, convert_action_domain[domain][conversion])
    list_to_unite = input.split()
    index_actions = []
    for idx,token in enumerate(list_to_unite):
        if token in keywords:
            index_actions.append(idx)
    index_actions.append(len(list_to_unite))
    new_list = []
    for i in range(len(index_actions)-1):
        new_action = " ".join(list_to_unite[index_actions[i]:index_actions[i+1]])
        new_list.append(new_action.replace(" ",separator))
    return new_list
# parto dal mio stato iniziale
# cerco i miei oggetti e li categorizzo
# loop sul mio stato
# prendo la mia prima azione
# controllo se soddisfa le mie precondizioni
#   se non soddisfa ERRORE
# applico gli effetti positivi
# applico gli effetti negativi (ho terminato di aggiornare il mio stato)
# controllo se ho soddisfatto i goals
# ripeto fino a soddisfazione goals, fine azioni o azione violata

def create_starting_structures(plan, domain):
    initial_states = plan['input'].split("<|goals|>")[0].strip().split("<|startofplan|>")[1].strip()
    goal_states = plan['input'].split("<|goals|>")[1].strip().split("<|actions|>")[0].strip()
    initial_states = unite_actions(initial_states, list(dict_predicates_domain[domain].keys()), domain)
    goal_states = unite_actions(goal_states, list(dict_predicates_domain[domain].keys()), domain)
    actions = unite_actions(plan["actions"], list(dict_actions_domain[domain].keys()), domain)
        
    dict_states = {}
    dict_goals = {}
    for init_state in initial_states:
        dict_states[init_state] = True
    for goal_state in goal_states:
        if goal_state in initial_states:
            dict_goals[goal_state] = True
        else:
            dict_goals[goal_state] = False
    return (dict_states, dict_goals, actions)

def execute_action(states, action, domain):
    # Return a Tuple
    # in the first position the result True, False
    # in the second position the next state if result is True or the current state if it is False
    # in the third position the motivation of the wrong execution
    # split my action, on position 0 the action, then the objects
    #print(action)
    splitted_action = action.split("_")[0] # prendo il nome della mia azione
    try:
        action_parameter = dict_actions_domain[domain][splitted_action] # verifico che l'azione esiste
    except:
        action_parameter = None
    if action_parameter is None:
        return (False, states,"action_name_wrong", splitted_action, action, "")
    splitted_objects = action.split("_")[1:] # ottengo il nome dei miei oggetti definiti nel mio problema
    action_objects = action_parameter[0] # ottengo gli oggetti accettati dall'azione
    if len(action_objects) == len(splitted_objects): # verifico che gli oggetti siano in egual numero rispetto a quanti ne richiede la mia azione
        for i in range(0, len(action_objects)): # scorro i miei oggetti
            obj_nonumber = ''.join([j for j in splitted_objects[i] if not j.isdigit()]) # calcolo il mio nome dell'oggetto senza tener conto dei numeri
            if obj_nonumber not in dict_objects_domain[domain][action_objects[i]]: # verifico che l'oggetto si trovi nella lista di nomi possibili associata alla descrizione dell'azione
                return (False, states, "object_name_wrong", splitted_action, obj_nonumber, splitted_objects[i])
    else:
        return (False, states, "object_number_wrong", splitted_action, len(action_objects), len(splitted_objects))
    
    action_prec = action_parameter[1] # prendo le precondizioni della mia azione
    violed_precondtion = False
    violed_preconditions_list = []
    violed_preconditions_list_nonumber = []
    for prec in action_prec: # scorro le mie precondizioni
        prec_list = prec.split(" ")
        prec_parametrized = "" + prec_list[0] # metto il mio predicato
        for obj in prec_list[1:]: # scorro gli oggetti della mia precondizione
            prec_parametrized = prec_parametrized + "_" + splitted_objects[int(obj)] # sostituisco gli oggetti generici ai miei oggetti del problema
        if prec_parametrized not in states.keys(): # controllo se la mia precondizione esiste come chiave del dizionario (se non esiste non è vera)
            violed_precondtion = True
            violed_preconditions_list.append(prec_parametrized)
            violed_preconditions_list_nonumber.append(rimuovi_numeri(prec_parametrized))
        elif states[prec_parametrized] is False: # controllo che la mia precondizione sia vera per eseguire l'azione
            violed_precondtion = True
            violed_preconditions_list.append(prec_parametrized)
            violed_preconditions_list_nonumber.append(rimuovi_numeri(prec_parametrized))
        else:
            pass
    if violed_precondtion is True:
        return (False, states, "violed_preconditions", violed_preconditions_list_nonumber, violed_preconditions_list, splitted_action) 
        
    # eseguo gli effetti negativi
    action_neg = action_parameter[3] # prendo i miei effetti negativi
    for neg in action_neg: # li scorro
        neg_list = neg.split(" ") 
        neg_parametrized = "" + neg_list[0] # ottengo il mio predicato
        for obj in neg_list[1:]: # per ogni oggetto (rappresentato come indice)
            neg_parametrized = neg_parametrized + "_" + splitted_objects[int(obj)] # vado a sostituirlo col corrispettivo dell'azione in corso
        states[neg_parametrized] = False # cambio il valore nei miei stati
        #print("ho reso falso " + neg_parametrized)

    # eseguo gli effetti additivi
    action_plus = action_parameter[2] # prendo i miei effetti additivi
    for plus in action_plus: # li scorro
        plus_list = plus.split(" ")
        plus_parametrized = "" + plus_list[0] # ottengo il mio predicato
        for obj in plus_list[1:]: # per ogni oggetto (rappresentato come indice)
            plus_parametrized = plus_parametrized + "_" + splitted_objects[int(obj)] # vado a sostituirlo col corrispettivo dell'azione in corso
        states[plus_parametrized] = True # cambio il valore nei miei stati
        #print("ho reso vero " + plus_parametrized)
    
    return (True, states, "action_succesfull")

def check_goals(states, goal_states, domain):
    all_goals_satisfied = True
    goals_unsatisfied_list = []
    goals_unsatisfied_list_nonumber = []
    #print(goal_states)
    for goal in goal_states.keys():
        #print("Analizzo il goal " + goal)
        if goal not in states.keys():
            goal_states[goal] = False
            all_goals_satisfied = False
            goals_unsatisfied_list.append(goal)
            goals_unsatisfied_list_nonumber.append(rimuovi_numeri(goal))
            #print("Il mio goal non è negli stati visti")
        elif states[goal] is False:
            goal_states[goal] = False
            all_goals_satisfied = False
            goals_unsatisfied_list.append(goal)
            goals_unsatisfied_list_nonumber.append(rimuovi_numeri(goal))
            #print("Il mio goal è negli stati visti falso")
        else:
            goal_states[goal] = True
            #print("Il mio goal è negli stati visti vero")
    if all_goals_satisfied is True:
        return (True, goal_states, "goals_succesfull")
    else:
        return (False, goal_states, "goals_not_succesfull", goals_unsatisfied_list_nonumber, goals_unsatisfied_list)

def parse_problem(plan, domain):
    if domain == "satellite":
        dict_actions_domain['satellite'] = dict_actions_s_normal
    elif domain == "satellite_types":
        dict_actions_domain['satellite'] = dict_actions_s_invariant
        domain = "satellite"
    init_structures = create_starting_structures(plan, domain)
    init_state = init_structures[0]
    goal_state = init_structures[1]
    actions = init_structures[2]

    start = time.time()

    result_goals = check_goals(init_state, goal_state, domain)
    if result_goals[0] is True:
        return (result_goals[0], result_goals[1], result_goals[2], len(actions))
        #print(result_goals[2])
    else:
        pass
        #print(result_goals[2])

    state = init_state
    j = 0
    for action in actions:
        start_act = time.time()
        result = execute_action(state, action, domain)
        if result[0] is True:
            #print(result[2])
            state = result[1]
            result_goals = check_goals(state, goal_state, domain)
            if result_goals[0] is True:
                #print(result_goals[2])
                j = j + 1
                break
            else:
                pass
                #print(result_goals[2])
        else:
            result_goals = check_goals(state, goal_state, domain)
            return (result[0], result_goals[1], result[2], result[3], result[4], result[5], j)
            #print(result[2])
            #print(result[1])
            break
        j = j + 1
        end_act = time.time()
        #print("Ho impiegato per fare una azione: " + str(end_act-start_act))

    number_missing_actions = len(actions) - j
    end = time.time()
    #print("Ho impiegato " + str(end-start))
    return (result_goals[0], result_goals[1], result_goals[2], number_missing_actions)

def rimuovi_spazi(stringa):
    return re.sub(r'\s+(\d)', r'\1', stringa)


def rimuovi_numeri(stringa):
    return ''.join([i for i in stringa if not i.isdigit()])

############################################################################################################
# REWARD
############################################################################################################
def calculate_reward(plan, 
                    domain , 
                    discounted = False, 
                    discount_factor = 0.99, 
                    use_percentage = True, 
                    no_penalty = False, 
                    traslated_reward = False,
                    use_reward_eos = False,
                    use_penalty_unused_actions = False,
                    reward_type = "standard",):
    if domain == "satellite":
        dict_actions_domain['satellite'] = dict_actions_s_normal
    elif domain == "satellite_types":
        dict_actions_domain['satellite'] = dict_actions_s_invariant
        domain = "satellite"
    # Creo le strutture necessarie
    init_structures = create_starting_structures(plan, domain)
    init_state = init_structures[0]
    goal_state = init_structures[1]
    actions = init_structures[2]
    start = time.time()

    # Calcolo il reward
    
    if discounted is False and reward_type in ["replicated", "standard"]:
        score = calculate_default_reward(init_state, goal_state, actions, domain, use_percentage, no_penalty)
        if traslated_reward is True and no_penalty is False:
            if use_percentage:
                score = (score+1)/2.0
            else:
                score = (score+len(goal_state.keys()))/2.0
        if reward_type == "standard":
            return score
        else:
            # creo un vettore di dimensione uguale al numero di azioni+1 
            # e assegno a ciascuna azione il reward ottenuto
            score = [score for i in range(len(actions)+1)]
            final_score = distribute_reward_to_tokens(actions, score)
            return final_score

    # Discounted rewards richiede di mantenere in memoria una lista di rewards per ora non funziona con replicated.
    if discounted is True and reward_type in ["standard", "distributed", "cumulative"]:
        score = calculate_discounted_reward(init_state, goal_state, actions, domain, use_percentage, no_penalty, discount_factor, reward_type,
                                            reward_eos=use_reward_eos, penalty_unused_actions=use_penalty_unused_actions)
        if traslated_reward is True and no_penalty is False:
            if use_percentage:
                score = (score+1)/2.0
            else:
                score = (score+len(goal_state.keys()))/2.0
        if reward_type == "standard":
            if type(score) == list:
                raise ValueError(f"Standard reward returned as a list: {score}")
            return score
        else:
            # If we have vectorized_rewards but the model doesn't produce an action it is possible that the score vector has a single value.
            if len(score) == 1:
                warnings.warn(f"Score is a single value {score}")
                warnings.warn(f"init_state: {init_state}")
                warnings.warn(f"goal_state: {goal_state}")
                warnings.warn(f"actions: {actions}")
                warnings.warn(f"domain: {domain}")

            return score
    
    # Se non ho scelto un reward type valido
    raise ValueError(f"Invalid configuration: discounted={discounted}, reward={reward_type}")

# Questa funzione calcola il reward tradizionale e ne ritorna il valore. Se si usa replicated verra' poi distribuito, altrimenti no e si ritornera' il valore singolo
def calculate_default_reward(init_state, goal_state, actions, domain, use_percentage, no_penalty):
    result_goals = check_goals(init_state, goal_state, domain)
    if result_goals[0] is True:
        if use_percentage is True:
            return 1
        else:
            return len(result_goals[1].keys())  
    else:
        pass
    state = init_state
    j = 0
    for action in actions:
        start_act = time.time()
        result = execute_action(state, action, domain) # Eseguo l'azione e ne verifico la correttezza
        if result[0] is True: # Se l'azione e' eseguibile tutto ok
            state = result[1]
            result_goals = check_goals(state, goal_state, domain)
            if result_goals[0] is True:
                if use_percentage is True:
                    return 1
                else:
                    return len(result_goals[1].keys())
            else:
                pass # Non ho raggiunto i goals...continuo
        else: # Se l'azione non e' eseguibile -> controllo quanti goals sono e penalizzo
            result_goals = check_goals(state, goal_state, domain)
            goals_satisfied = result_goals[1]
            count = 0
            n_goals = len(goals_satisfied.keys())
            for goal in goals_satisfied.keys():
                if goals_satisfied[goal] is True:
                    count += 1
            if no_penalty is True:
                if use_percentage is True:
                    return (count/n_goals)
                else:
                    return (count)
            else:
                #Occorre penalizzare qui
                if use_percentage is True:
                    return (count/n_goals) -1
                else:
                    return count -(1*n_goals)
        j = j + 1
        end_act = time.time()

    number_missing_actions = len(actions) - j
    end = time.time()
    goals_satisfied = result_goals[1]
    count = 0
    n_goals = len(goals_satisfied.keys())
    for goal in goals_satisfied.keys():
        if goals_satisfied[goal] is True:
            count += 1
    if use_percentage is True:
        return count/n_goals
    else:
        return count

# Questa funzione calcola il reward -> nel caso standard restituisce un singolo valore, nel caso distributed restituisce un vettore di valori dipendentemente dalla tipologia scelta

def calculate_discounted_reward(init_state, 
                                goal_state, 
                                actions, 
                                domain, 
                                use_percentage, 
                                no_penalty, 
                                discount_factor, 
                                reward_type, 
                                reward_eos=False, penalty_unused_actions=False):
    rewards = []
    n_goals = len(goal_state.keys())
    new_goal_satisfied = {}
    for goal in goal_state.keys():
        new_goal_satisfied[goal] = False
        
    vectorized_rewards = ((reward_type == "distributed") or (reward_type == "cumulative"))

    result_goals = check_goals(init_state, goal_state, domain)
    goal_satisfied_count = 0
    for goal in goal_state.keys():
        if result_goals[1][goal] is True and new_goal_satisfied[goal] is True: # se un goal è già soddisfatto
            pass
        elif result_goals[1][goal] is False and new_goal_satisfied[goal] is True: # un goal che era soddisfatto non è più soddisfatto
            pass
        elif result_goals[1][goal] is False and new_goal_satisfied[goal] is False: # il goal non è soddisfatto
            pass
        else: # abbiamo soddisfatto un goal (result_goals[1][goal] is True and new_goal_satisfied[goal] is False)
            goal_satisfied_count += 1
            new_goal_satisfied[goal] = True
    if use_percentage is True:
        rewards.append(goal_satisfied_count/n_goals)
    else:
        rewards.append(goal_satisfied_count)

    if result_goals[0] is True:
        reward_eos = rewards[0] if reward_eos else 0.0
        coeff_penalty_unused_actions = -0.1 if use_percentage is True else -1
        penalty_unused_actions = coeff_penalty_unused_actions if penalty_unused_actions else 0.0
        if vectorized_rewards:
            return distribute_reward_to_tokens(actions, compute_reward(rewards, discount_factor=discount_factor, reward_type = reward_type,), reward_eos=reward_eos, penalty_unused_actions=penalty_unused_actions)
        else:
            return compute_reward(rewards, discount_factor=discount_factor, reward_type = reward_type,)
    else:
        pass

    state = init_state
    j = 0
    for action in actions:
        result = execute_action(state, action, domain)
        if result[0] is True:
            state = result[1]
            result_goals = check_goals(state, goal_state, domain)

            # valuto quanti goal la mia azione ha soddisfatto
            goal_satisfied_count = 0
            for goal in goal_state.keys():
                if result_goals[1][goal] is True and new_goal_satisfied[goal] is True: # se un goal è già soddisfatto
                    pass
                elif result_goals[1][goal] is False and new_goal_satisfied[goal] is True: # un goal che era soddisfatto non è più soddisfatto
                    pass
                elif result_goals[1][goal] is False and new_goal_satisfied[goal] is False: # il goal non è soddisfatto
                    pass
                else: # abbiamo soddisfatto un goal (result_goals[1][goal] is True and new_goal_satisfied[goal] is False)
                    goal_satisfied_count += 1
                    new_goal_satisfied[goal] = True
            if use_percentage is True:
                rewards.append(goal_satisfied_count/n_goals)
            else:
                rewards.append(goal_satisfied_count)

            if result_goals[0] is True:
                coeff_percentage_eos = 1 if use_percentage else n_goals
                reward_eos = coeff_percentage_eos if reward_eos else 0.0
                coeff_penalty_unused_actions = -0.1 if use_percentage else -1
                penalty_unused_actions = coeff_penalty_unused_actions if penalty_unused_actions else 0.0
                if vectorized_rewards:
                    return distribute_reward_to_tokens(actions, compute_reward(rewards, discount_factor=discount_factor, reward_type = reward_type,), reward_eos=reward_eos, penalty_unused_actions=penalty_unused_actions)
                else:
                    return compute_reward(rewards, discount_factor=discount_factor, reward_type = reward_type,)
        
        else: # Qui succede quando un azione ROMPE le precondizioni
            if no_penalty is False: # se voglio penalizzare...
                if use_percentage is True:
                    rewards.append(-1.0)
                else:
                    rewards.append(-1*n_goals)
            
            if vectorized_rewards:
                reward_eos = 0.0
                penalty_unused_actions = 0.0
                return distribute_reward_to_tokens(actions, compute_reward(rewards, discount_factor=discount_factor, reward_type = reward_type,), reward_eos=reward_eos, penalty_unused_actions=penalty_unused_actions)
            else:
                return compute_reward(rewards, discount_factor=discount_factor, reward_type = reward_type,)  

    if vectorized_rewards:
        reward_eos = 0.0
        coeff_penalty_unused_actions = 0.0
        return distribute_reward_to_tokens(actions, compute_reward(rewards, discount_factor=discount_factor, reward_type = reward_type,), reward_eos=reward_eos, penalty_unused_actions=penalty_unused_actions)
    else:
        return compute_reward(rewards, discount_factor=discount_factor, reward_type = reward_type,)  

# Questa funzione calcola il reward -> nel caso standard restituisce un singolo valore, nel caso distributed restituisce un vettore di valori dipendentemente dalla tipologia scelta
def compute_reward(rewards, discount_factor = 0.99, reward_type = "standard"):
    if reward_type == "standard":
        rewards.reverse()
        reward_sum = 0
        for reward in rewards:
            reward_sum = reward_sum*discount_factor + reward
        return reward_sum

    elif reward_type == "cumulative":
        reward_sum = 0
        reward_list = []
        exp_count = 0
        for reward in rewards:
            reward_sum = reward_sum + (discount_factor**exp_count)*reward
            reward_list.append(reward_sum)
            exp_count += 1
        return reward_list

    elif reward_type == "distributed":
        reward_list = []
        exp_count = 0
        for reward in rewards:
            current = (discount_factor**exp_count)*reward
            reward_list.append(current)
            exp_count += 1
        return reward_list
    else:
        raise ValueError(f"Invalid reward type {reward_type}")

def distribute_reward_to_tokens(actions, rewards, reward_eos=0.0, penalty_unused_actions=0.0):
    if len(actions) == 0:
        return [rewards[0]]
    token_reward_list = [] # Skippo il primo reward perchè è il reward per lo stato iniziale

    if len(actions) == (len(rewards)-1):
        #print("Ok")
        pass
    else:
        #print("The plan reaches the goals and generates more actions")
        for i in range(len(actions)-len(rewards)+1):
            rewards.append(penalty_unused_actions)
            reward_eos = 0.0 # ha generato azioni in più in cui non si ha una verifica delle precondizioni, quindi EOS non è detto sia corretto 

    for index in range(0,len(actions)):
        action = actions[index]
        reward = rewards[index+1]
        # TODO qui potrei passare il tokenizer.
        token_action_len = len(action.strip().split("_"))
        for i in range(0,token_action_len):
            token_reward_list.append(reward)
    token_reward_list.append(reward_eos)
    return token_reward_list
