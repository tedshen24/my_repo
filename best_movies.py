from dash.dependencies import Input, Output
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px

data = pd.read_csv('all-in-one.csv')

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=stylesheet)

HORIZONTAL_STYLE = {'display': 'inline-block', 'vertical-align': 'top', 'margin': '10px'}

year_array = []
genre_array = []

for item in set(data['year']):
    year_array.append({"label": str(item), "value": item})

for item in set(data['genre1']) | set(data['genre2']) | set(data['genre3']):
    if isinstance(item, str):
        genre_array.append({"label": str(item), "value": item})

app.layout = html.Div([
    html.H1('Best movies!',
            style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.H4('Choose filter type'),
            dcc.RadioItems(
                options=[
                    {'label': 'Name Search', 'value': 1},
                    {'label': 'Fuzzy Search', 'value': 2},
                    {'label': 'Filter Search', 'value': 3},
                ],
                value=1,
                id='show_table',
            )
        ], style=HORIZONTAL_STYLE),
        html.Div([
            html.H4("Input search keyword:"),
            dcc.Input(placeholder='eg: Black Panther', value='', type='text', id='keyword'),
        ], style=HORIZONTAL_STYLE, id='filter1', ),
        html.Div([
            html.H4("Preference Filter"),
            html.Div([
                dcc.Checklist(options=[{"label": "Year", "value": "enable"}, ], id='enable_year', ),
                dcc.Dropdown(options=year_array, id='year'),
            ]),
            html.Div([
                dcc.Checklist(options=[{"label": "Genre", "value": "enable"}], id='enable_genre', ),
                dcc.Dropdown(options=genre_array, id='genre'),
            ]),
            html.Div([
                dcc.Checklist(options=[{"label": "RunningTime", "value": "enable"}], id='enable_running_time', ),
                dcc.Dropdown(options=[
                    {'label': '0-60', 'value': 0},
                    {'label': '60-90', 'value': 1},
                    {'label': '90-120', 'value': 2},
                    {'label': '120+', 'value': 3}, ],
                    id='running_time'),
            ]),
        ], style=HORIZONTAL_STYLE, id='filter2', ),
        html.Div([dcc.Graph(id='fig_pie')],
                 style=HORIZONTAL_STYLE, ),
        html.Div([html.H4("Query result:")]),
        html.Div([dash_table.DataTable(
            id='query_result',
            columns=[{"name": i, "id": i} for i in data.columns],
            page_size=25,
            page_count=0,
            style_cell={'textAlign': 'left'},
        )]),

    ]),
    html.Div(id='table_div')
])


@app.callback(
    Output('filter1', 'style'),
    [Input('show_table', 'value')])
def toggle_container(toggle_value):
    if toggle_value != 3:
        return HORIZONTAL_STYLE
    else:
        return {'display': 'none'}


@app.callback(
    Output('filter2', 'style'),
    [Input('show_table', 'value')])
def toggle_container2(toggle_value):
    if toggle_value == 3:
        return HORIZONTAL_STYLE
    else:
        return {'display': 'none'}


def search_inner(show_table, keyword,
                 year, genre, running_time,
                 enable_year, enable_genre, enable_running_time, ):
    if show_table == 1:
        if keyword is None or keyword == "":
            return data
        else:
            part1 = data['title'] == keyword
            part2 = data['actors'].fillna("").str.split(',').map(lambda x: keyword in x)
            part3 = data['screenwriters'].fillna("").str.split(',').map(lambda x: keyword in x)
            part4 = data['directors'].fillna("").str.split(',').map(lambda x: keyword in x)
            part5 = data['producers'].fillna("").str.split(',').map(lambda x: keyword in x)
            return data[part1 | part2 | part3 | part4 | part5]
    elif show_table == 2:
        if keyword is None or keyword == "":
            return data
        else:
            part1 = data['title'].str.contains(keyword)
            part2 = data['actors'].str.contains(keyword)
            part3 = data['screenwriters'].str.contains(keyword)
            part4 = data['directors'].str.contains(keyword)
            part5 = data['producers'].str.contains(keyword)
            return data[part1 | part2 | part3 | part4 | part5]
    else:
        if enable_year is None and enable_genre is None and enable_running_time is None:
            return data
        else:
            ret_data = data
            if enable_year and year is not None:
                ret_data = ret_data[ret_data.year == int(year)]
            if enable_genre and genre is not None:
                part1 = ret_data.genre1 == genre
                part2 = ret_data.genre2 == genre
                part3 = ret_data.genre3 == genre
                ret_data = ret_data[part1 | part2 | part3]
            if enable_running_time and running_time is not None:
                ret_data['running_time'] = ret_data['running_time'].fillna(-1)
                start_end_pairs = ((0, 60), (60, 90), (90, 120), (120, 999))
                _start, _end = start_end_pairs[running_time]
                ret_data = ret_data[(ret_data.running_time > _start) & (ret_data.running_time < _end)]
            return ret_data


@app.callback(
    Output(component_id='fig_pie', component_property='figure'),
    Input('show_table', 'value'),
    Input('keyword', 'value'),
    Input('year', 'value'),
    Input('genre', 'value'),
    Input('running_time', 'value'),
    Input('enable_year', 'value'),
    Input('enable_genre', 'value'),
    Input('enable_running_time', 'value'),
)
def update_pie(show_table, keyword,
               year, genre, running_time,
               enable_year, enable_genre, enable_running_time, ):
    return to_fig(search_inner(show_table, keyword,
                               year, genre, running_time,
                               enable_year, enable_genre, enable_running_time, ))


@app.callback(
    Output(component_id='query_result', component_property='data'),
    Input('show_table', 'value'),
    Input('keyword', 'value'),
    Input('year', 'value'),
    Input('genre', 'value'),
    Input('running_time', 'value'),
    Input('enable_year', 'value'),
    Input('enable_genre', 'value'),
    Input('enable_running_time', 'value'),
)
def update_table(show_table, keyword,
                 year, genre, running_time,
                 enable_year, enable_genre, enable_running_time, ):
    return search_inner(show_table, keyword,
                        year, genre, running_time,
                        enable_year, enable_genre, enable_running_time, ).to_dict('records')


def to_fig(df):
    _tmp = df.groupby("genre1")
    _tmp = _tmp['genre1'].count().to_frame()
    fig = px.pie(_tmp, values=_tmp.genre1, names=_tmp.index)
    return fig


server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
