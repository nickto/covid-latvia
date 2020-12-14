import streamlit as st
import pandas as pd
import yaml
import math
import logging
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter

configs = yaml.safe_load(open("configs.yaml", "r"))

# Preprocess population
population = pd.read_csv(configs["data"]["population"]["processed"]["path"])
population = population.set_index("name")
population_latvia = population.loc["VISA LATVIJA", "total"]

# Preprocess cases
cases = pd.read_csv(configs["data"]["cases"]["processed"]["path"])
cases.loc[:, "date"] = cases.loc[:, "date"].apply(lambda d: d[:-1])
cases.loc[:, "date"] = pd.to_datetime(cases.loc[:, "date"])
cases = cases.sort_values("date")
cases = cases.set_index("date")
cases = cases.asfreq("D")
cases.loc[:, "cumsum_14_days"] = cases.loc[:, "positive"].rolling(14).sum()
cases.loc[cases.loc[:, "cumsum_14_days"].isna(),
          "cumsum_14_days"] = cases.loc[:, "positive"].cumsum()
cases = cases.reset_index()
cases.loc[:, "date"] = cases.loc[:, "date"].apply(lambda d: d.date())
cases.loc[:, "cumsum_14_days_per_100K"] = cases.loc[:, "cumsum_14_days"] * (
    1e5 / population_latvia)

def plot_ts(x, y):
    p = figure(plot_width=700,
            plot_height=400,
            tools="pan,wheel_zoom,reset",
            active_drag="pan",
            active_scroll="wheel_zoom")
    p.xaxis.formatter = DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %Y"],
    )
    p.xaxis.major_label_orientation = math.pi / 6
    p.line(x, y)
    return p

st.title("COVID-19 Latvia")
st.subheader("14-day cumulative cases per 100,000 inhabitants")
p = plot_ts(cases.date, cases.cumsum_14_days_per_100K)
st.bokeh_chart(p)

st.subheader("Daily confirmed cases")
p = plot_ts(cases.date, cases.positive)
st.bokeh_chart(p)

st.subheader("Daily tests")
p = plot_ts(cases.date, cases.tests)
st.bokeh_chart(p)

st.subheader("14-day cumulative cases")
p = plot_ts(cases.date, cases.cumsum_14_days)
st.bokeh_chart(p)
