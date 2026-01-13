import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load data
data = pd.read_csv('historical_automobile_sales.csv')

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Styles
SIDEBAR_STYLE = {
    'padding': '20px',
    'backgroundColor': '#f8f9fa',
    'borderRadius': '10px',
    'margin-bottom': '20px',
    'boxShadow': '2px 2px 5px rgba(0,0,0,0.1)'
}

# Layout
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f0f2f5'}, children=[
    
    # Title
    html.H1("Automobile Sales Statistics Dashboard",
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
    
    # Filter Section
    html.Div(style=SIDEBAR_STYLE, children=[
        html.Div([
            html.Label("Select Statistics Report:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='dropdown-statistics',
                options=[
                    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
                ],
                placeholder='Select a report type',
                style={'width': '100%'}
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label("Select Year:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='select-year',
                options=[{'label': i, 'value': i} for i in range(1980, 2024)],
                placeholder='Select a year',
                disabled=True
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ]),
    
    # Output Display
    html.Div(id='output-container', style={'marginTop': '20px'})
])

# CALLBACK 1 — Enable/Disable Year Dropdown
@app.callback(
    [Output('select-year', 'disabled'),
     Output('select-year', 'value')],
    Input('dropdown-statistics', 'value')
)
def toggle_year_dropdown(selected_stat):
    if selected_stat == 'Yearly Statistics':
        return False, None # Enable and clear value
    return True, None # Disable and clear value

# CALLBACK 2 — Generate Plots
@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'),
     Input('select-year', 'value')]
)
def update_output(selected_stat, input_year):
    if not selected_stat:
        return html.Div("Please select a statistic type to begin analysis.", 
                        style={'textAlign': 'center', 'marginTop': '100px', 'fontSize': '20px', 'color': '#7f8c8d'})

    # --- RECESSION STATISTICS ---
    if selected_stat == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]
        
        # 1. Sales over time
        sales_line = px.line(recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index(), 
                            x='Year', y='Automobile_Sales', title="Avg Sales Trend (Recession)")
        
        # 2. Vehicle Type Bar
        v_type_bar = px.bar(recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index(), 
                           x='Vehicle_Type', y='Automobile_Sales', title="Avg Sales by Vehicle Type")
        
        # 3. Ad Spend Pie
        ad_pie = px.pie(recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index(), 
                       values='Advertising_Expenditure', names='Vehicle_Type', title="Ad Spend Share")
        
        # 4. Unemployment Effect
        unemp_bar = px.bar(recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index(), 
                          x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type', title='Unemployment vs Sales')

        plots = [sales_line, v_type_bar, ad_pie, unemp_bar]

    # --- YEARLY STATISTICS ---
    elif selected_stat == 'Yearly Statistics':
        if not input_year:
            return html.Div("Please select a year to view yearly statistics.")
        
        yearly_data = data[data['Year'] == input_year]
        
        # 1. Overall Trend (All years)
        total_trend = px.line(data.groupby('Year')['Automobile_Sales'].mean().reset_index(), 
                             x='Year', y='Automobile_Sales', title='Annual Sales Trend (1980-2023)')
        
        # 2. Monthly Trend for selected year
        month_trend = px.line(yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index(), 
                             x='Month', y='Automobile_Sales', title=f'Monthly Sales in {input_year}')
        
        # 3. Avg Sales by Type
        type_bar = px.bar(yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index(), 
                         x='Vehicle_Type', y='Automobile_Sales', title=f'Avg Sales by Type ({input_year})')
        
        # 4. Ad Spend Pie
        ad_pie_year = px.pie(yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index(), 
                            values='Advertising_Expenditure', names='Vehicle_Type', title=f'Ad Spend by Type ({input_year})')

        plots = [total_trend, month_trend, type_bar, ad_pie_year]

    # Return as a 2x2 Grid
    return html.Div([
        html.Div([
            html.Div(dcc.Graph(figure=plots[0]), style={'width': '50%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=plots[1]), style={'width': '50%', 'display': 'inline-block'}),
        ], style={'display': 'flex'}),
        html.Div([
            html.Div(dcc.Graph(figure=plots[2]), style={'width': '50%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=plots[3]), style={'width': '50%', 'display': 'inline-block'}),
        ], style={'display': 'flex'})
    ], style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '10px'})

if __name__ == '__main__':
    app.run_server(debug=True)
