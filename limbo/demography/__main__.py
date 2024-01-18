import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input
from plotly.subplots import make_subplots

from limbo.demography.demography_model import simulate_with_fertility_rate


def main():
    app = Dash(__name__)

    app.layout = html.Div([
        html.H1(children='Demography simulator', style={'textAlign': 'center', 'fontFamily': 'Helvetica'}),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Slider(1, 2, id='slider-fertility-rate', value=1.2),
                        dcc.Graph(id='sum_pops_graph', style={'height': '80vh'}),
                    ],
                    style={'flex': '50%', 'padding': '10px'}
                ),
                html.Div(
                    children=[
                        dcc.Slider(0, 50, id='slider-duration-years', value=0),
                        dcc.Graph(id='populations_graph', style={'height': '80vh'}),
                    ],
                    style={'flex': '50%', 'padding': '10px'}
                ),
            ],
            style={'display': 'flex', 'flexDirection': 'row'}
        )
    ])

    app.run(debug=True)


@callback(
    Output('populations_graph', 'figure'),
    Input('slider-fertility-rate', 'value'),
    Input('slider-duration-years', 'value')
)
def update_population_graph(value, value2):
    years, pops, sum_pops, ratios_vec, immigrations_vec, pension_ages_vec = simulate_with_fertility_rate(
        float(value))

    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    value2 = int(value2)

    fig.add_trace(
        go.Line(x=list(range(0, 100)), y=pops[value2], xaxis="x", yaxis="y", name=f"Year {value2 + 2024}"), row=1,
        col=1)

    legend = dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )

    fig.update_layout(legend=legend)

    return fig


@callback(
    Output('sum_pops_graph', 'figure'),
    Input('slider-fertility-rate', 'value')
)
def update_graphs(value):
    years, pops, sum_pops, ratios_vec, immigrations_vec, pension_ages_vec = simulate_with_fertility_rate(
        float(value))

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    sum_pops_line = go.Line(x=years, y=sum_pops, xaxis="x", yaxis="y", name="Population")
    ratios_line = go.Line(x=years, y=ratios_vec, xaxis="x1", yaxis="y1", name="Ratio worker per retired")
    pension_ages_line = go.Line(x=years, y=pension_ages_vec, xaxis="x2", yaxis="y2", name="Legal retirement age")
    immigrations_line = go.Line(x=years, y=immigrations_vec, xaxis="x3", yaxis="y3", name="Immigration")

    legend = dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )

    fig.update_layout(legend=legend)

    fig.add_trace(sum_pops_line, row=1, col=1)
    fig.add_trace(ratios_line, row=2, col=1)
    fig.add_trace(pension_ages_line, row=3, col=1)
    fig.add_trace(immigrations_line, row=4, col=1)

    return fig


if __name__ == "__main__":
    main()
