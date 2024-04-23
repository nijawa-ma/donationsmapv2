from dash import Dash, html, dcc
import json
import plotly.graph_objects as go  # Use Plotly Graph Objects for more control

app = Dash(__name__)

# Load GeoJSON file
with open(r'C:\Users\NickWard\OneDrive\Apps\Donations and economy\Mapping\gz_2010_us_050_00_500k.json', 'r') as f:
    counties = json.load(f)

for feature in counties['features']:
    state_code = feature['properties']['STATE']
    county_code = feature['properties']['COUNTY']
    # Ensure leading zeros are preserved when necessary
    fips_code = f"{state_code}{county_code.zfill(3)}"
    feature['properties']['FIPS'] = fips_code

def display_simple_geojson(geojson):
    # Create a map using only GeoJSON, no DataFrame required
    fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=[feature['properties']['FIPS'] for feature in counties['features']],
                                        z=[1]*len(geojson['features']),  # Dummy variable for coloring
                                        colorscale="Viridis",  # Uniform color
                                        marker_opacity=0.5,  # Make counties semi-transparent
                                        marker_line_width=0.1))  # No outline for counties
    # Set mapbox style and initial view position
    fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

# Set the layout of the Dash app
app.layout = html.Div([
    dcc.Graph(figure=display_simple_geojson(counties))
])

if __name__ == '__main__':
    app.run_server(debug=True)