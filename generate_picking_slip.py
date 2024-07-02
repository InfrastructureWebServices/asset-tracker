from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from os import path
directory = path.dirname(__file__)
wb = load_workbook(path.join(directory, 'data', 'template.xlsx'))

border = Border(
    left=Side(border_style='medium', color='00000000'),
    right=Side(border_style='medium', color='00000000'),
    bottom=Side(border_style='medium', color='00000000'),
    top=Side(border_style='medium', color='00000000')
    )

import json
with open('picking_slip.json', 'r') as f:
    data = json.loads(f.read())

ws = wb['Form']

defined_names = wb.defined_names

asset_table = ws.tables['asset_table']

insert_row_id = int(defined_names['insert_row_after'].value)
ws.insert_rows(insert_row_id, amount=2)

asset_table.ref = asset_table.ref[:-1] + str(insert_row_id-1+2)

data_range = asset_table.split(':')
data_range[0] = data_range[0][:-1] + (int(data_range[0][]))

wb.save(path.join(directory, 'output', 'output.xlsx'))

print('ok')
