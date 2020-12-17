import streamlit as st
import pandas as pd
import yaml
import math
import logging
import datetime
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter


# Functions
def get_n_day_sum(source_col, target_col, df, n=14):
    df = df.copy()
    df.loc[:, target_col] = df.loc[:, source_col].rolling(n).sum()
    # Find indices because we subset by .iloc
    target_idx = df.columns.get_loc(target_col)
    source_idx = df.columns.get_loc(source_col)
    # Rewrite first n observations with regular cumsum, because rolling sum
    # leaves NAs in the first n - 1 places
    df.iloc[:n, target_idx] = df.iloc[:n, source_idx].expanding().sum()
    return df


def get_n_day_mean(source_col, target_col, df, n=14):
    df = df.copy()
    df.loc[:, target_col] = df.loc[:, source_col].rolling(n).mean()
    # Find indices because we subset by .iloc
    target_idx = df.columns.get_loc(target_col)
    source_idx = df.columns.get_loc(source_col)
    # Rewrite first n observations with regular cummean, because rolling mean
    # leaves NAs in the first n - 1 places
    df.iloc[:n, target_idx] = df.iloc[:n, source_idx].expanding().sum()
    return df


def plot_ts(x, y, plot_width=700, plot_height=400):
    if isinstance(x.iloc[-1], datetime.date):
        x = x.apply(lambda x: datetime.datetime.combine(
            x, datetime.datetime.min.time()))

    p = figure(
        plot_width=plot_width,
        plot_height=plot_height,
        tools="pan,wheel_zoom,reset",
        active_drag="pan",
        active_scroll="wheel_zoom",
        x_axis_type="datetime",
    )
    p.xaxis.formatter = DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %Y"],
    )
    p.xaxis.major_label_orientation = math.pi / 6
    p.line(x, y)
    return p


def plot_overview(x, y, show_last=90, plot_width=700, plot_height=200):
    if isinstance(x.iloc[-1], datetime.date):
        x = x.apply(lambda x: datetime.datetime.combine(
            x, datetime.datetime.min.time()))

    p = figure(plot_width=plot_width,
               plot_height=plot_height,
               tools="xpan,xwheel_zoom,reset",
               active_drag="xpan",
               active_scroll="xwheel_zoom",
               x_axis_type="datetime",
               x_range=(x.iloc[-show_last], x.iloc[-1]))
    p.xaxis.formatter = DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %Y"],
    )
    p.xaxis.major_label_orientation = math.pi / 6
    p.line(x, y)

    return p


# Read in configs
configs = yaml.safe_load(open("configs.yaml", "r"))

# Preprocess population
population = pd.read_csv(configs["data"]["population"]["processed"]["path"])
population = population.set_index("name")
population_latvia = population.loc["VISA LATVIJA", "total"]

# Read in cases
cases = pd.read_csv(configs["data"]["cases"]["processed"]["path"])
# Read in cases metadata
cases_meta = yaml.load(open(configs["data"]["cases"]["processed"]["path"] + ".meta.yaml", "r"))
# Remove trailing dot in dates, so it is parsable
cases.loc[:, "date"] = cases.loc[:, "date"].apply(lambda d: d[:-1])
# Convert string date to actual date
cases.loc[:, "date"] = pd.to_datetime(cases.loc[:, "date"])
# Fill in missing dates (if any)
cases = cases.sort_values("date")
cases = cases.set_index("date")
cases = cases.asfreq("D")
# Compute 14-day cumulative indicators
cases = get_n_day_sum("cases", "cases_14_days_sum", cases)
cases = get_n_day_sum("deaths", "deaths_14_days_sum", cases)
# Compute 14-day mean indicators
cases = get_n_day_mean("cases", "cases_14_days_mean", cases)
cases = get_n_day_mean("deaths", "deaths_14_days_mean", cases)
# Make date back as a column instead of index
cases = cases.reset_index()
cases.loc[:, "date"] = cases.loc[:, "date"].apply(lambda d: d.date())
# Compute per 100K indicators
cases.loc[:,
          "cases_14_days_sum_per_100K"] = cases.loc[:, "cases_14_days_sum"] * (
              1e5 / population_latvia)
cases.loc[:,
          "deaths_14_days_sum_per_100K"] = cases.loc[:,
                                                     "deaths_14_days_sum"] * (
                                                         1e5 /
                                                         population_latvia)

# Page layout
st.set_page_config(page_title="Latvia COVID-19", page_icon="🏥")
st.title("COVID-19 Latvia")
st.write("Data last updated on", pd.to_datetime(cases_meta["last_modified"]).strftime("%Y-%m-%d %H:%M"))

summarize_by_values = {
    "summary": "Summary",
    "daily": "Daily",
    "14d_mean": "14-day mean",
    "14d_sum": "14-day sum",
    "14d_sum_normalized": "14-day sum per 100K",
}

summarize_by = st.sidebar.selectbox(
    "Show",
    tuple(summarize_by_values.values()),
)

if summarize_by == summarize_by_values["summary"]:
    st.header("Summary")

    def get_summary_of(col, df):
        value = df.loc[:, col].iloc[-1]
        value_1d = df.loc[:, col].iloc[-2]
        value_7d = df.loc[:, col].iloc[-8]
        direction_1d = "⬆️" if value > value_1d else "⬇️"
        direction_7d = "⬆️" if value > value_7d else "⬇️"
        return value, direction_1d, direction_7d

    cols = st.beta_columns(2)

    # Incidence
    value, direction_1d, direction_7d = get_summary_of(
        "cases_14_days_sum_per_100K",
        cases,
    )
    with cols[0]:
        st.write("14-day incidence:", round(value, 2))
    with cols[1]:
        st.write(direction_1d, "from yesterday,", direction_7d,
                 "from last week")

    # Cases
    value, direction_1d, direction_7d = get_summary_of(
        "cases",
        cases,
    )
    with cols[0]:
        st.write("Daily cases:", round(value, 2))
    with cols[1]:
        st.write(direction_1d, "from yesterday,", direction_7d,
                 "from last week")

    # Positivity rate
    value, direction_1d, direction_7d = get_summary_of(
        "positivity_rate",
        cases,
    )
    with cols[0]:
        st.write("Positivity rate:", round(value, 2), "%")
    with cols[1]:
        st.write(direction_1d, "from yesterday,", direction_7d,
                 "from last week")

    # Tests
    value, direction_1d, direction_7d = get_summary_of(
        "tests",
        cases,
    )
    with cols[0]:
        st.write("Tests:", round(value, 2))
    with cols[1]:
        st.write(direction_1d, "from yesterday,", direction_7d,
                 "from last week")

    st.subheader(
        "14-day cumulative cases per 100,000 inhabitants, last 90 days")
    p = plot_overview(cases.date, cases.cases_14_days_sum_per_100K)
    st.bokeh_chart(p)

    st.stop()
elif summarize_by == summarize_by_values["daily"]:
    st.header("Daily")

    st.subheader("Daily cases")
    p = plot_ts(cases.date, cases.cases)
    st.bokeh_chart(p)

    st.subheader("Daily tests")
    p = plot_ts(cases.date, cases.tests)
    st.bokeh_chart(p)

    st.subheader("Daily deaths")
    p = plot_ts(cases.date, cases.deaths)
    st.bokeh_chart(p)

    st.stop()
elif summarize_by == summarize_by_values["14d_sum"]:
    st.header("14-day sum")

    st.subheader("14-day cumulative cases")
    p = plot_ts(cases.date, cases.cases_14_days_sum)
    st.bokeh_chart(p)

    st.subheader("14-day cumulative deaths")
    p = plot_ts(cases.date, cases.deaths_14_days_sum)
    st.bokeh_chart(p)

    st.stop()
elif summarize_by == summarize_by_values["14d_mean"]:
    st.header("14-day mean")

    st.subheader("14-day mean cases")
    p = plot_ts(cases.date, cases.cases_14_days_mean)
    st.bokeh_chart(p)

    st.subheader("14-day mean deaths")
    p = plot_ts(cases.date, cases.deaths_14_days_mean)
    st.bokeh_chart(p)

    st.stop()
elif summarize_by == summarize_by_values["14d_sum_normalized"]:
    st.header("14-day sum per 100,000 inhabitants")

    st.subheader("14-day cumulative cases per 100,000 inhabitants")
    p = plot_ts(cases.date, cases.cases_14_days_sum_per_100K)
    st.bokeh_chart(p)

    st.subheader("14-day cumulative deaths per 100,000 inhabitants")
    p = plot_ts(cases.date, cases.deaths_14_days_sum_per_100K)
    st.bokeh_chart(p)

    st.stop()
else:
    ValueError("Unexpected value in the sidebar")
