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

# transform alcohol dataset
alcohol_df = pd.read_csv("alcohol_by_country.csv")
alcohol_remove_col_df = alcohol_df[['LOCATION', 'TIME', 'Value']]
alcohol_maxyear_df = alcohol_remove_col_df.loc[alcohol_remove_col_df.groupby('LOCATION')['TIME'].idxmax()].sort_index()
alcohol_sorted_by_value_df = alcohol_maxyear_df.sort_values(by="Value")

# transform smoke dataset
smoke_df = pd.read_csv("smoke_by_country.csv")
smoke_remove_col_df = smoke_df[['LOCATION', 'TIME', 'Value']]
smoke_maxyear_df = smoke_remove_col_df.loc[smoke_remove_col_df.groupby('LOCATION')['TIME'].idxmax()].sort_index()
smoke_sorted_by_value_df = smoke_maxyear_df.sort_values(by="Value")

merged_df = pd.merge(obesity_sorted_by_value_df, alcohol_sorted_by_value_df, on='LOCATION')
merged_df = merged_df[['LOCATION', 'Value_x', 'Value_y']]
merged_df = merged_df.rename(columns={'Value_x': 'Obesity_value', 'Value_y': 'Alcohol_value'})

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.A(
                    html.Img(id="logo", src=app.get_asset_url("dash-logo.png")),
                    href="https://plotly.com/dash/",
                ),
                html.H4(children="A Comparative Analysis of Obesity & Lifestyle Factors In OECD Countries"),
                html.P(
                    id="description",
                    children="† Obesity has become a major public health concern in many countries. "
                             "While several lifestyle factors have been identified as potential contributors to obesity, "
                             "the relationship between obesity and these factors is not well understood.",
                ),
            ],
        )
    ])

if __name__ == '__main__':
    app.run(port=8005)