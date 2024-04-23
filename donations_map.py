import dash
from dash import dcc
from dash import html
from dash import Input, Output, State
import plotly.express as px
import json
import pandas as pd
from flask import Flask
from flask_compress import Compress

server = Flask(__name__)
Compress(server)
server.config['COMPRESS_MIN_SIZE'] = 500  # Compress responses over 500 bytes
app = dash.Dash(__name__, server=server)

with open(r'C:\Users\NickWard\OneDrive\Apps\Donations map vDEPLOY\Mapping\gz_2010_us_050_00_20m.json', 'r') as f:
    counties = json.load(f)

#This is code for lower dimensionality GeoJSON
'''for feature in counties['features']:
    # Ensure FIPS is five digits long
    county_code = feature['id']
    fips_code = county_code.zfill(5)  # Add leading zero if needed
    feature['properties']['FIPS'] = fips_code'''

# Sample CSV file that maps FIPS codes to state information
'''state_fips_mapping = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming"
}'''

# Map state information to the GeoJSON
'''for feature in counties['features']:
    # Extract state code from FIPS
    fips_code = feature['properties']['FIPS']
    state_code = fips_code[:2]  # First two digits are the state code
    feature['properties']['STATE'] = state_fips_mapping.get(state_code, "Unknown")  # Add state info'''

#This is the code for the high dimension GeoJSON
for feature in counties['features']:
    state_code = feature['properties']['STATE']
    county_code = feature['properties']['COUNTY']
    # Ensure leading zeros are preserved when necessary
    fips_code = f"{state_code}{county_code.zfill(3)}"
    feature['properties']['FIPS'] = fips_code

df = pd.read_csv(r'C:\Users\NickWard\OneDrive\Apps\Donations map vDEPLOY\Data\DATA FOR APP v2.csv', dtype = {'FIPS': str})
states = sorted(df['state'].unique())
state_options = [{'label': 'All', 'value': 'All'}] + [{'label': state, 'value': state} for state in states]

def generate_choropleth(dataframe, value_column, geojson):
    #print("Generating map with:", dataframe.head())

    color_discrete_map = {
        '0-$0.4' : '#ffffe0',
        '$0.4-$1.0' : '#a5d5d8',
        '$1.0-$2.1' : '#73a2c6',
        '$2.1-$4.6' : '#4771b2',
        '$4.6-$695.0' : '#00429d'
    }

    fig = px.choropleth(
        dataframe,  # Use the passed DataFrame
        geojson=geojson,
        locations='FIPS',  # Ensure your FIPS column is named 'FIPS'
        color=value_column,
        color_discrete_map=color_discrete_map,
        featureidkey="properties.FIPS",
        scope="usa",
        labels={value_column: 'Donations per capita'}
    )
    fig.update_geos(fitbounds=None, visible=False)
    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0},
                      mapbox_zoom=3
                      )
    return fig

app.layout = html.Div([
    dcc.Store(id='stored-geojson', data=counties, storage_type='session'),
    dcc.Store(id='stored-data', data=df.to_dict('records'), storage_type='session'),
    dcc.Dropdown(
        id='state-dropdown',
        options=state_options,
        value="Alabama",
        placeholder='Select a state',
    ),
    dcc.Dropdown(
        id='party-dropdown',
        options=[
            {'label': 'Democratic Donations', 'value': 'DEM'},
            {'label': 'Republican Donations', 'value': 'REP'},
            {'label': 'Other Donations', 'value': 'OTHER_per_capita'},
            {'label': 'Total Donations', 'value': 'TOTAL_per_capita'}
        ],
        value='TOTAL'
    ),
    dcc.Graph(id='map-graph')
])

@app.callback(
    Output('map-graph', 'figure'),
    [Input('party-dropdown', 'value'), Input('state-dropdown', 'value')],
    [State('stored-data', 'data'), State('stored-geojson', 'data')]
)

def update_map(selected_party, selected_state, stored_data, stored_geojson):
    filtered_df=pd.DataFrame(stored_data)
    geojson = stored_geojson
    #print(geojson)

    if selected_state == 'All':
        # If 'All' is selected, use the entire DataFrame
        pass
    else:
        # Filter the DataFrame for the selected state
        filtered_df = filtered_df[filtered_df['state'] == selected_state] if 'state' in filtered_df.columns else pd.DataFrame()

    # Generate the choropleth map using the filtered DataFrame and stored GeoJSON
    print(filtered_df.head())
    return generate_choropleth(filtered_df, selected_party, geojson)

if __name__ == '__main__':
    app.run_server(debug=True)
