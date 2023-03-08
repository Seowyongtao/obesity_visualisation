from dash import Dash, dcc, html, Output, Input, State, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# transform obesity dataset
obesity_df = pd.read_csv("obesity_by_country.csv")
obesity_mean_df = obesity_df.groupby(['LOCATION', 'TIME'])['Value'].mean().reset_index()
obesity_maxyear_df = obesity_mean_df.loc[obesity_mean_df.groupby('LOCATION')['TIME'].idxmax()]
obesity_sorted_by_value_df = obesity_maxyear_df.sort_values(by="Value")
obesity_location_value = obesity_sorted_by_value_df[['LOCATION', 'Value']]
print(obesity_location_value.head(5))

# Create choropleth map figure
fig = px.choropleth(
    data_frame=obesity_df,
    locations='LOCATION',
    color='Value',
    locationmode='ISO-3',
    color_continuous_scale='Greens_r',
    range_color=[0, obesity_df['Value'].max()],
)

# Set the layout of the map
fig.update_layout(
    geo=dict(
        bgcolor='white',  # Set the background color of the map
        showframe=False,  # Remove the frame around the map
        showcoastlines=False,  # Remove the coastlines from the map
        projection_type='equirectangular',  # Choose a projection type
    ),
)

app.layout = html.Div(
    # style={'backgroundColor': 'black'},  # Set the background color of the app
    children=[
        html.H1('Choropleth Map', style={'color': 'black'}),  # Set the text color of the heading
        html.Div(
            style={'backgroundColor': 'black', 'padding': '50px'},  # Set the background color of the container
            children=[
                dcc.Graph(figure=fig, style={'backgroundColor': 'black', 'padding': '50px'} ),
            ],
        ),
    ],
)


if __name__ == '__main__':
    app.run(port=8005)