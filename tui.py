import json

from textual.app import App
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Footer, Header, Input, DataTable
from textual.containers import Horizontal

from helpers import get_list

class InputScreen(ModalScreen[str]):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self):
        yield Input(placeholder = "string", id="string")
    
    def on_input_submitted(self, event):
        self.query_one(Input).value = ''
        self.dismiss(event.value)
    
class nymApp(App):
    DATA = get_list()
    iymn = ['items','yes', 'maybe', 'no']
    
    BINDINGS = [
        Binding('y', 'yes', 'mark yes'),
        Binding('x', 'no', 'mark no'),
        Binding('m', 'maybe', 'mark maybe'),
        Binding('s', 'switch_table', 'switch tables'),
        Binding('n', 'next', 'next', show=False),
        Binding('j', 'next', 'next', show=False),        
        Binding('p', 'previous', 'previous', show=False),
        Binding('k', 'previous', 'previous', show=False),
        Binding('/', 'search lists', 'search list'),
        Binding('f', 'search_reset', 'finish search'),
        Binding('S', 'save', 'save data'),
        Binding('r', 'rename', 'rename list'),
        Binding('R', 'reset', 'reset'),
        Binding('C', 'clear', 'clear'),
        Binding('o', 'open', 'open'),
        ]
    CSS_PATH = 'main.tcss'
    SCREENS = {'input': InputScreen}
    SEARCHING = False
    
    def compose(self):
        yield Header()
        with Horizontal():
            for i in self.iymn:
                yield DataTable(cursor_type='row', id=i, classes=i+'box', zebra_stripes=True)
        yield Footer()

    def on_mount(self):
        for i in self.iymn:
            table = self.query_one('#'+i)
            if i == 'items':
                table.add_column(self.DATA['listname'], key=self.DATA['listname'])
                table.focus()
            else:
                table.add_column(i.title(), key=i+'Column')
            for item in self.DATA[i]:
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
        # self.DATA['yes'].append(item)
        # focus.remove_row(item)
        # self.DATA[name].remove(item)
        
    def action_yes(self):
        focus = self.focused
        name = focus.id
        yes = self.query_one('#yes')
        current = focus.cursor_coordinate
        item = focus.get_cell_at(current)
        yes.add_row(item, key=item)
        self.DATA['yes'].append(item)
        focus.remove_row(item)
        self.DATA[name].remove(item)
        
    def action_no(self):
        focus = self.focused
        name = focus.id
        no = self.query_one('#no')
        current = focus.cursor_coordinate
        item = focus.get_cell_at(current)
        no.add_row(item, key=item)
        self.DATA['no'].append(item)
        focus.remove_row(item)
        self.DATA[name].remove(item)

    def action_maybe(self):
        focus = self.focused
        name = focus.id
        maybe = self.query_one('#maybe')
        current = focus.cursor_coordinate
        item = focus.get_cell_at(current)
        maybe.add_row(item, key=item)
        self.DATA['maybe'].append(item)
        focus.remove_row(item)
        self.DATA[name].remove(item)

    def action_switch_table(self):
        def nexter(item, items):
            i = items.index(item)
            if i + 1 == len(items):
                return items[0]
            else:
                return items[i + 1]

        current = self.focused.id
        self.query_one(f'#{nexter(current, self.iymn)}').focus()

    def action_reset(self):
        for i in self.iymn[1:]:
            self.DATA['items'] += self.DATA[i]
            self.DATA[i] = []
            dtable = self.query_one(f'#{i}')
            dtable.clear(columns=True)
        self.DATA['items'].sort()
        items = self.query_one('#items')
        items.clear(columns=True)
        self.on_mount()

    def action_save(self):
        if self.DATA['listname'] != 'cleared' and (self.DATA['items'] or self.DATA['yes'] or self.DATA['maybe']):
            with open(self.DATA['listname']+'.json', 'w', encoding='utf-8') as jf:
                json.dump(self.DATA, jf)
                
    def action_clear(self):
        self.action_save()
        for i in self.iymn:
            self.DATA[i] = []
            dtable = self.query_one(f'#{i}')
            dtable.clear(columns=True)
        self.DATA['listname'] = 'cleared'

    def action_rename(self):
        items = self.query_one('#items')
        def renameList(name):
            self.DATA['listname'] = name
            items.clear(columns=True)
            items.add_column(self.DATA['listname'])
            for item in self.DATA['items']:
                items.add_row(item, key=item)
        self.push_screen('input', renameList)

    def action_search(self):
        self.SEARCHING = True
        self.refresh_bindings()
        items = self.query_one('#items')
        def makeResultTables(search_string):
            for l in self.iymn:
                table = self.query_one('#'+l)
                result = [i for i in self.DATA[l] if search_string in i]
                table.clear()
                for item in result:
                    table.add_row(item, key=item)
        self.push_screen('input', makeResultTables)

    def action_search_reset(self):
        for l in self.iymn:
            table = self.query_one('#'+l)
            table.clear()
            for item in self.DATA[l]:
                table.add_row(item, key=item)
        self.SEARCHING = False
        self.refresh_bindings()

    def action_open(self):
        def openFile(name):
            self.action_clear()
            self.DATA = get_list(name+'.json', False)
            self.DATA['listname'] = name
            self.on_mount()
        self.push_screen('input', openFile)

    def check_action(self, action, parameters):
        if action == 'search_reset' and not self.SEARCHING:
            return False
        if action == 'reset' and self.SEARCHING:
            return False
        return True
                
    def on_unmount(self):
        self.action_save()

if __name__ == "__main__":
    app = nymApp()
    app.run()
