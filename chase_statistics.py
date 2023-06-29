from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

def run_app(session):
    def generate_table(id, default_df, size):
        return dash_table.DataTable(
            id=id,
            data=default_df.to_dict('records'),
            columns=[{"name": i, 'id': i} for i in default_df.columns],
            page_size=size,
            filter_action="native",
            filter_options={"placeholder_text": "Filter column..."},
            style_cell={'textAlign': 'left'},
            style_filter={
                'backgroundColor': 'LightSteelBlue',
            },
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            },
            style_data={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
        )
    app = Dash(__name__)
    df = pd.read_sql_table("transactions", session.bind)

    month_grouped_df = df.groupby([pd.Grouper(key='date', freq='M'), 'type'], as_index=False).amount.sum()
    year_grouped_df = df.groupby([pd.Grouper(key='date', freq='Y'), 'type'], as_index=False).amount.sum()
    month_grouped_df.sort_values(by=['date', 'type'], inplace=True, ascending=False)
    year_grouped_df.sort_values(by=['date', 'type'], inplace=True, ascending=False)
    all_years = list(set(month_grouped_df['date'].dt.year))
    df.sort_values(by=['date'], inplace=True, ascending=False)
    df.drop(columns=['id'], inplace=True)

    app.layout = html.Div(
        [
            html.H1(
                children='Chase Finance Interface',
                style = {
                    'textAlign' : 'center',
                    'backgroundColor':'gray',
                    'color':'white'
                }
            ),
            html.Hr(            
                style = {
                    'backgroundColor':'gray'
                }
            ),
            dcc.RadioItems(
                options=all_years + ['All'],
                value='All', 
                id='year-control',
                style = {
                    'color':'white',
                    'backgroundColor':'gray'
                }
            ),
            html.Hr(),
            dcc.Graph(id='spending-graph'),
            html.Br(),
            generate_table('all-table', df, 30),
            generate_table('month-table', month_grouped_df, 10),
            generate_table('year-table', year_grouped_df, 10)
        ],
        style={
            "backgroundColor": 'LightSteelBlue'
        },
    )

    @callback(
        Output('year-table', 'data'),
        Input('year-control', 'value')
    )
    def update_year_table(year_chosen):
        if year_chosen == 'All':
            year_chosen = all_years
        else:
            year_chosen = [year_chosen]
        df_copy = year_grouped_df[year_grouped_df['date'].dt.year.isin(year_chosen)].copy()
        df_copy['date'] = df_copy['date'].dt.to_period('Y').map(str)
        df_copy['amount'] = df_copy['amount'].round(2)
        
        return df_copy.to_dict('records')

    @callback(
        Output('month-table', 'data'),
        Input('year-control', 'value')
    )
    def update_month_table(year_chosen):
        if year_chosen == 'All':
            year_chosen = all_years
        else:
            year_chosen = [year_chosen]
        df_copy = month_grouped_df[month_grouped_df['date'].dt.year.isin(year_chosen)].copy()
        df_copy['date'] = df_copy['date'].dt.to_period('M').map(str)
        df_copy['amount'] = df_copy['amount'].round(2)
        
        return df_copy.to_dict('records')

    @callback(
        Output('all-table', 'data'),
        Input('year-control', 'value')
    )
    def update_all_table(year_chosen):
        if year_chosen == 'All':
            year_chosen = all_years
        else:
            year_chosen = [year_chosen]
        df_copy = df[df['date'].dt.year.isin(year_chosen)].copy()
        df_copy['date'] = df_copy['date'].dt.to_period('D').map(str)
        df_copy['amount'] = df_copy['amount'].round(2)
        
        return df_copy.to_dict('records')

    @callback(
        Output('spending-graph', 'figure'),
        Input('year-control', 'value')
    )
    def update_spending_graph(year_chosen):
        if year_chosen == 'All':
            year_chosen = all_years
        else:
            year_chosen = [year_chosen]
        spending_df = month_grouped_df[month_grouped_df['date'].dt.year.isin(year_chosen)].copy()
        spending_df['date'] = spending_df['date'].dt.to_period('M').map(str)
        spending_df['amount'] = spending_df['amount'].round(2)

        fig = px.line(
            spending_df,
            x="date",
            y="amount",
            color="type",
            title="Spending Per Month",
            text="amount",
            labels={"date" : "YYYY-MM", "amount" : "Amount in Dollars", "type" : "Transaction Type"}
        )
        fig.update_layout(
            autotypenumbers='convert types',
            height=800,
            xaxis_type='category',
            paper_bgcolor="black",
            plot_bgcolor='gray',
            font_color="white"
        )
        fig.update_xaxes(categoryorder='category ascending')

        return fig

    app.run_server(debug=True)
