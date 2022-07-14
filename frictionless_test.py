from frictionless import describe
from frictionless import Schema
import pprint


# studies.csv
with open('studies.csv') as file:
    print(file.read())

schema = Schema.describe('studies.csv')
schema.to_yaml('studies.schema.yaml')

schema.get_field("study_id").title = "Study identifier"
schema.primary_key = "study_id"

schema.get_field("first_author").title = "Identifier of the neighbor"
schema.get_field("year").title = "Year of study publication"
schema.get_field("title").title = "Publication title"
schema.get_field("catalogued").title = "Data included in database: True or False"
schema.get_field("doi").title = "Publication DOI"


schema.to_yaml("studies.schema.yaml")


#measurement_info.csv

schema = Schema.describe('measurement_info.csv')
schema.to_yaml('measurement_info.schema.yaml')

schema.get_field("study_id").title = "Study identifier"
schema.get_field("study_id").type = "integer"
schema.foreign_keys = "study_id"

schema.get_field("measurement_id").title = "Measurement identifier"
schema.primary_key = "measurement_id"

schema.get_field("location_source").title = "Source of location information"
schema.get_field("y_lat").title = "Y coordinate in local coordinate system or latitude"
schema.get_field("x_lon").title = "X coordinate in local coordinate system or longitude"
schema.get_field("epsg").title = "epsg code if coordinates are not EPSG:4326 (lat/lon)"
schema.get_field("elevation_source").title = "Source of elevation information if not published"
schema.get_field("elevation_masl").title = "Elevation in meters above sea level"
schema.get_field("glacier_name").title = "Glacier name"
schema.get_field("rgi_id").title = "Randolph Glacier Invetory glacier id"
schema.get_field("start_date").title = "Start of measurement period"
schema.get_field("start_date").description = "If only measurement year is known, this is the first day of the year; if only measurement month is known, this is the first day of the month. If measurement happend on a specific day, start_date is equal to end_date."
schema.get_field("end_date").title = "End of measurement period"
schema.get_field("end_date").description = "If only measurement year is known, this is the last day of the year; if only measurement month is known, this is the last day of the month. If measurement happend on a specific day, start_date is equal to end_date"
schema.get_field("to_bottom").title = "Borehole reached glacier bed: True or False"
schema.get_field("site_description").title = "Description of measurement site"
schema.get_field("site_description").example = "Ablation area; crater rim; summit region etc."
schema.get_field("notes").title = "Additional notes"
schema.get_field("extraction_method").title = "Means by which data was obtained / added"

schema.to_yaml("measurement_info.schema.yaml")

#data.csv
schema = Schema.describe('temperatures.csv')
schema.to_yaml('temperatures.schema.yaml')

schema.get_field("measurement_id").title = "Measurement identifier"
schema.foreign_keys = "measurement_id"

schema.get_field("temperature_degC").title = "Temperature in degrees Celcius"
schema.get_field("depth_m").title = "Measurement depth in meters from the surface (positive increasing)"

schema.to_yaml("temperatures.schema.yaml")

#Generate templates?
from frictionless import Resource
import pandas as pd

with Resource('studies.csv') as resource:
    print(f'Header: {resource.header}')
    print(f'Valid: {resource.header.valid}')

studies_template = pd.DataFrame(columns=resource.header.to_list())
#studies_template.to_csv('studies_template.csv', index=False)

with Resource('measurement_info.csv') as resource:
    print(f'Header: {resource.header}')
    print(f'Valid: {resource.header.valid}')

measurement_info_template = pd.DataFrame(columns=resource.header.to_list())
#studies_template.to_csv('measurement_info_template.csv', index=False)


with Resource('temperatures.csv') as resource:
    print(f'Header: {resource.header}')
    print(f'Valid: {resource.header.valid}')

temperatures_template = pd.DataFrame(columns=resource.header.to_list())
#studies_template.to_csv('temperatures_template.csv', index=False)

with pd.ExcelWriter('ice_temperatures_template.xlsx', mode='w') as writer:
    studies_template.to_excel(writer, sheet_name='studies', index=False)
    measurement_info_template.to_excel(writer, sheet_name='measurement_info', index=False)
    temperatures_template.to_excel(writer, sheet_name='data', index=False)

workbook  = writer.book
worksheet = writer.sheets['measurement_info']

date_format = workbook.add_format({'num_format': 'yyyy-MM-dd'})
worksheet.set_column('C:P', 100)
#worksheet.set_column('K:L', date_format)

writer.save() #doesn't seem to write changes to the file
