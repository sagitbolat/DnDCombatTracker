import curses
import igraph as ig

character_names={}


class Action:
    def __init__(self, round, origin, target, hit, damage, notes):
        self.round = round #which round this action took place. 1 round includes every creature's turn.
        self.origin=origin #name of the person performng action
        self.target=target #who the action targets
        self.hit = hit #true = attack or spell succeeds, false = attack or spell fails
        self.damage = damage
        self.notes = notes

    def to_string(self):
        if self.hit:
            return f"Round {self.round}: {self.origin} hits {self.target} for {self.damage} damage. NOTES: {self.notes}"
        else:
            return f"Round {self.round}: {self.origin} misses {self.target}. NOTES: {self.notes}"


def main(stdscr):
    actions = []
    # Clear screen
    stdscr.clear()
    curses.nocbreak() 
    curses.start_color()
    
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    stdscr.addstr(0, 0, "Enter character names and initiative. Once you are done, enter 'END' as the name.", curses.color_pair(1))
    stdscr.addstr(2,0, "=====================================")

    curses.echo()
    entering_names = True
    current_row = 3
    while(entering_names):
        stdscr.move(1, 0)  # Move the cursor to the beginning of the second line
        stdscr.clrtoeol()
        stdscr.addstr(1, 0, "Name: ")
        name = stdscr.getstr().decode()
        stdscr.refresh()

        if name == "END":
            break
            entering_names = False
        
        stdscr.move(1, 0)  # Move the cursor to the beginning of the second line
        stdscr.clrtoeol()
        stdscr.addstr(1, 0, "Initiative: ")
        initiative = stdscr.getstr().decode()
        
        if initiative == "END":
            break
            entering_names = False
         
        stdscr.refresh()
        character_names[float(initiative)] = name
        stdscr.addstr(current_row, 0, name + "|" + initiative)
        current_row += 1

    # Refresh the screen to show the changes
    stdscr.refresh()

    curses.noecho()
    sorted_characters = {k: character_names[k] for k in sorted(character_names, reverse=True)}


    def single_seletion(list_of_seletions, selected_index, print_offset=0):

        for i, selection in enumerate(list_of_seletions):
            if i == selected_index:
                stdscr.addstr(i + 1+print_offset, 0, f"> {selection}", curses.A_REVERSE)
            else:
                stdscr.addstr(i + 1+print_offset, 0, f"  {selection}")

        stdscr.refresh()  # Refresh the screen to update the UI

        stdscr.nodelay(True)
        key = stdscr.getch()
        stdscr.nodelay(False)
        if key in [curses.KEY_UP, ord('w'), ord('W')]:
            return (selected_index - 1) % len(list_of_seletions)
        elif key in [curses.KEY_DOWN, ord('s'), ord('S')]:
            return (selected_index + 1) % len(list_of_seletions)
        elif key in [curses.KEY_ENTER, ord('\n'), ord('\r')]:
            return -1
        else: return selected_index


    num_turns = 0
    combat_ongoing = True
    while combat_ongoing:
        num_turns += 1
        for initiative in sorted_characters:
            curr_turn = True
            while curr_turn:
                name = sorted_characters[initiative]

                # Display and select target
                target_names = list(character_names.values())
                selected_index = 0

                target_names.append("END TURN")
                target_names.append("END COMBAT")


                #target selection
                while True:
                    stdscr.clear()  # Clear the screen at the start of each iteration

                    stdscr.addstr(0, 0, f"Turn {num_turns}. ")
                    stdscr.addstr(f"{name}'s", curses.color_pair(1))
                    stdscr.addstr(f" turn.")
                    stdscr.addstr(1, 0, f"Select Target:")

                    sel = single_seletion(target_names, selected_index, 1)
                    if (sel == -1):
                        break
                    selected_index = sel
                    

                target_name = target_names[selected_index] #NOTE: Record
                if (target_name == "END COMBAT"):
                    combat_ongoing = False
                    break
                if (target_name == "END TURN"):
                    curr_turn = False
                    break 
                stdscr.addstr(len(target_names) + 2, 0, f"Selected target: {target_name}")

                #hit prompt
                hit = ["Yes", "No"]
                selected_index=0
                while True:
                    stdscr.clear()  # Clear the screen at the start of each iteration

                    stdscr.addstr(0, 0, f"{name}", curses.color_pair(1))
                    stdscr.addstr(" targets ")
                    stdscr.addstr(f"{target_name}", curses.color_pair(1))
                    stdscr.addstr(1, 0, f"Does it hit/affect target?")
                    sel = single_seletion(hit, selected_index, 1)
                    if (sel == -1):
                        break
                    selected_index = sel
                    

                hit_or_not = hit[selected_index] #NOTE: record
                if (hit_or_not == "Yes"):
                    stdscr.addstr(4, 0, f"Enter Damage or effect: ")
                    curses.echo()
                    effect = stdscr.getstr().decode() #NOTE: Record
                    curses.noecho()
                else:
                    effect = "Miss"

                # additional Notes:
                stdscr.addstr(5, 0, "Additional Notes: ")
                curses.echo()
                notes = stdscr.getstr().decode() #NOTE: Record
                curses.noecho()

                if (notes != "IGNORE"):
                    action = Action(num_turns, name, target_name, hit_or_not, effect, notes)
                    actions.append(action)
                stdscr.refresh()

    curses.endwin()


    file_name = input("Save file name: ")
    with open(f"{file_name}.txt", 'w') as file:
        for action in actions:
            file.write(action.to_string()+'\n')

    actions_by_round = {}
    for action in actions:
        if action.round not in actions_by_round:
            actions_by_round[action.round] = []
        actions_by_round[action.round].append(action)

    # Create a flowchart for each round
    for round, actions in actions_by_round.items():
        g = ig.Graph(directed=True)
        vertices = set()
        for action in actions:
            vertices.add(action.origin)
            vertices.add(action.target)
        g.add_vertices(sorted(list(vertices)))
        
        for action in actions:
            g.add_edge(action.origin, action.target)
            edge_id = g.get_eid(action.origin, action.target)
            g.es[edge_id]['label'] = f'{action.notes} ({action.damage})'
            g.es[edge_id]['color'] = 'green' if action.hit else 'red'
        
        layout = g.layout('kk')  # Kamada-Kawai layout
        ig.plot(g, f'round_{round}.png', layout=layout, bbox=(600, 600), margin=50, vertex_label=g.vs['name'], edge_label=g.es['label'], edge_color=g.es['color'], vertex_size=75) 
 


# Initialize curses and call the main function
curses.wrapper(main)
