
def parse_problem(initial_state, goal_state, actions, domain):
    if domain == "blocksworld":
        return parse_problem_blocksworld(initial_state, goal_state, actions)
    elif domain == "childsnack":
        return parse_problem_childsnack(initial_state, goal_state, actions)
    elif domain == "depots":
        return parse_problem_depots(initial_state, goal_state, actions)
    elif domain == "driverlog":
        return parse_problem_driverlog(initial_state, goal_state, actions)
    elif domain == "floortile":
        return parse_problem_floortile(initial_state, goal_state, actions)
    elif domain == "logistics":
        return parse_problem_logistics(initial_state, goal_state, actions)
    elif domain == "sokoban":
        return parse_problem_sokoban(initial_state, goal_state, actions)
    elif domain == "zenotravel":
        return parse_problem_zenotravel(initial_state, goal_state, actions)
    elif domain == "satellite":
        return parse_problem_satellite(initial_state, goal_state, actions)
    elif domain == "floortile":
        return parse_problem_floortile(initial_state, goal_state, actions)
    print("Dominio non trovato !!")
    return (initial_state, goal_state, actions)

def parse_problem_satellite(initial_state, goal_state, actions):
    changing_list = {
        "power_avail": "power-avail",
        "calibration_target": "calibration-target",
        "on_board": "on-board",
        "have_image": "have-image",
    }
    import re
    for i,init_state in enumerate(initial_state):
       for key, value in changing_list.items():
            initial_state[i] = initial_state[i].replace(key, value)
    for i, goal in enumerate(goal_state):
        for key, value in changing_list.items():
            goal_state[i] = goal_state[i].replace(key, value)
    return (initial_state, goal_state, actions)
def parse_problem_blocksworld(initial_state, goal_state, actions):
    for i, _ in enumerate(initial_state):
        initial_state[i] = initial_state[i].replace("handempty", "arm-empty")
        initial_state[i] = initial_state[i].replace("ontable", "on-table")
    return (initial_state, goal_state, actions)

def parse_problem_childsnack(initial_state, goal_state, actions):
    return (initial_state, goal_state, actions)

def parse_problem_depots(initial_state, goal_state, actions):
    return (initial_state, goal_state, actions)

def parse_problem_driverlog(initial_state, goal_state, actions):
    return (initial_state, goal_state, actions)

def parse_problem_floortile(initial_state, goal_state, actions):
    for i,action in enumerate(actions):
        if "up" in actions[i] and "paint-up" not in actions[i]:
            actions[i] = actions[i].replace("up", "move-up")
        if "down" in actions[i] and "paint-down" not in actions[i]:
            actions[i] = actions[i].replace("down", "move-down")
        if "left" in actions[i] and "paint-left" not in actions[i]:
            actions[i] = actions[i].replace("left", "move-left")
        if "right" in actions[i] and "paint-right" not in actions[i]:
            actions[i] = actions[i].replace("right", "move-right")
        actions[i] = actions[i].replace("_", "-")
    for i,init_state in enumerate(initial_state):
        initial_state[i] = initial_state[i].replace("_", "-")
    for i,goal in enumerate(goal_state):
        goal_state[i] = goal_state[i].replace("_", "-") 
    return (initial_state, goal_state, actions)

def parse_problem_logistics(initial_state, goal_state, actions):
    for i,init_state in enumerate(initial_state):
        if init_state.split("_")[0] == "obj":
            objects_string = '_'.join(init_state.split("_")[1:])
            predicate_string = "package" + "_" + objects_string
            initial_state[i] = predicate_string
    return (initial_state, goal_state, actions)

def parse_problem_sokoban(initial_state, goal_state, actions):
    return (initial_state, goal_state, actions)

def parse_problem_zenotravel(initial_state, goal_state, actions):
    return (initial_state, goal_state, actions)