from textual.app import App
from textual.widget import Widget
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, Input, DataTable
from textual.containers import Container, Horizontal, Vertical, VerticalScroll

import json, pickle, os
from pprint import pprint

def nexter(item, items):
    l = len(items)
    i = items.index(item)
    if i + 1 == l:
        return items[0]
    else:
        return items[i + 1]

iymn = ['items','yes', 'maybe', 'no']

if os.path.isfile('current.json'):
    with open('current.json', 'r', encoding='utf-8') as jf:
        DATA = json.load(jf)
elif os.path.isfile('list'):        
    with open('list', 'r', encoding='utf-8') as listfile:
        DATA = {}
        DATA['items'] = listfile.read().split('\n')
        DATA['yes']=[]
        DATA['no']=[]
        DATA['maybe']=[]
        DATA['listname'] = input('What are this a list of?\n')

class Search(ModalScreen[str]):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self):
        yield Input(placeholder = "search string", id="search_string")
    
    def on_input_submitted(self, event):
        self.query_one(Input).value = ''
        self.dismiss(event.value)
        
class nymApp(App):
    BINDINGS = [
        Binding('y', 'yes', 'mark yes'),
        Binding('x', 'no', 'mark no'),
        Binding('m', 'maybe', 'mark maybe'),
        Binding('s', 'switch_table', 'switch tables'),
        Binding('r', 'reset', 'reset'),
        Binding('n', 'next', 'next', show=False),
        Binding('j', 'next', 'next', show=False),        
        Binding('p', 'previous', 'previous', show=False),
        Binding('k', 'previous', 'previous', show=False),
        Binding('/', 'search', 'search list'),
        Binding('f', 'search_reset', 'finish search'),
        ]
    CSS_PATH = 'main.tcss'
    SCREENS = {'search': Search}
    SEARCHING = False
    
    def compose(self):
        yield Header()
        with Horizontal():
            for i in iymn:
                yield DataTable(cursor_type='row', id=i, classes=i+'box', zebra_stripes=True)
        yield Footer()

    def on_mount(self):
        for i in iymn:
            table = self.query_one('#'+i)
            if i == 'items':
                table.add_column(DATA['listname'], key=DATA['listname'])
                table.focus()
            else:
                table.add_column(i.title(), key=i+'Column')
            for item in DATA[i]:
                table.add_row(item, key=item)

    def action_next(self):
        self.focused.action_cursor_down()

    def action_previous(self):
        self.focused.action_cursor_up()

    def action_sort(self, event):
        print(event)
        # focus = self.focused
        # name = focus.id
        
        # yes = self.query_one('#yes')
        # current = focus.cursor_coordinate
        # item = focus.get_cell_at(current)
        # yes.add_row(item, key=item)
        # DATA['yes'].append(item)
        # focus.remove_row(item)
        # DATA[name].remove(item)
        
    def action_yes(self):
        focus = self.focused
        name = focus.id
        yes = self.query_one('#yes')
        current = focus.cursor_coordinate
        item = focus.get_cell_at(current)
        yes.add_row(item, key=item)
        DATA['yes'].append(item)
        focus.remove_row(item)
        DATA[name].remove(item)
        
    def action_no(self):
        focus = self.focused
        name = focus.id
        no = self.query_one('#no')
        current = focus.cursor_coordinate
        item = focus.get_cell_at(current)
        no.add_row(item, key=item)
        DATA['no'].append(item)
        focus.remove_row(item)
        DATA[name].remove(item)

        
    def action_maybe(self):
        focus = self.focused
        name = focus.id
        maybe = self.query_one('#maybe')
        current = focus.cursor_coordinate
        item = focus.get_cell_at(current)
        maybe.add_row(item, key=item)
        DATA['maybe'].append(item)
        focus.remove_row(item)
        DATA[name].remove(item)
        
    def action_switch_table(self):
        current = self.focused.id
        self.query_one(f'#{nexter(current, iymn)}').focus()

    def action_reset(self):
        for i in iymn[1:]:
            DATA['items'] += DATA[i]
            DATA[i] = []
            dtable = self.query_one(f'#{i}')
            dtable.remove_column(f'{i}Column')
            dtable.clear()
        DATA['items'].sort()
        items = self.query_one('#items')
        items.remove_column(DATA['listname'])
        items.clear()
        self.on_mount()

    def action_search(self):
        self.SEARCHING = True
        self.refresh_bindings()
        items = self.query_one('#items')
        def makeResultTable(search_string):
            result = [i for i in DATA['items'] if search_string in i]
            items.clear()
            for item in result:
                items.add_row(item, key=item)
        self.push_screen('search', makeResultTable)

    def action_search_reset(self):
        items = self.query_one('#items')
        items.clear()
        for item in DATA['items']:
            items.add_row(item, key=item)
        self.SEARCHING = False
        self.refresh_bindings()

    def check_action(self, action, parameters):
        if action == 'search_reset' and self.SEARCHING == False:
            return False
        if action == 'reset' and self.SEARCHING:
            return False
        return True
        
    def on_unmount(self):
        with open('current.json', 'w', encoding='utf-8') as jf:
            json.dump(DATA, jf, indent=2)
            
def main():
    pass
    # print("Hello from nym!")


if __name__ == "__main__":
    app = nymApp()
    app.run()
    
