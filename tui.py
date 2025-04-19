import json
import os
import pyperclip

from textual.app import App
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Footer, Header, Input, DataTable, OptionList
from textual.widgets.option_list import Option
from textual.containers import Horizontal

iymn = ['items','yes', 'maybe', 'no']

class InputScreen(ModalScreen[str]):
    BINDINGS = [('escape', 'app.pop_screen', 'Pop screen')]

    def compose(self):
        yield Input(placeholder = 'string', id='string')

    def on_input_submitted(self, event):
        self.query_one(Input).value = ''
        self.dismiss(event.value)

class OptionScreen(ModalScreen[str]):
    fileList = [i.split('.')[0] for i in os.listdir('./lists/') if i.endswith('.json')]
    BINDINGS = [('escape', 'app.pop_screen', 'Pop screen'),
                ('n', 'focused.cursor_down', 'next'),
                ('p', 'focused.cursor_up', 'previous'),
                ('j', 'focused.cursor_down', 'next'),
                ('k', 'focused.cursor_up', 'previous'),
                ]

    def compose(self):
        yield Input(placeholder = 'file', id='input')
        yield OptionList(*self.fileList, id='optList')

    def on_mount(self):
        print('hello')
        self.query_one('#input').focus()

    def on_input_changed(self, event):
        optList = self.query_one('#optList')
        optList.clear_options()
        newList = [i for i in self.fileList if event.value in i]
        optList.add_options(new_options=newList)

    def on_option_list_option_selected(self, event):
        optList = event.option_list
        opt = optList.options[optList.highlighted].prompt
        self.dismiss(opt)
    
class nymApp(App):
    iymn = ['items','yes', 'maybe', 'no']
    ymnd = {'y': 'yes', 'm': 'maybe', 'x':'no'}
    # DATA = {k: [] for k in iymn}
    # DATA['listname'] = 'default'
    
    BINDINGS = [
        Binding('y', 'yes', 'mark yes'),
        Binding('x', 'no', 'mark no'),
        Binding('m', 'maybe', 'mark maybe'),
        Binding('M', 'maybes_to_items', 'maybes to items'),
        Binding('X', 'clear_nos', 'clear nos'),
        Binding('n', 'next', 'next', show=False),
        Binding('j', 'next', 'next', show=False),        
        Binding('p', 'previous', 'previous', show=False),
        Binding('k', 'previous', 'previous', show=False),
        Binding('/', 'search', 'search list'),
        Binding('f', 'search_reset', 'finish search'),
        Binding('S', 'save', 'save data'),
        Binding('r', 'rename', 'rename list'),
        Binding('R', 'reset', 'reset'),
        Binding('C', 'clear', 'clear'),
        Binding('o', 'open', 'open'),
        ]
    CSS_PATH = 'main.tcss'
    SCREENS = {'input': InputScreen, 'options': OptionScreen}
    SEARCHING = False

    def __init__(self, DATA):
        super().__init__()
        self. DATA = DATA
            
    def compose(self):
        yield Header()
        with Horizontal():
            for i in self.iymn:
                yield DataTable(cursor_type='row', id=i, classes=i+'box', zebra_stripes=True)
        yield Footer()

    def populate_tables(self):
        for i in self.iymn:
            table = self.query_one('#'+i)
            if i == 'items':
                table.add_column(self.DATA['listname'], key=self.DATA['listname'])
                table.focus()
            else:
                table.add_column(i.title(), key=i+'Column')
            for item in self.DATA[i]:
                table.add_row(item, key=item)

    def on_mount(self):
        self.populate_tables()
        
    def action_next(self):
        self.focused.action_cursor_down()

    def action_previous(self):
        self.focused.action_cursor_up()

    def on_key(self, event):
        if (i:=event.key) in ['y','m','x']:
            dest = self.ymnd[i]
            focus = self.focused
            source = focus.id
            if dest != source:
                destTable = self.query_one('#'+ dest)
                cursor = focus.cursor_coordinate
                try:
                    item = focus.get_cell_at(cursor)
                    destTable.add_row(item, key=item)
                    self.DATA[dest].append(item)
                    focus.remove_row(item)
                    self.DATA[source].remove(item)
                except:
                    pass
        
    def action_yes(self):
        pass

    def action_no(self):
        pass

    def action_maybe(self):
        pass

    def action_reset(self):
        for i in self.iymn[1:]:
            self.DATA['items'] += self.DATA[i]
            self.DATA[i] = []
            dtable = self.query_one(f'#{i}')
            dtable.clear(columns=True)
        self.DATA['items'].sort()
        items = self.query_one('#items')
        items.clear(columns=True)
        self.populate_tables()

    def action_save(self):
        if self.DATA['listname'] != 'cleared' and (self.DATA['items'] or self.DATA['yes'] or self.DATA['maybe']):
            with open('./lists/'+self.DATA['listname']+'.json', 'w', encoding='utf-8') as jf:
                json.dump(self.DATA, jf)
                
    def action_clear(self):
        self.action_save()
        for i in self.iymn:
            self.DATA[i] = []
            dtable = self.query_one(f'#{i}')
            dtable.clear(columns=True)
        self.DATA['listname'] = 'cleared'

    def action_clear_nos(self):
        self.DATA['no'] = []
        noTable = self.query_one('#no')
        noTable.clear()

    def action_maybes_to_items(self):
        self.DATA['items'] += self.DATA['maybe']
        self.DATA['items'].sort()
        self.DATA['maybe'] = []
        items = self.query_one('#items')
        maybes = self.query_one('#maybe')
        items.clear()
        maybes.clear()        
        for item in self.DATA['items']:
            items.add_row(item, key=item)

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
            if name:
                self.action_clear()
                with open('./lists/'+name+'.json') as jf:
                    self.DATA = json.load(jf)
                self.populate_tables()
        self.push_screen('options', openFile)

    def check_action(self, action, parameters):
        if action == 'search_reset' and not self.SEARCHING:
            return False
        if action == 'reset' and self.SEARCHING:
            return False
        return True
                
    def on_unmount(self):
        self.action_save()

if __name__ == '__main__':
    DATA = {"items": ["sangeeth.blog", "sangeeth.cc", "sangeeth.codes", "sangeeth.fm", "sangeeth.fyi", "sangeeth.ink", "sangeeth.life", "sangeeth.site", "sangeeth.works"], "yes": [], "maybe": [], "no": [], "listname": "personal domains"}
    app = nymApp(DATA)
    app.run()
