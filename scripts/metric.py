
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
    ["aircraft"],
    ["flevel"]
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

dict_actions_domain['visitall'] = dict_actions_v
dict_predicates_domain['visitall'] = dict_predicates_v
dict_objects_domain['visitall'] = dict_objects_v
convert_action_domain['visitall'] = {}


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

# To create a VALIDATOR in python i need some methods that do the following:
    # starting from my initial state
    # categorize my objects
    # loop through my state
    # take my first action
    # check if it satisfies my preconditions
    #   if it doesn't satisfy, ERROR
    # apply positive effects
    # apply negative effects (finished updating my state)
    # check if I have satisfied the goals
    # repeat until goals are satisfied, no more actions, or violated action
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
# Methods that check if the action is executable and execute it 
def execute_action(states, action, domain):
    # Return a Tuple
    # in the first position the result True, False
    # in the second position the next state if result is True or the current state if it is False
    # in the third position the motivation of the wrong execution
    # split my action, on position 0 the action, then the objects
    #print(action)
    # First i need to verify if the name of the action is correct, then the number of objects and their names 
    splitted_action = action.split("_")[0] # I get the name of the action
    try:
        action_parameter = dict_actions_domain[domain][splitted_action] # verify that the action_name is valid
    except:
        action_parameter = None
    if action_parameter is None:
        return (False, states,"action_name_wrong", splitted_action, action, "")
    splitted_objects = action.split("_")[1:] # I get the objects
    action_objects = action_parameter[0] # I get the objects used by the action
    if len(action_objects) == len(splitted_objects): # I check if the number of objects is correct
        for i in range(0, len(action_objects)): # I loop through the objects
            obj_nonumber = ''.join([j for j in splitted_objects[i] if not j.isdigit()]) # I remove the numbers from the object
            if obj_nonumber not in dict_objects_domain[domain][action_objects[i]]: # I check if the object is valid
                return (False, states, "object_name_wrong", splitted_action, obj_nonumber, splitted_objects[i])
    else:
        return (False, states, "object_number_wrong", splitted_action, len(action_objects), len(splitted_objects))
    # Now i can verify if the action is executable (the preconditions are satisfied)
    action_prec = action_parameter[1] # I get the not grounded preconditions
    violed_precondtion = False
    violed_preconditions_list = []
    violed_preconditions_list_nonumber = []
    for prec in action_prec: # I loop through the preconditions
        prec_list = prec.split(" ")
        prec_parametrized = "" + prec_list[0] # I get the predicate
        for obj in prec_list[1:]: # I iterate through the objects
            prec_parametrized = prec_parametrized + "_" + splitted_objects[int(obj)] # I replace the object with the one in the action
        if prec_parametrized not in states.keys(): # I check if the predicate is in the states
            violed_precondtion = True
            violed_preconditions_list.append(prec_parametrized)
            violed_preconditions_list_nonumber.append(remove_numbers(prec_parametrized))
        elif states[prec_parametrized] is False: # I check if the predicate is false -> i can't execute the action
            violed_precondtion = True
            violed_preconditions_list.append(prec_parametrized)
            violed_preconditions_list_nonumber.append(remove_numbers(prec_parametrized))
        else:
            pass
    if violed_precondtion is True:
        return (False, states, "violed_preconditions", violed_preconditions_list_nonumber, violed_preconditions_list, splitted_action) 
        
    # I execute the action (negative effects)
    action_neg = action_parameter[3] # I get the negative effects
    for neg in action_neg: #  i loop through the negative effects
        neg_list = neg.split(" ") 
        neg_parametrized = "" + neg_list[0] # I get the predicate
        for obj in neg_list[1:]: # I iterate through the objects
            neg_parametrized = neg_parametrized + "_" + splitted_objects[int(obj)] # I replace the object with the one in the action
        states[neg_parametrized] = False # I change the value in my states
    
    # I execute the action (positive effects)
    action_plus = action_parameter[2] # I get the positive effects
    for plus in action_plus: # I loop through the positive effects
        plus_list = plus.split(" ")
        plus_parametrized = "" + plus_list[0] # I get the predicate
        for obj in plus_list[1:]: # I iterate through the objects
            plus_parametrized = plus_parametrized + "_" + splitted_objects[int(obj)] # I replace the object with the one in the action
        states[plus_parametrized] = True # I change the value in my states
    
    return (True, states, "action_succesfull")

# Method that checks if the goals are satisfied
def check_goals(states, goal_states, domain):
    all_goals_satisfied = True
    goals_unsatisfied_list = []
    goals_unsatisfied_list_nonumber = []
    for goal in goal_states.keys():
        if goal not in states.keys():
            goal_states[goal] = False
            all_goals_satisfied = False
            goals_unsatisfied_list.append(goal)
            goals_unsatisfied_list_nonumber.append(remove_numbers(goal))
        elif states[goal] is False:
            goal_states[goal] = False
            all_goals_satisfied = False
            goals_unsatisfied_list.append(goal)
            goals_unsatisfied_list_nonumber.append(remove_numbers(goal))
        else:
            goal_states[goal] = True
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
    else:
        pass

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
                j = j + 1
                break
            else:
                pass
        else:
            result_goals = check_goals(state, goal_state, domain)
            return (result[0], result_goals[1], result[2], result[3], result[4], result[5], j)
            break
        j = j + 1
        end_act = time.time()

    number_missing_actions = len(actions) - j
    end = time.time()
    return (result_goals[0], result_goals[1], result_goals[2], number_missing_actions)

def remove_blanks(stringa):
    return re.sub(r'\s+(\d)', r'\1', stringa)


def remove_numbers(stringa):
    return ''.join([i for i in stringa if not i.isdigit()])