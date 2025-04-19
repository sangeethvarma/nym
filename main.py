import json
import click
import pyperclip

from tui import nymApp

iymn = ['items','yes', 'maybe', 'no']

@click.command()
@click.option('-j', '--json-file', type=click.File('r'), help='Path to list JSON file.')
@click.option('-l', '--list-file', type=click.File('r'), help='Path to a list file.')
@click.option('-c', '--clipboard', is_flag=True, help='Read list from the clipboard.')

def main(json_file, list_file, clipboard):
    """
    Sort a list into Yes, No, Maybe.
    """
    # Ensure only one input source is provided
    sources = [bool(json_file), bool(list_file), clipboard]
   
    if sum(sources) != 1:
        raise click.UsageError('Please specify exactly one input source: --json-file, --text-file, or --clipboard.')

    if json_file:
        try:
            DATA = json.load(json_file)
        except json.JSONDecodeError as e:
            raise click.ClickException(f'Invalid JSON file: {e}')
    else:
        listname = click.prompt('What are this a list of? ', type=str)    
        if list_file:
            DATA = {}
            DATA['items'] = list_file.read().split('\n')
            DATA.update({k : [] for k in iymn[1:]})
            DATA['listname'] = listname
        elif clipboard:
            DATA = {}
            DATA['items'] = pyperclip.paste().split('\r\n')
            DATA.update({k : [] for k in iymn[1:]})
            DATA['listname'] = listname
            
    app = nymApp(DATA)
    app.run()

if __name__ == "__main__":
    main()

    
    
