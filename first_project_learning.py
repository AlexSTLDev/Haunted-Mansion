import random
import sys
import time
import msvcrt  # For skipping text scroll (Windows only)

# === Password Protection ===
valid_names = ["alex", "skye", "beth"]
max_attempts = 3
attempts = 0

while attempts < max_attempts:
    entered_name = input("Enter your name to unlock the program: ")
    if entered_name.lower() in [name.lower() for name in valid_names]:
        print("Access granted!")
        break
    else:
        attempts += 1
        print(f"Access denied. Attempts left: {max_attempts - attempts}")

if attempts == max_attempts:
    print("Too many failed attempts. Exiting program.")
    exit()

# === Global Game State ===
current_room = "foyer"
inventory = []
visited_rooms = set()
rooms_unlocked = {"basement": False, "stairs": False}
candelabra_acquired = False
candle_revealed = False
candle_tilted = False
puzzle_completed = False
stairwell_searched = False
note_read_in_study = False
shield_moved = False
rusty_key_acquired = False

def type_text(text, delay=0.03):
    for i, char in enumerate(text):
        if msvcrt.kbhit() and msvcrt.getch() == b'\r':  # Enter key to skip
            sys.stdout.write(text[i:])
            sys.stdout.flush()
            break
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def show_inventory():
    print("\nInventory:", ", ".join(inventory) if inventory else "Empty")

def show_map():
    print("\nExplored Map:")
    for room in visited_rooms:
        print("-", room.replace("_", " ").title())

def final_puzzle():
    global puzzle_completed
    target_word = "mad scientist"
    guessed = set()
    attempts_left = 8

    type_text("\nA voice echoes: 'Heh heh heh... solve my final riddle and earn your freedom!'")
    type_text("You notice glowing letters forming a puzzle on the wall...")

    while attempts_left > 0:
        display = " ".join([letter if letter in guessed or letter == " " else "_" for letter in target_word])
        type_text(f"\nPuzzle: {display}")
        type_text(f"Attempts remaining: {attempts_left}")
        guess = input("Guess a letter: ").strip().lower()

        if not guess or len(guess) != 1 or not guess.isalpha():
            print("Please guess a single letter.")
            continue

        if guess in guessed:
            print("You've already guessed that letter.")
            continue

        guessed.add(guess)

        if guess in target_word:
            type_text("Correct!")
        else:
            attempts_left -= 1
            type_text("Wrong...")

        if all(c in guessed or c == " " for c in target_word):
            puzzle_completed = True
            type_text("\nThe word glows brightly: 'MAD SCIENTIST'")
            type_text("A hidden door creaks open behind a bookcase, revealing daylight...")
            type_text("You've escaped the haunted mansion! Thanks for playing!")
            sys.exit()

    type_text("\nThe letters burn away. The mad scientist appears, laughing maniacally...")
    type_text("You are trapped forever in his twisted experiment. Game over.")
    sys.exit()

def move_to_room(room_name):
    global current_room, stairwell_searched

    # Slip hazard if not searched stairwell
    if current_room == "stairwell" and room_name == "stairs" and not stairwell_searched:
        type_text("\nAs you step forward, your foot slips on something!")
        type_text("You tumble painfully down the stairs and barely manage to get up.")
        # Optionally, you could add health or a penalty here
        stairwell_searched = True  # After slipping, we say they've been warned

    # Locked stairwell requiring rusty key
    if current_room == "stairs" and room_name == "upstairs" and "rusty key" not in inventory:
        type_text("\nThe door to the upstairs is locked tight. You need a key.")
        return

    # Basement is dark if no candelabra
    if room_name == "basement" and "candelabra" not in inventory:
        type_text("\nIt's pitch black down there. You can't see a thing without a light source.")
        return

    current_room = room_name
    visited_rooms.add(room_name)
    describe_room(room_name)

def describe_room(room_name):
    room = rooms[room_name]

    # Dark room check
    if room["dark"]:
        if "candelabra" in inventory or candle_tilted:
            # With light
            type_text("\n" + room["description"])
        else:
            type_text("\nIt is too dark to see anything in here.")
            return
    else:
        type_text("\n" + room["description"])

    # Special dynamic elements
    if room_name == "study" and not note_read_in_study:
        type_text("There is a note here that might be useful. Maybe you should read it.")

    if room_name == "dining":
        if note_read_in_study and not shield_moved:
            type_text("You see a large shield on the wall. Maybe it can be moved.")
        elif shield_moved and not rusty_key_acquired:
            type_text("Behind the moved shield, something glints faintly.")

def search_room():
    global note_read_in_study, shield_moved, rusty_key_acquired, stairwell_searched, candelabra_acquired, candle_tilted

    room = rooms[current_room]

    # Searching stairwell reveals the slip hazard paper
    if current_room == "stairwell" and not stairwell_searched:
        stairwell_searched = True
        type_text("\nYou find a crumpled piece of paper tucked in a gap in the wall.")
        type_text("It reads: 'Sometimes, tilting what gives light can reveal what hides in the dark.'")
        return

    # Searching study reveals note
    if current_room == "study" and not note_read_in_study:
        note_read_in_study = True
        type_text("\nYou pick up the note: 'The key to escape is hidden where pens once scratched secrets...'")
        return

    # Searching desk shows note that hints about shield
    if current_room == "desk" and "rusty key" not in inventory:
        type_text("\nIn the desk drawer, you find a faded note: 'Check behind the shield in the dining room.'")
        return

    # Searching dining allows moving the shield only if note read
    if current_room == "dining" and note_read_in_study and not shield_moved:
        shield_moved = True
        rusty_key_acquired = True
        inventory.append("rusty key")
        type_text("\nYou move the shield aside and find a rusty key hidden behind it!")
        return

    # Searching servants room to get candelabra
    if current_room == "servants" and "candelabra" not in inventory:
        candelabra_acquired = True
        inventory.append("candelabra")
        type_text("\nYou pick up the dusty candelabra from the crate.")
        return

    # Searching master bedroom for beaker clue
    if current_room == "master":
        type_text("\nYou notice a broken beaker shattered on the floor, remnants of some strange chemical.")
        return

    # Searching bathroom for mirror clue
    if current_room == "bathroom":
        type_text("\nThe cracked bathroom mirror has backward letters etched faintly:")
        type_text("'t__ts_i_nc__ a_' (Could it be a clue?)")
        return

    # Searching any other room
    if not room["items"]:
        type_text("\nYou search around but find nothing of interest.")

def use_item(item_name):
    global candle_tilted

    if item_name not in inventory:
        type_text(f"\nYou don't have {item_name} in your inventory.")
        return

    if current_room == "stairwell" and item_name == "candelabra" and not candle_tilted:
        candle_tilted = True
        type_text("\nYou carefully tilt the candelabra as the note suggested.")
        type_text("A hidden light flickers on, revealing a safe path down the basement stairs!")
        return

    type_text(f"\nUsing {item_name} here doesn't seem to do anything.")

def check_win_condition():
    if current_room == "the light":
        final_puzzle()

def help_menu():
    print("""
Commands:
  move [room]      - Move to a connected room.
  search           - Search the current room for items or clues.
  use [item]       - Use an item from your inventory.
  inventory        - Show your inventory.
  map              - Show explored rooms.
  help             - Show this help menu.
  quit             - Exit the game.
""")

# Rooms dictionary with descriptions, connections, etc.
rooms = {
    "foyer": {
        "description": (
            "You step into the mansion's foreboding foyer. Time has ravaged the once-grand space. "
            "The walls wear peeling, tattered wallpaper that reveals cracked, stained plaster beneath. "
            "Faded portraits hang crookedly, their faces marred by deep scratches, as if someone tried "
            "to erase their memory. A weak candle sputters dimly on a rusted sconce, casting "
            "twisted, flickering shadows that dance ominously across the floor.\n"
            "Around you, three distinct pathways beckon: to the left, a dark doorway leads to a shadowy stairwell. "
            "Ahead, the heavy door to the study waits, its wood dark and weathered. To your right, the dining room stands frozen, "
            "its air thick with an unsettling silence."
        ),
        "connections": ["study", "stairwell", "dining room"],
        "items": [],
        "dark": False
    },
    "study": {
        "description": (
            "Dust chokes the air in this forgotten library. Books lie scattered and broken, "
            "their pages yellowed and torn. The scent of mildew and rot clings to the shelves. "
            "A damp note, stained with dark smudges, rests on the floor.\n"
            "The study connects to the foyer, and further ahead, you can spot a desk."
        ),
        "connections": ["foyer", "desk"],
        "items": [],
        "dark": False
    },
    "desk": {
        "description": (
            "A massive oak desk dominates the room, scarred by deep gouges and water rings. "
            "Several drawers hang open, revealing brittle papers and rusty nails. "
            "The air smells faintly of decayed ink.\n"
            "You can see a way back to the study."
        ),
        "connections": ["study"],
        "items": ["rusty key"],
        "dark": False
    },
    "stairwell": {
        "description": (
            "The narrow hallway's wooden floorboards creak with every step. "
            "Cobwebs stretch thick across the ceiling. The wallpaper here is stained with dark streaks, "
            "as if something has oozed down the walls. An odd glint catches your eye on the wall.\n"
            "The stairwell leads to the foyer below, or you can continue upward to the stairs."
        ),
        "connections": ["foyer", "stairs"],
        "items": [],
        "dark": False
    },
    "dining room": {
        "description": (
            "The dining room is frozen in time. A rotted feast sits atop a dust-covered table, "
            "its foul scent hanging heavy. A massive, tarnished shield hangs crooked on the wall, "
            "its edges chipped and scratched, as if from countless forgotten battles.\n"
            "You can return to the foyer."
        ),
        "connections": ["foyer"],
        "items": ["dagger"],
        "dark": False
    },
    "stairs": {
        "description": (
            "The staircase groans beneath your weight. Faded bloodstains mar the worn steps. "
            "An ancient door at the top remains locked, its iron handle rusted shut. "
            "The air grows colder as you look upwards.\n"
            "The stairs lead to the servants' quarters, the kids' room, or the master bedroom above."
        ),
        "connections": ["stairwell", "master", "servants", "kids_room"],
        "items": [],
        "dark": False
    },
    "master": {
        "description": (
            "The master bedroom is thick with dust and decay. Peeling wallpaper curls away from moldy plaster. "
            "Shattered glass from a broken beaker lies scattered across the warped floorboards, "
            "emitting a faint chemical odor.\n"
            "The master bedroom connects to the bathroom."
        ),
        "connections": ["stairs", "bathroom"],
        "items": [],
        "dark": True
    },
    "bathroom": {
        "description": (
            "The cracked bathroom mirror hangs askew, stained with grime and spiderwebs. "
            "Faint backward letters have been etched into the foggy glass, barely visible. "
            "The sink drips a slow, rhythmic plop, echoing in the silence.\n"
            "You can return to the master bedroom."
        ),
        "connections": ["master"],
        "items": [],
        "dark": True
    },
    "servants": {
        "description": (
            "A cramped servants' room cluttered with broken crates and dusty rags. "
            "The air tastes stale, heavy with forgotten labor. A dusty candelabra rests forgotten on an overturned crate.\n"
            "The servants' quarters connect to the stairs."
        ),
        "connections": ["stairs"],
        "items": ["candelabra"],
        "dark": False
    },
    "kids_room": {
        "description": (
            "This child's room is frozen in eerie silence. Broken toys lie half-buried in dust, "
            "and the wallpaper is torn, revealing dark stains beneath. The room smells faintly of something sour.\n"
            "You can return to the stairs."
        ),
        "connections": ["stairs"],
        "items": [],
        "dark": False
    },
    "basement": {
        "description": (
            "You step into the basement, a cavern of shadows and damp stone. The air is thick with mold and the faint metallic scent of rusted tools. "
            "Chains hang from the ceiling, clinking softly despite the stillness.\n"
            "The basement connects to the foyer, and there's a hidden passage leading deeper into the house."
        ),
        "connections": ["foyer", "hidden_passage"],
        "items": [],
        "dark": True
    },
    "hidden_passage": {
        "description": (
            "A narrow, dust-choked passage stretches ahead, walls slick with moisture. "
            "The faint light at its end flickers, casting long, distorted shapes.\n"
            "The hidden passage connects to the basement and leads to a strange, eerie light."
        ),
        "connections": ["basement", "the light"],
        "items": [],
        "dark": True
    },
    "the light": {
        "description": (
            "You enter a grotesque laboratory, jars filled with cloudy formaldehyde preserve severed limbs and twisted creatures. "
            "The sickly green light hums overhead, illuminating horrors best left unseen.\n"
            "The laboratory connects to the hidden passage."
        ),
        "connections": ["hidden_passage"],
        "items": [],
        "dark": True
    },
    "upstairs": {
        "description": (
            "Upstairs, the corridor stretches endlessly, wallpaper peeling like dead skin, "
            "and the floorboards creak as if whispering secrets. Locked doors line the walls, each hiding forgotten terrors.\n"
            "The upstairs corridor connects to the stairs below."
        ),
        "connections": ["stairs"],
        "items": [],
        "dark": False
    }
}




def main():
    print("""
Commands:
  move [room]      - Move to a connected room.
  search           - Search the current room for items or clues.
  use [item]       - Use an item from your inventory.
  inventory        - Show your inventory.
  map              - Show explored rooms.
  help             - Show this help menu.
  quit             - Exit the game.
""")
    type_text("Welcome to the Haunted Mansion!")
    type_text("Type 'help' for a list of commands.\n")
    visited_rooms.add(current_room)
    describe_room(current_room)

    while True:
        check_win_condition()
        cmd = input("\n> ").strip().lower()
        if not cmd:
            continue

        parts = cmd.split()
        command = parts[0]

        if command == "help":
            help_menu()

        elif command == "quit":
            print("Thanks for playing!")
            break

        elif command == "inventory":
            show_inventory()

        elif command == "map":
            show_map()

        elif command == "move":
            if len(parts) < 2:
                print("Move where?")
                continue
            dest = " ".join(parts[1:]).replace(" ", "_")
            dest = dest.lower()

            # Handle special locked stairwell upstairs access
            if dest == "upstairs":
                if current_room != "stairs":
                    print("You need to be at the stairs to go upstairs.")
                    continue
                if "rusty key" not in inventory:
                    print("The upstairs door is locked. You need a rusty key.")
                    continue
                # Allow going upstairs
                move_to_room("upstairs")
                continue

            if dest in rooms[current_room]["connections"]:
                move_to_room(dest)
            else:
                print(f"You can't go to {dest.replace('_',' ')} from here.")

        elif command == "search":
            search_room()

        elif command == "use":
            if len(parts) < 2:
                print("Use what?")
                continue
            item = " ".join(parts[1:])
            use_item(item)

        else:
            print("Unknown command. Type 'help' for assistance.")

if __name__ == "__main__":
    main()