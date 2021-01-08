import dash

def update_yaxis_range(xaxis_range, fig):
    if fig is None or xaxis_range is None or "xaxis.range" not in xaxis_range:
        return dash.no_update

    # Get new range
    begin, end = xaxis_range["xaxis.range"]

    # Find max y in the new range
    data = zip(fig["data"][0]["x"], fig["data"][0]["y"])
    y_max = max([y for x, y in data if x >= begin and x <= end])

    # Make sure range slider does not change range
    fig["layout"]["xaxis"]["rangeslider"]["yaxis"]["range"] = [
        min(fig["data"][0]["y"]) - 0.05 * max(fig["data"][0]["y"]),
        1.05 * max(fig["data"][0]["y"]),
    ]
    fig["layout"]["xaxis"]["rangeslider"]["yaxis"]["rangemode"] = "normal"

    # Change range of graph
    fig["layout"]["yaxis"]["range"][1] = 1.05 * y_max
    fig["layout"]["yaxis"]["autorange"] = False
    return fig    

def update_double_yaxis_range(xaxis_range, fig):
    if fig is None or xaxis_range is None or "xaxis.range" not in xaxis_range:
        return dash.no_update

    # Get new range
    begin, end = xaxis_range["xaxis.range"]

    # Find max y in the new range
    data = zip(fig["data"][0]["x"], fig["data"][0]["y"])
    y_max1 = max([y for x, y in data if x >= begin and x <= end])

    data = zip(fig["data"][1]["x"], fig["data"][1]["y"])
    y_max2 = max([y for x, y in data if x >= begin and x <= end])

    # Make sure range slider does not change range
    for i, yaxis in enumerate(["yaxis", "yaxis2"]):
        fig["layout"]["xaxis"]["rangeslider"][yaxis]["range"] = [
            min(fig["data"][i]["y"]) - 0.05 * max(fig["data"][i]["y"]),
            1.05 * max(fig["data"][i]["y"]),
        ]
        fig["layout"]["xaxis"]["rangeslider"][yaxis]["rangemode"] = "normal"

    # Change range of graph
    fig["layout"]["yaxis"]["range"][1] = 1.05 * y_max1
    fig["layout"]["yaxis"]["autorange"] = False

    fig["layout"]["yaxis2"]["range"][1] = 1.05 * y_max2
    fig["layout"]["yaxis2"]["autorange"] = False

    return fig