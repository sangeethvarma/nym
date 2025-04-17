import os
import subprocess
import json
from pprint import pprint
# import pyperclip

iymn = ['items','yes', 'maybe', 'no']

def get_list(filename='list', get_from_cli=True):
    if os.path.isfile(filename +'.json'):
        with open(filename + '.json', 'r', encoding='utf-8') as jf:
            DATA = json.load(jf)
            pprint(f "READ {filename}.json\n"*100)
    # elif os.path.isfile('current.json'):
    #     with open('current.json', 'r', encoding='utf-8') as jf:
    #         DATA = json.load(jf)
    elif os.path.isfile(filename):        
        with open(filename, 'r', encoding='utf-8') as listfile:
            DATA = {}
            DATA['items'] = listfile.read().split('\n')
            DATA.update({k : [] for k in iymn[1:]})
            DATA['listname'] = input('What are this a list of?\n')
            pprint(f "READ {filename} file\n"*100)
    else:
        if get_from_cli:
            line = 'hello'
            print('Paste in your list of items and press Enter...')
            items = []
            while line:
                line = input()
                if line: items.append(line)
            DATA = {'items': items}
            DATA.update({k : [] for k in iymn[1:]})
            DATA['listname'] = input('What are this a list of?\n')
        else:
            subprocess.run(['pwsh', '-Command', 'touch '+filename])
            DATA = {k : [] for k in iymn}
            DATA['listname'] = filename
            pprint(f "CREATED {filename} file\n"*100)

    return DATA

if __name__ == "__main__":
    get_list()
