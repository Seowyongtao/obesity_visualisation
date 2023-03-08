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

app.layout = html.Div([
    dcc.Dropdown(options=['Alcohol', 'Smoke'], value='Alcohol', id='dropdown_list'),
    dcc.Graph(
        id='scatter-chart',
        figure=px.scatter(merged_df, x="Alcohol_value", y="Obesity_value", size='Alcohol_value', title="Scatter Plot")
    )
])


@callback(
    Output(component_id='scatter-chart', component_property='figure'),
    Input(component_id='dropdown_list', component_property='value'),
    prevent_initial_call=True
)
def update_plot(chosen_data):  # the function argument comes from the component property of the Input

    if chosen_data == 'Alcohol':

        new_merged_df = pd.merge(obesity_sorted_by_value_df, alcohol_sorted_by_value_df, on='LOCATION')
        new_merged_df = new_merged_df[['LOCATION', 'Value_x', 'Value_y']]
        new_merged_df = new_merged_df.rename(columns={'Value_x': 'Obesity_value', 'Value_y': 'Alcohol_value'})

        fig = px.scatter(new_merged_df, x="Alcohol_value", y="Obesity_value", size='Alcohol_value',
                         title="Scatter Plot")

    else:

        new_merged_df = pd.merge(obesity_sorted_by_value_df, smoke_sorted_by_value_df, on='LOCATION')
        new_merged_df = new_merged_df[['LOCATION', 'Value_x', 'Value_y']]
        new_merged_df = new_merged_df.rename(columns={'Value_x': 'Obesity_value', 'Value_y': 'Smoke_value'})

        fig = px.scatter(new_merged_df, x="Smoke_value", y="Obesity_value", size='Smoke_value',
                         title="Scatter Plot")

    return fig  # the returned objects are assigned to the component properties of the Outputs


if __name__ == '__main__':
    app.run(port=8005)