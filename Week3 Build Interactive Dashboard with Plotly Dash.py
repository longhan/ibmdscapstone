# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create site names dict options
site_names = [{'label':'All Sites', 'value':'ALL'}]
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_df = launch_sites_df[['Launch Site', 'Launch Site']]
launch_sites_df.columns = ['label', 'value']
site_names = site_names + launch_sites_df.to_dict('records')
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=site_names,
                                            value = 'ALL',
                                            placeholder="Select a launch site",
                                            searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'), Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = go.Figure(data=[go.Pie(values=filtered_df['class'],
            labels =filtered_df['Launch Site'],
            title = 'Total Success Launches By Sites')])
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        entered_site_df = filtered_df.groupby('class')['class'].count()
        fig = go.Figure(data=[go.Pie(values=entered_site_df,
            labels =["0","1"],
            title = 'Total Success Launches By Sites' + entered_site)])
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id="payload-slider", component_property="value"))
def get_payload_chart(selected_site, selected_payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
        low, high = selected_payload_range
        mask = (filtered_df['Payload Mass (kg)'] > low) & (filtered_df['Payload Mass (kg)'] < high)
        fig = px.scatter(filtered_df[mask], x="Payload Mass (kg)", y="class", color="Booster Version Category", title='Correlation between Payload and Success for all Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==selected_site]
        low, high = selected_payload_range
        mask = (filtered_df['Payload Mass (kg)'] > low) & (filtered_df['Payload Mass (kg)'] < high)
        fig = px.scatter(filtered_df[mask], x="Payload Mass (kg)", y="class", color="Booster Version Category", title='Correlation between Payload and Success for ' + selected_site)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
