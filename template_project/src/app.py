import pandas as pd
import json
import plotly.express as px
import streamlit as st


st.title("Volcanoes of the world")

def prepare_data_for_map(df):
    # Load GeoJSON data
    with open("countries.geojson", "r") as f:
        geojson_data = json.load(f)



# Clean the 'Elev' column by replacing negative values with a default value
    df['Elevation'] = df['Elev'].apply(lambda x: max(x, 0))
    
    countries_data = df.groupby(['Country', 'Population (2020)']).agg({
    'Latitude': 'mean',
    'Longitude': 'mean',
    'Elevation': 'mean',
    'Type': 'first',
    'Status': 'first',
    'Last Known': 'first',
}).reset_index()



    # Create a dictionary to store map data
    map_data = {
        'geojson': geojson_data,
        'df': countries_data,
        'geo_column': 'Country',
        'value_column': 'Population (2020)',
        'color_scale': 'Viridis',
        'labels': {'Population (2020)': 'Population'},
        'mapbox_style': "carto-positron",
        'marker_size_column': 'Elevation',
        'holocene_color': 'red',  # Set the color for Holocene activity
        'marker_color': 'blue'
    }

    return map_data

# Example usage
df = pd.read_csv("volcano_ds_pop.csv")
map_data = prepare_data_for_map(df)

# Create choropleth map
fig = px.choropleth_mapbox(map_data['df'],
                            geojson=map_data['geojson'],
                            featureidkey='properties.ADMIN',
                            locations=map_data['geo_column'],
                            color=map_data['value_column'],
                            color_continuous_scale=map_data['color_scale'],
                            opacity=0.5,
                            labels=map_data['labels']
                            )

# Update the initial zoom level
fig.update_geos(fitbounds="locations", visible=False)

# Add volcano markers with different colors for "Holocene" activity
fig.add_trace(px.scatter_mapbox(df[df['Status'] == 'Holocene'],
                                lat='Latitude',
                                lon='Longitude',
                                text='Volcano Name',
                                hover_data=['Elevation', 'Type', 'Status'],
                                color_discrete_sequence=[map_data['holocene_color']],
                                size=map_data['marker_size_column'],
                                size_max=10,
                                opacity=0.8
                                ).data[0])

# Add volcano markers for other activities
fig.add_trace(px.scatter_mapbox(df[df['Status'] != 'Holocene'],
                                lat='Latitude',
                                lon='Longitude',
                                text='Volcano Name',
                                hover_data=['Elevation', 'Type', 'Status'],
                                color_discrete_sequence=[map_data['marker_color']],
                                size=map_data['marker_size_column'],
                                size_max=10,
                                opacity=0.8
                                ).data[0])

fig.update_layout(mapbox_style=map_data['mapbox_style'], margin={"r": 0, "t": 0, "l": 0, "b": 0})
#fig.show()
st.plotly_chart(fig)