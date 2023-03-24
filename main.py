from dash import Dash, dcc, html, Output, Input, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#############################################################

# Data Processing area #

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

# transform social support dataset
social_support_df = pd.read_csv("socialsupport_by_country.csv")
social_support_remove_col_df = social_support_df[['LOCATION', 'TIME', 'Value']]
social_support_maxyear_df = social_support_remove_col_df.loc[
    social_support_remove_col_df.groupby('LOCATION')['TIME'].idxmax()].sort_index()
social_support_sorted_by_value_df = social_support_maxyear_df.sort_values(by="Value")

# merge obesity and alcohol dataset
merged_df = pd.merge(obesity_sorted_by_value_df, alcohol_sorted_by_value_df, on='LOCATION')
merged_df = merged_df[['LOCATION', 'Value_x', 'Value_y']]
merged_df = merged_df.rename(columns={'Value_x': 'Obesity_value', 'Value_y': 'Alcohol_value'})

# country list
country_df = obesity_sorted_by_value_df[['LOCATION']]
country_list = country_df['LOCATION'].tolist()

# Data filtered by country (For line chart part)
obesity_full_df = pd.read_csv("obesity_by_country_full.csv")
obesity_mean_full_df = obesity_full_df.groupby(['LOCATION', 'TIME'])['Value'].mean().reset_index()
mask = obesity_mean_full_df['LOCATION'] == country_list[0]
obesity_mean_full_filtered_df = obesity_mean_full_df[mask]

alcohol_full_df = pd.read_csv("alcohol_by_country_full.csv")
alcohol_mean_full_df = alcohol_full_df.groupby(['LOCATION', 'TIME'])['Value'].mean().reset_index()
mask = alcohol_mean_full_df['LOCATION'] == country_list[0]
alcohol_mean_full_filtered_df = alcohol_mean_full_df[mask]

#############################################################

# Figures and Components area #

# Choropleth Map

fig_map = px.choropleth(data_frame=obesity_sorted_by_value_df
                        , locations='LOCATION'
                        , color='Value'
                        , locationmode='ISO-3'
                        , color_continuous_scale='Aggrnyl'
                        , range_color=[0, obesity_sorted_by_value_df['Value'].max()]
                        , labels={'Value': 'Obese<br>(population %)'})

fig_map = fig_map.update_layout(geo=dict(bgcolor='black',
                                         projection_type='orthographic',
                                         showocean=True, oceancolor="lightblue",
                                         showland=True, landcolor="white"),
                                paper_bgcolor='black',
                                margin=dict(l=0, r=0, t=0, b=0),
                                font_color='#00ff85')

# Scatter Plot

fig_scatterPlot = px.scatter(merged_df
                             , x='Alcohol_value', y='Obesity_value'
                             , size='Obesity_value'
                             , title='Obese (% of population aged 15+) vs Alcohol Consumption (Litre/Capita, aged 15+)'
                             , color='Alcohol_value'
                             , color_continuous_scale=['white', '#62fbd3', '#00ff85']
                             , color_discrete_sequence=['#00ff85']
                             , labels={
                                    "Alcohol_value": "Alcohol Consumption",
                                    "Obesity_value": "Obesity"
                                })

fig_scatterPlot = fig_scatterPlot.update_layout(
    plot_bgcolor='black'
    , paper_bgcolor='black'
    , font_color='#00ff85')

# Line chart

fig_lineChart1 = px.line(obesity_mean_full_filtered_df
                         , x="TIME", y="Value"
                         , title='Obese (% of population aged 15+)'
                         , markers=True
                         , labels={
                                 "TIME": "Year",
                                 "Value": "Population (%)"
                           })

fig_lineChart1 = fig_lineChart1.update_layout(
    plot_bgcolor='black'
    , paper_bgcolor='black'
    , font_color='#00ff85')

fig_lineChart1 = fig_lineChart1.update_traces(
    line_color='#00ff85')

fig_lineChart2 = px.line(alcohol_mean_full_filtered_df
                         , x="TIME", y="Value"
                         , title='Alcohol Consumption (lcpd, aged 15+)'
                         , markers=True
                         , labels={
                                 "TIME": "Year",
                                 "Value": "Litre/Capita"
                           })

fig_lineChart2 = fig_lineChart2.update_layout(
    plot_bgcolor='black'
    , paper_bgcolor='black'
    , font_color='#00ff85')

fig_lineChart2 = fig_lineChart2.update_traces(
    line_color='red')

#############################################################

# App Layout #

app.layout = html.Div(
    id="root",
    children=[

        # Header

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
                    children="Obesity has become a major public health concern in many countries. "
                             "While several lifestyle factors have been identified as potential contributors to obesity, "
                             "the relationship between obesity and these factors is not well understood.",
                ),
            ],
        ),

        # Map

        html.Div(
            children=[
                dbc.Row([

                    dbc.Col([
                        dcc.Graph(
                            id='map',
                            figure=fig_map
                        ),
                    ], width=6, className='barContainer'),

                    dbc.Col([
                        dbc.Row([

                            dbc.Col([
                                dcc.Graph(
                                    id='pie1'
                                )
                            ], width=6, className='pieContainer'),

                            dbc.Col([
                                dcc.Graph(
                                    id='pie2'
                                )
                            ], width=6, className='pieContainer'),

                            dbc.Col([
                                dcc.Graph(
                                    id='pie3'
                                )
                            ], width=6, className='pieContainer'),

                            dbc.Col([
                                dcc.Graph(
                                    id='pie4'
                                )
                            ], width=6, className='pieContainer')

                        ])
                    ], width=6, className='barContainer'),

                ]),
            ]
        ),

        # Bar Container 1

        html.Div(
            children=[
                dbc.Row([

                    dbc.Col([
                        dcc.Graph(
                            id='barChart1',
                            figure=px.bar(obesity_sorted_by_value_df
                                          , x='LOCATION', y='Value'
                                          , color_discrete_sequence=['#00ff85']
                                          , text_auto='.2s'
                                          , labels={
                                                 "LOCATION": "Country",
                                                 "Value": "Population (%)"
                                             }).update_layout(
                                plot_bgcolor='black',
                                paper_bgcolor='black',
                                font_color='#00ff85',
                                xaxis_tickangle=-45,
                                title={
                                    'text': "<b> Obese (% of population aged 15+) </b>",
                                    'font': {
                                        'size': 20,
                                        'color': '#00ff85'
                                    }
                                }
                            ).update_traces(textposition="outside"),
                            style={
                                'border': '2px solid white',
                                'border-radius': '2px',
                                'border-width': 'thin'
                            }
                        ),
                    ], width=6, className='barContainer'),

                    dbc.Col([
                        dcc.Graph(
                            id='barChart2',
                            figure=px.bar(alcohol_sorted_by_value_df
                                          , x='LOCATION', y='Value'
                                          , color_discrete_sequence=['#00ff85']
                                          , text_auto='.2s'
                                          , labels={
                                                "LOCATION": "Country",
                                                "Value": "Litre/Capita"
                                            }).update_layout(
                                plot_bgcolor='black',
                                paper_bgcolor='black',
                                font_color='#00ff85',
                                xaxis_tickangle=-45,
                                title={
                                    'text': "<b> Alcohol Consumption (lcpd, aged 15+) </b>",
                                    'font': {
                                        'size': 20,
                                        'color': '#00ff85'
                                    }
                                }
                            ).update_traces(textposition="outside"),
                            style={
                                'border': '2px solid white',
                                'border-radius': '2px',
                                'border-width': 'thin'
                            }
                        ),
                    ], width=6, className='barContainer'),

                ]),
            ]
        ),

        # Bar Container 2

        html.Div(
            children=[
                dbc.Row([

                    dbc.Col([
                        dcc.Graph(
                            id='barChart3',
                            figure=px.bar(smoke_sorted_by_value_df
                                          , x='LOCATION', y='Value'
                                          , color_discrete_sequence=['#00ff85']
                                          , text_auto='.2s'
                                          , labels={
                                                "LOCATION": "Country",
                                                "Value": "Population (%)"
                                            }).update_layout(
                                plot_bgcolor='black',
                                paper_bgcolor='black',
                                font_color='#00ff85',
                                xaxis_tickangle=-45,
                                title={
                                    'text': "<b> Daily Smokers (% of population aged 15+) </b>",
                                    'font': {
                                        'size': 20,
                                        'color': '#00ff85'
                                    }
                                }
                            ).update_traces(textposition="outside"),
                            style={
                                'border': '2px solid white',
                                'border-radius': '2px',
                                'border-width': 'thin'
                            }
                        ),
                    ], width=6, className='barContainer'),

                    dbc.Col([
                        dcc.Graph(
                            id='barChart4',
                            figure=px.bar(social_support_sorted_by_value_df
                                          , x='LOCATION', y='Value'
                                          , color_discrete_sequence=['#00ff85']
                                          , text_auto='.2s'
                                          , labels={
                                                "LOCATION": "Country",
                                                "Value": "Population (%)"
                                            }).update_layout(
                                plot_bgcolor='black',
                                paper_bgcolor='black',
                                font_color='#00ff85',
                                xaxis_tickangle=-45,
                                title={
                                    'text': "<b> Social Support (% of population aged 15+) </b>",
                                    'font': {
                                        'size': 20,
                                        'color': '#00ff85'
                                    }
                                }
                            ).update_traces(textposition="outside"),
                            style={
                                'border': '2px solid white',
                                'border-radius': '2px',
                                'border-width': 'thin'
                            }
                        ),
                    ], width=6, className='barContainer'),

                ]),
            ]
        ),

        # Scatter Plot Container

        html.Div(
            children=[
                dbc.Row([
                    dbc.Col([
                        'Select a Lifestyle Factor to compare with:',
                        dcc.Dropdown(id='scatterDropdown', options=['Alcohol Consumption', 'Daily Smokers', 'Social Support'],
                                     value='Alcohol')
                    ], width=12, style={'color': '#00ff85'}),
                    dbc.Col([
                        dcc.Graph(
                            id='scatterChart',
                            figure=fig_scatterPlot
                        )
                    ], width=12),
                ],
                    style={
                        'border': '2px solid white',
                        'border-radius': '2px',
                        'border-width': 'thin'
                    }
                    , className='scatterPlotContainer'
                )
            ]
        ),

        # Line Charts Container

        html.Div(
            children=[
                dbc.Row([
                    dbc.Col([
                        "Select a Country:",
                        dcc.Dropdown(id='lineChartDropdown1', options=country_list, value=country_list[0])
                    ], width=6, className='lineChartDropdown'),

                    dbc.Col([
                        "Select a Lifestyle Factor to compare with:",
                        dcc.Dropdown(id='lineChartDropdown2', options=['Alcohol Consumption', 'Daily Smokers', 'Social Support'],
                                     value='Alcohol')
                    ], width=6, className='lineChartDropdown'),

                    dbc.Col([
                        dcc.Graph(
                            id='lineChart1',
                            figure=fig_lineChart1
                        )
                    ], width=6),

                    dbc.Col([
                        dcc.Graph(
                            id='lineChart2',
                            figure=fig_lineChart2
                        )
                    ], width=6)

                ],
                    style={
                        'border': '2px solid white',
                        'border-radius': '2px',
                        'border-width': 'thin'
                    }
                    , className='lineChartContainer'
                )
            ]
        )

    ])


#############################################################

# Callbacks area #

# Choropleth map click data

@app.callback(
    [
        Output(component_id='pie1', component_property='figure'),
        Output(component_id='pie2', component_property='figure'),
        Output(component_id='pie3', component_property='figure'),
        Output(component_id='pie4', component_property='figure'),
    ],
    Input(component_id='map', component_property='clickData')
)
def update_pies(click_data):
    if click_data is not None:

        # Update dataset for obesity pie chart
        filter_mask = obesity_sorted_by_value_df['LOCATION'] == click_data['points'][0]['location']
        new_obesity_sorted_by_value_filtered_country_df = obesity_sorted_by_value_df[filter_mask]
        new_obesity_value = new_obesity_sorted_by_value_filtered_country_df['Value'].to_string(index=False)
        new_obesity_value = float(new_obesity_value)

        new_obesity_percentage_df = pd.DataFrame({'names': ['progress', 'remaining'],
                                                  'values': [new_obesity_value / 100, (100 - new_obesity_value) / 100]})

        # Update dataset for alcohol pie chart
        filter_mask = alcohol_sorted_by_value_df['LOCATION'] == click_data['points'][0]['location']
        new_alcohol_sorted_by_value_filtered_country_df = alcohol_sorted_by_value_df[filter_mask]
        new_alcohol_value = new_alcohol_sorted_by_value_filtered_country_df['Value'].to_string(index=False)
        new_alcohol_value = float(new_alcohol_value)

        new_alcohol_percentage_df = pd.DataFrame({'names': ['progress', 'remaining'],
                                                  'values': [new_alcohol_value / 13, (13 - new_alcohol_value) / 13]})

        # Update dataset daily smoker pie chart
        filter_mask = smoke_sorted_by_value_df['LOCATION'] == click_data['points'][0]['location']
        new_smoke_sorted_by_value_filtered_country_df = smoke_sorted_by_value_df[filter_mask]
        new_smoke_value = new_smoke_sorted_by_value_filtered_country_df['Value'].to_string(index=False)
        new_smoke_value = float(new_smoke_value)

        new_smoke_percentage_df = pd.DataFrame({'names': ['progress', 'remaining'],
                                                'values': [new_smoke_value / 100, (100 - new_smoke_value) / 100]})

        # Update dataset for social support pie chart
        filter_mask = social_support_sorted_by_value_df['LOCATION'] == click_data['points'][0]['location']
        new_social_support_sorted_by_value_filtered_country_df = social_support_sorted_by_value_df[filter_mask]
        new_social_support_value = new_social_support_sorted_by_value_filtered_country_df['Value'].to_string(
            index=False)
        new_social_support_value = float(new_social_support_value)

        new_social_support_percentage_df = pd.DataFrame({'names': ['progress', 'remaining'],
                                                         'values': [new_social_support_value / 100,
                                                                    (100 - new_social_support_value) / 100]})

    else:

        # Remain 0 if the map data is not clicked for all the pie charts
        new_obesity_value = 0

        new_obesity_percentage_df = pd.DataFrame({'names': ['progress', 'remaining'],
                                                  'values': [0 / 100, (100 - 0) / 100]})

        new_alcohol_value = 0

        new_alcohol_percentage_df = pd.DataFrame({'names': ['progress', 'remaining'],
                                                  'values': [0 / 100, (100 - 0) / 100]})

        new_smoke_value = 0

        new_smoke_percentage_df = pd.DataFrame({'names': ['progress', 'remaining'],
                                                'values': [0 / 100, (100 - 0) / 100]})

        new_social_support_value = 0

        new_social_support_percentage_df = pd.DataFrame({'names': ['progress', 'remaining'],
                                                         'values': [0 / 100, (100 - 0) / 100]})

    # Update obesity pie chart
    fig_pie_obesity = px.pie(new_obesity_percentage_df
                             , values='values', names='names'
                             , hole=0.5, height=225.5
                             , color='names'
                             , color_discrete_map={'progress': '#00ff85',
                                                   'remaining': 'grey'})

    fig_pie_obesity = fig_pie_obesity.update_layout(title_text='Obese (population %)'
                                                    , margin=dict(t=50, b=50, l=50, r=50)
                                                    , paper_bgcolor='black'
                                                    , font_color='#00ff85'
                                                    , hovermode=False).update_traces(sort=False, textinfo='none')

    fig_pie_obesity = fig_pie_obesity.update(layout_showlegend=False).add_annotation(x=0.5, y=0.5
                                                                                     , text=str(int(new_obesity_value)) + '%'
                                                                                     , font=dict(size=20,
                                                                                                 family='Verdana',
                                                                                                 color='#00ff85')
                                                                                     , showarrow=False)

    # Update alcohol pie chart
    fig_pie_alcohol = px.pie(new_alcohol_percentage_df
                             , values='values', names='names'
                             , hole=0.5, height=225.5
                             , color='names'
                             , color_discrete_map={'progress': '#00ff85',
                                                   'remaining': 'grey'})

    fig_pie_alcohol = fig_pie_alcohol.update_layout(title_text='Alcohol Consumption (lcpd)'
                                                    , margin=dict(t=50, b=50, l=50, r=50)
                                                    , paper_bgcolor='black'
                                                    , font_color='#00ff85'
                                                    , hovermode=False).update_traces(sort=False, textinfo='none')

    fig_pie_alcohol = fig_pie_alcohol.update(layout_showlegend=False).add_annotation(x=0.5, y=0.5
                                                                                     , text=str(int(new_alcohol_value))
                                                                                     , font=dict(size=20,
                                                                                                 family='Verdana',
                                                                                                 color='#00ff85')
                                                                                     , showarrow=False)

    # Update daily smoke pie chart
    fig_pie_smoke = px.pie(new_smoke_percentage_df
                           , values='values', names='names'
                           , hole=0.5, height=225.5
                           , color='names'
                           , color_discrete_map={'progress': '#00ff85',
                                                 'remaining': 'grey'})

    fig_pie_smoke = fig_pie_smoke.update_layout(title_text='Daily Smokers (population %)'
                                                , margin=dict(t=50, b=50, l=50, r=50)
                                                , paper_bgcolor='black'
                                                , font_color='#00ff85'
                                                , hovermode=False).update_traces(sort=False, textinfo='none')

    fig_pie_smoke = fig_pie_smoke.update(layout_showlegend=False).add_annotation(x=0.5, y=0.5
                                                                                 , text=str(int(new_smoke_value)) + '%'
                                                                                 , font=dict(size=20, family='Verdana',
                                                                                             color='#00ff85')
                                                                                 , showarrow=False)

    # Update social support pie chart
    fig_pie_social_support = px.pie(new_social_support_percentage_df
                                    , values='values', names='names'
                                    , hole=0.5, height=225.5
                                    , color='names'
                                    , color_discrete_map={'progress': '#00ff85',
                                                          'remaining': 'grey'})

    fig_pie_social_support = fig_pie_social_support.update_layout(title_text='Social Support (population %)'
                                                                  , margin=dict(t=50, b=50, l=50, r=50)
                                                                  , paper_bgcolor='black'
                                                                  , font_color='#00ff85'
                                                                  , hovermode=False).update_traces(sort=False,
                                                                                                   textinfo='none')

    fig_pie_social_support = fig_pie_social_support.update(layout_showlegend=False).add_annotation(x=0.5, y=0.5
                                                                                                   , text=str(int(new_social_support_value)) + '%'
                                                                                                   , font=dict(size=20,
                                                                                                               family='Verdana',
                                                                                                               color='#00ff85')
                                                                                                   , showarrow=False)

    return fig_pie_obesity, fig_pie_alcohol, fig_pie_smoke, fig_pie_social_support


# Scatter plot

@callback(
    Output(component_id='scatterChart', component_property='figure'),
    Input(component_id='scatterDropdown', component_property='value'),
    prevent_initial_call=True
)
def update_scatter_plot(chosen_data):

    # Update scatter plot according to what user pick from the dropdown
    if chosen_data == 'Alcohol Consumption':

        new_merged_df = pd.merge(obesity_sorted_by_value_df, alcohol_sorted_by_value_df, on='LOCATION')
        new_merged_df = new_merged_df[['LOCATION', 'Value_x', 'Value_y']]
        new_merged_df = new_merged_df.rename(columns={'Value_x': 'Obesity_value', 'Value_y': 'Alcohol_value'})

        fig_scatter_plot = px.scatter(new_merged_df
                                      , x='Alcohol_value', y='Obesity_value'
                                      , size='Obesity_value', title='Obese (% of population aged 15+) vs Alcohol Consumption (Litre/Capita, aged 15+)'
                                      , color='Alcohol_value'
                                      , color_continuous_scale=['white', '#62fbd3', '#00ff85']
                                      , color_discrete_sequence=['#00ff85']
                                      , labels={
                                            "Alcohol_value": "Alcohol Consumption",
                                            "Obesity_value": "Obesity"
                                        })

        fig_scatter_plot = fig_scatter_plot.update_layout(
            plot_bgcolor='black'
            , paper_bgcolor='black'
            , font_color='#00ff85')

    elif chosen_data == 'Daily Smokers':

        new_merged_df = pd.merge(obesity_sorted_by_value_df, smoke_sorted_by_value_df, on='LOCATION')
        new_merged_df = new_merged_df[['LOCATION', 'Value_x', 'Value_y']]
        new_merged_df = new_merged_df.rename(columns={'Value_x': 'Obesity_value', 'Value_y': 'Smoke_value'})

        fig_scatter_plot = px.scatter(new_merged_df
                                      , x='Smoke_value', y='Obesity_value'
                                      , size='Obesity_value'
                                      , title='Obese (% of population aged 15+) vs Daily Smokers (% of population aged 15+)'
                                      , color='Smoke_value'
                                      , color_continuous_scale=['white', '#62fbd3', '#00ff85']
                                      , color_discrete_sequence=['#00ff85']
                                      , labels={
                                            "Smoke_value": "Daily Smokers",
                                            "Obesity_value": "Obesity"
                                        })

        fig_scatter_plot = fig_scatter_plot.update_layout(
            plot_bgcolor='black'
            , paper_bgcolor='black'
            , font_color='#00ff85')

    else:

        new_merged_df = pd.merge(obesity_sorted_by_value_df, social_support_sorted_by_value_df, on='LOCATION')
        new_merged_df = new_merged_df[['LOCATION', 'Value_x', 'Value_y']]
        new_merged_df = new_merged_df.rename(columns={'Value_x': 'Obesity_value', 'Value_y': 'Social_support_value'})

        fig_scatter_plot = px.scatter(new_merged_df
                                      , x='Social_support_value', y='Obesity_value'
                                      , size='Obesity_value'
                                      , title='Obese (% of population aged 15+) vs Social Support (% of population aged 15+)'
                                      , color='Social_support_value'
                                      , color_continuous_scale=['white', '#62fbd3', '#00ff85']
                                      , color_discrete_sequence=['#00ff85']
                                      , labels={
                                            "Social_support_value": "Social Support",
                                            "Obesity_value": "Obesity"
                                        })

        fig_scatter_plot = fig_scatter_plot.update_layout(
            plot_bgcolor='black'
            , paper_bgcolor='black'
            , font_color='#00ff85')

    return fig_scatter_plot


# Line Chart

@callback(
    [
        Output(component_id='lineChart1', component_property='figure'),
        Output(component_id='lineChart2', component_property='figure')
    ],
    [
        Input(component_id='lineChartDropdown1', component_property='value'),
        Input(component_id='lineChartDropdown2', component_property='value')
    ]

)
def update_scatter_plot(chosen_country, chosen_life_factor):
    new_obesity_full_df = pd.read_csv("obesity_by_country_full.csv")
    new_obesity_mean_full_df = new_obesity_full_df.groupby(['LOCATION', 'TIME'])['Value'].mean().reset_index()
    filter_mask = new_obesity_mean_full_df['LOCATION'] == chosen_country
    new_obesity_mean_full_filtered_df = new_obesity_mean_full_df[filter_mask]

    fig_line_chart_1 = px.line(new_obesity_mean_full_filtered_df
                               , x="TIME", y="Value"
                               , title='Obese (% of population aged 15+)'
                               , markers=True
                               , labels={
                                     "TIME": "Year",
                                     "Value": "Population (%)"
                                 })

    fig_line_chart_1 = fig_line_chart_1.update_layout(
        plot_bgcolor='black'
        , paper_bgcolor='black'
        , font_color='#00ff85')

    fig_line_chart_1 = fig_line_chart_1.update_traces(
        line_color='#00ff85')

    # Update the dataset and line chart based on which value picked from dropdown
    if chosen_life_factor == 'Alcohol Consumption':

        new_alcohol_full_df = pd.read_csv("alcohol_by_country_full.csv")
        new_alcohol_mean_full_df = new_alcohol_full_df.groupby(['LOCATION', 'TIME'])['Value'].mean().reset_index()
        filter_mask = new_alcohol_mean_full_df['LOCATION'] == chosen_country
        new_alcohol_mean_full_filtered_df = new_alcohol_mean_full_df[filter_mask]

        fig_line_chart_2 = px.line(new_alcohol_mean_full_filtered_df
                                   , x="TIME", y="Value"
                                   , title='Alcohol Consumption (lcpd, aged 15+)'
                                   , markers=True
                                   , labels={
                                         "TIME": "Year",
                                         "Value": "Litre/Capita"
                                      })

        fig_line_chart_2 = fig_line_chart_2.update_layout(
            plot_bgcolor='black'
            , paper_bgcolor='black'
            , font_color='#00ff85')

        fig_line_chart_2 = fig_line_chart_2.update_traces(
            line_color='red')

    elif chosen_life_factor == 'Daily Smokers':

        smoke_full_df = pd.read_csv("smoke_by_country_full.csv")
        filter_mask = smoke_full_df['SUBJECT'] == 'TOT'
        smoke_full_df_filtered_by_subject = smoke_full_df[filter_mask]
        smoke_mean_full_df = smoke_full_df_filtered_by_subject.groupby(['LOCATION', 'TIME'])[
            'Value'].mean().reset_index()
        filter_mask = smoke_mean_full_df['LOCATION'] == chosen_country
        smoke_mean_full_filtered_by_country_df = smoke_mean_full_df[filter_mask]

        fig_line_chart_2 = px.line(smoke_mean_full_filtered_by_country_df
                                   , x="TIME", y="Value"
                                   , title='Daily Smokers (% of population aged 15+)'
                                   , markers=True
                                   , labels={
                                             "TIME": "Year",
                                             "Value": "Population (%)"
                                      })

        fig_line_chart_2 = fig_line_chart_2.update_layout(
            plot_bgcolor='black'
            , paper_bgcolor='black'
            , font_color='#00ff85')

        fig_line_chart_2 = fig_line_chart_2.update_traces(
            line_color='red')

    else:

        social_support_full_df = pd.read_csv("socialsupport_by_country_full.csv")
        filter_mask = social_support_full_df['SUBJECT'] == 'TOT'
        social_support_full_df_filtered_by_subject = social_support_full_df[filter_mask]
        social_support_mean_full_df = social_support_full_df_filtered_by_subject.groupby(['LOCATION', 'TIME'])[
            'Value'].mean().reset_index()
        filter_mask = social_support_mean_full_df['LOCATION'] == chosen_country
        social_support_mean_full_filtered_by_country_df = social_support_mean_full_df[filter_mask]

        fig_line_chart_2 = px.line(social_support_mean_full_filtered_by_country_df
                                   , x="TIME", y="Value"
                                   , title='Social Support (% of population aged 15+)'
                                   , markers=True
                                   , labels={
                                         "TIME": "Year",
                                         "Value": "Population (%)"
                                     })

        fig_line_chart_2 = fig_line_chart_2.update_layout(
            plot_bgcolor='black'
            , paper_bgcolor='black'
            , font_color='#00ff85')

        fig_line_chart_2 = fig_line_chart_2.update_traces(
            line_color='red')

    return fig_line_chart_1, fig_line_chart_2


if __name__ == '__main__':
    app.run(port=8005)
