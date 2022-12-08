from pprint import pprint
from frictionless import extract
from frictionless import validate


with open('datapackage.yml') as file:
    print(file.read())

rows = extract('datapackage.yml')
pprint(rows)

report = validate('datapackage.yml')
pprint(report.flatten(["cells", "fieldName", "type", "description"]))
pprint(report)
