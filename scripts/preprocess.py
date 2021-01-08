import yaml
import pandas as pd


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


def preprocess_population(df):
    return df.set_index("name")


def preprocess_cases(df):
    # Convert positivy rate to decimal from percentage
    df.loc[:, "positivity_rate"] = df.loc[:, "positivity_rate"] / 100
    # Remove trailing dot in dates, so it is parsable
    df.loc[:, "date"] = df.loc[:, "date"].apply(lambda d: d[:-1])
    # Convert string date to actual date
    df.loc[:, "date"] = pd.to_datetime(df.loc[:, "date"])
    # Fill in missing dates (if any)
    df = df.sort_values("date")
    df = df.set_index("date")
    df = df.asfreq("D")
    df = df.reset_index()
    df.loc[:, "date"] = df.loc[:, "date"].apply(lambda d: d.date())
    return df


if __name__ == "__main__":
    # Read in configs
    configs = yaml.safe_load(open("configs.yaml", "r"))

    # Preprocess population
    population = pd.read_csv(configs["data"]["population"]["clean"]["path"])
    population = preprocess_population(population)

    # Preprocess cases
    cases = pd.read_csv(configs["data"]["cases"]["clean"]["path"])
    cases = preprocess_cases(cases)

    # Compute 14-day cumulative indicators
    cases = get_n_day_sum("cases", "cases_14_days_sum", cases)
    cases = get_n_day_sum("deaths", "deaths_14_days_sum", cases)

    # Compute 14-day mean indicators
    cases = get_n_day_mean("cases", "cases_14_days_mean", cases)
    cases = get_n_day_mean("deaths", "deaths_14_days_mean", cases)

    # Compute per 100K indicators
    population_latvia = population.loc["VISA LATVIJA", "total"]
    multiplier = (1e5 / population_latvia)

    col = "cases_14_days_sum"
    cases.loc[:, f"{col:s}_per_100K"] = cases.loc[:, col] * multiplier

    col = "deaths_14_days_sum"
    cases.loc[:, f"{col:s}_per_100K"] = cases.loc[:, col] * multiplier

    # Save
    population.to_csv(configs["data"]["population"]["processed"]["path"])
    cases.to_csv(configs["data"]["cases"]["processed"]["path"])
