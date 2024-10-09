from lxml import etree as ET
import dash
from dash import dcc, html
import dash_table
import pandas as pd
import plotly.express as px
import os

# Function to load and parse the XML
def load_ccda_file(file_path):
    tree = ET.parse(file_path)
    return tree.getroot()

# Function to extract patient demographics
def get_patient_demographics(root):
    namespace = {'hl7': 'urn:hl7-org:v3'}
    patient_info = root.find(".//hl7:patientRole", namespaces=namespace)
    patient_data = {
        'Name': f"{patient_info.find('.//hl7:given', namespaces=namespace).text} {patient_info.find('.//hl7:family', namespaces=namespace).text}",
        'Gender': patient_info.find('.//hl7:administrativeGenderCode', namespaces=namespace).get('displayName'),
        'Birth Date': patient_info.find('.//hl7:birthTime', namespaces=namespace).get('value'),
        'Address': f"{patient_info.find('.//hl7:streetAddressLine', namespaces=namespace).text}, {patient_info.find('.//hl7:city', namespaces=namespace).text}, {patient_info.find('.//hl7:state', namespaces=namespace).text}",
        'Phone': patient_info.find('.//hl7:telecom', namespaces=namespace).get('value')
    }
    return patient_data

# Extract encounters
def get_encounters(root):
    namespace = {'hl7': 'urn:hl7-org:v3'}
    encounters = []
    for encounter in root.findall(".//hl7:encounter", namespaces=namespace):
        data = {
            'Code': encounter.find('hl7:code', namespaces=namespace).get('displayName'),
            'Effective Time': encounter.find('hl7:effectiveTime/hl7:low', namespaces=namespace).get('value')
        }
        encounters.append(data)
    return pd.DataFrame(encounters)

# Initialize Dash app
app = dash.Dash(__name__)

# Get list of XML files in the resources folder
resources_folder = 'resources'
xml_files = [f for f in os.listdir(resources_folder) if f.endswith('.xml')]

# Set initial file and parse it
initial_file = os.path.join(resources_folder, xml_files[0])
root = load_ccda_file(initial_file)

demographics = get_patient_demographics(root)
encounters_df = get_encounters(root)

app.layout = html.Div([
    html.H1("CCDA Document Explorer"),
    html.Div([
        html.Label("Select CCDA File:"),
        dcc.Dropdown(
            id='file-dropdown',
            options=[{'label': f, 'value': os.path.join(resources_folder, f)} for f in xml_files],
            value=initial_file
        )
    ]),
    html.Div([
        html.H3("Patient Demographics"),
        html.Ul(id='demographics-list', children=[html.Li(f"{key}: {value}") for key, value in demographics.items()])
    ]),
    html.Div([
        html.H3("Encounters"),
        dash_table.DataTable(
            id='encounters-table',
            columns=[{"name": i, "id": i} for i in encounters_df.columns],
            data=encounters_df.to_dict('records')
        )
    ])
])

@app.callback(
    [dash.dependencies.Output('demographics-list', 'children'),
     dash.dependencies.Output('encounters-table', 'data')],
    [dash.dependencies.Input('file-dropdown', 'value')]
)
def update_output(file_path):
    root = load_ccda_file(file_path)
    demographics = get_patient_demographics(root)
    encounters_df = get_encounters(root)
    demographics_list = [html.Li(f"{key}: {value}") for key, value in demographics.items()]
    return demographics_list, encounters_df.to_dict('records')

server = app.server

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', debug=True)