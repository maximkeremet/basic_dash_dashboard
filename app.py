# base imports
import pandas as pd
import numpy as np
from datetime import datetime as dt
from typing import List, Union

# dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# viz imports
from plotly import graph_objs as go
import plotly.express as px
from plotly.graph_objs import *

PLOTLY_THEME = 'simple_white'
STYLE = [dbc.themes.FLATLY]

app = dash.Dash('super-simple-app', external_stylesheets=STYLE)
server = app.server

df = pd.read_csv('datasets_supermarket_sales.csv')

columns_2_select = ['Date', 'City', 'Gender', 'Quantity', 'Product line', 'Tax 5%', 'Total']
selection = df[columns_2_select]
selection.columns = selection.columns.str.lower()
selection = selection.rename(columns={'product line': 'product_line'})

selection['year'] = selection['date'].str.split('/').str[2]
selection['month'] = selection['date'].str.split('/').str[0]

selection['date'] = selection['date'].str.split('/').str[1]+'-'+selection['date'].str.split('/').str[0]+'-'+selection['date'].str.split('/').str[2]
selection['date'] = pd.to_datetime(selection['date'], format='%d-%m-%Y')

date = selection['month'].unique()
cities = selection['city'].unique()
genders = selection['gender'].unique()
products = selection['product_line'].unique()

print(selection.head())

# components
controls = dbc.Card(
    [
        dbc.Row([
            dbc.Col(dbc.FormGroup(
            [
                dbc.Label("City:"),
                dcc.Dropdown(
                    id="city-selector",
                    options=[{"label": x, "value": x} for x in cities],
                    value="", multi=True
                )
            ]
            )),
            dbc.Col(dbc.FormGroup(
                [
                    dbc.Label("Gender:"),
                    dcc.Dropdown(
                        id="gender-selector",
                        options=[{"label": x, "value": x} for x in genders],
                        value="All"
                    )
                ]
            )),
            dbc.Col(dbc.FormGroup(
                [
                    dbc.Label("Product:"),
                    dcc.Dropdown(
                        id="product-selector",
                        options=[{"label": x, "value": x} for x in products],
                        value="All"
                    )
                ]
            )),
        ], align='center')
    ],
    body=True
)

sales_graph = dcc.Graph(id='sales-graph')
qty_graph = dcc.Graph(id='qty-graph')

# general layout
app.layout = dbc.Container(
    [
     html.H1("Basic sales dashboard"),
     html.Hr(),
     dbc.Row([dbc.Col(controls, width=6)]),
     dbc.Row([dbc.Col(sales_graph, width=6),
              dbc.Col(qty_graph, width=6)], align="center")
    ], fluid=True
)


@app.callback(Output(component_id='sales-graph', component_property='figure'),
              [Input(component_id='city-selector', component_property='value'),
               Input(component_id='gender-selector', component_property='value'),
               Input(component_id='product-selector', component_property='value')])
def update_sales_graph(cities: List, gender: List, product: List):

    global selection
    df = pd.DataFrame(selection)

    if len(cities) == 0:
        pass
    elif len(cities) == 1:
        df = df[df['city'] == cities[0]]
    elif len(cities) > 1:
        df = df[df['city'].isin(cities)]
    if gender == 'All' or gender is None:
        pass
    elif gender != 'All':
        df = df[df['gender'] == gender]
    if product == 'All' or product is None:
        pass
    elif product != 'All':
        df = df[df['product_line'] == product]

    sales_groupped = df.groupby('date')['total'].sum().reset_index()
    sales_groupped = sales_groupped.sort_values('date')
    sales_groupped['date'] = sales_groupped['date'].astype(str)

    sales_groupped['tax'] = sales_groupped['total'] * 0.05

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=sales_groupped['date'].values,
                             y=sales_groupped['total'].values,
                             fill=None, mode='lines+markers',
                             name='sales', line={'color': 'green'}))

    fig.add_trace(go.Scatter(x=sales_groupped['date'].values,
                             y=sales_groupped['tax'].values,
                             fill=None, mode='lines+markers',
                             name='tax', line={'color': 'tomato'}))

    fig.update_traces(opacity=0.75)

    fig.update_layout(template=PLOTLY_THEME, title_text="Daily sales, usd", xaxis_title=u"date",
                      yaxis_title="usd.")
    return fig


@app.callback(Output(component_id='qty-graph', component_property='figure'),
              [Input(component_id='city-selector', component_property='value'),
               Input(component_id='gender-selector', component_property='value'),
               Input(component_id='product-selector', component_property='value')])
def update_qty_graph( cities: List, gender: List, product: List):

    global selection
    df = pd.DataFrame(selection)

    if len(cities) == 0:
        pass
    elif len(cities) == 1:
        df = df[df['city'] == cities[0]]
    elif len(cities) > 1:
        df = df[df['city'].isin(cities)]
    if gender == 'All' or gender is None:
        pass
    elif gender != 'All':
        df = df[df['gender'] == gender]
    if product == 'All' or product is None:
        pass
    elif product != 'All':
        df = df[df['product_line'] == product]

    qty_groupped = df.groupby('date')['quantity'].sum().reset_index()
    qty_groupped = qty_groupped.sort_values('date')
    qty_groupped['date'] = qty_groupped['date'].astype(str)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=qty_groupped['date'].values,
                             y=qty_groupped['quantity'].values, fill=None,
                             mode='lines+markers', name='quantity, pcs',
                             line={'color': 'indigo'}))

    fig.update_traces(opacity=0.75)

    fig.update_layout(template=PLOTLY_THEME, title_text="Daily sales, qty", xaxis_title=u"date",
                      yaxis_title="units")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1', port=8081)