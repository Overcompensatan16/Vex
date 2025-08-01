RULES = [
    {
        "name": "detect_danger_wolf",
        "priority": 1,
        "tags": ["trump:TheWorld:1", "suit:Hazard", "mode:verbose"],
        "conditions": ["danger=wolf"],
        "conclusion": "ALERT: Wolf threat detected!"
    },
    {
        "name": "detect_danger_general",
        "priority": 2,
        "tags": ["trump:TheWorld:1", "suit:Hazard", "mode:generalized"],
        "conditions": ["danger"],
        "conclusion": "ALERT: Danger detected!"
    },
    {
        "name": "detect_fire_campfire",
        "priority": 1,
        "tags": ["trump:TheWorld:3", "suit:Hazard", "mode:verbose"],
        "conditions": ["fire=campfire"],
        "conclusion": "ALERT: Campfire detected!"
    },
    {
        "name": "detect_fire_general",
        "priority": 2,
        "tags": ["trump:TheWorld:3", "suit:Hazard", "mode:generalized"],
        "conditions": ["fire"],
        "conclusion": "ALERT: Fire detected!"
    },
    {
        "name": "evacuate_forest",
        "priority": 3,
        "tags": ["trump:TheWorld:2", "suit:Environment", "mode:generalized"],
        "conditions": ["location=forest", "ALERT: Danger detected!"],
        "conclusion": "ACTION: Evacuate forest immediately!"
    }
]

def get_hazard_rules():
    return RULES