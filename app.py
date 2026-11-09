import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

DATA_PATH = "data.csv"

df = pd.read_csv(DATA_PATH, parse_dates=["date"])

route_names = sorted(df["route"].unique())

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Пассажиропоток"),
    dcc.Dropdown(
        id="route-dropdown",
        options=[{"label": "Все маршруты", "value": "all"}] + [{"label": r, "value": r} for r in route_names],
        value="all"
    ),
    html.Div(id="kpi-passengers"),
    html.Div(id="kpi-delay"),
    dcc.Graph(id="line-chart"),
    dcc.Graph(id="bar-chart")
])

@app.callback(
    Output("kpi-passengers", "children"),
    Output("kpi-delay", "children"),
    Output("line-chart", "figure"),
    Output("bar-chart", "figure"),
    Input("route-dropdown", "value")
)
def update_dashboard(selected_route):
    if selected_route != "all":
        filtered = df[df["route"] == selected_route].copy()
    else:
        filtered = df.copy()

    passenger_total = filtered["passengers"].sum()
    delay_rate = (filtered["delayed_trips"].sum() / filtered["trips"].sum()) * 100

    daily = (
        filtered.groupby("date", as_index=False)["passengers"]
        .sum()
        .sort_values("date")
    )
    line = px.line(
        daily, x="date", y="passengers",
        title="Пассажиры по дням",
        labels={"date": "Дата", "passengers": "Пассажиры"},
        markers=True,
    )

    by_route = filtered.groupby("route", as_index=False)["passengers"].sum()
    bar = px.bar(
        by_route, x="route", y="passengers",
        title="Пассажиры по маршрутам",
        labels={"route": "Маршрут", "passengers": "Пассажиры"},
    )

    return (
        f"Всего пассажиров: {passenger_total}",
        f"Доля опозданий: {delay_rate:.1f}%",
        line,
        bar
    )

if __name__ == "__main__":
    app.run(debug=True)
