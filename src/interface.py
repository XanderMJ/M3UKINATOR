from simple_term_menu import TerminalMenu

class CLI:

    def __init__(self):
        self.exit = False

    def create_menu(self, title, entries, args=False, add_return=True, return_label="<< Return"):
        if add_return:
            entries[return_label] = None

        items, func = zip(*entries.items())
        menu = TerminalMenu(
            menu_entries=items,
            title=title,
            cycle_cursor=True,
            clear_screen=True
        )
        exit = False
        while not exit:
            selection = menu.show() #returns an int of the item selected
            if not selection == len(items)-1:
                if args==False:
                    func[selection]()
                elif args==True:
                    return selection
                else:
                    print("Invalid args")
            else:
                exit=True




    
