import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so


def plot_result(
    data: pd.DataFrame,
    x: str,
    y_dots: list[str] = [],
    y_line: list[str] = [],
    dots_options: dict = {},
    line_options: dict = {},
    facet_options: dict = {},
    fig_options: dict = {},
) -> plt.Figure:
    """Plot result from OneMod model.

    Parameters
    ----------
    data
        Dataframe with the results from the OneMod model.
    x
        Name of the column to use as x-axis.
    y_dots
        List of columns to plot as scatter plot.
    y_line
        List of columns to plot as line plot.
    dots_options
        Dictionary with options for scatter plot. Key to this dictionary is the
        column name that has been listed in `y_dots`.
    line_options
        Dictionary with options for line plot. Key to this dictionary is the
        column name that has been listed in `y_line`.
    facet_options
        Dictionary with options for facet plot. For details please see,
        https://seaborn.pydata.org/generated/seaborn.objects.Plot.facet.html
    fig_options
        Dictionary with options for creating the figure.

    Returns
    -------
    plt.Figure
        Figure object.

    Example
    -------
    >>> from onemod_diagnostics.figure import plot_result
    >>> data = ... # load result data for a single location
    >>> # plot result as time series
    >>> fig = plot_result(
    ...     data_sel,
    ...     x="year_id",
    ...     y_dots=["obs_rate"],
    ...     y_line=["truth", "regmod_smooth"],
    ...     dots_options=dict(obs_rate=dict(color="grey")),
    ...     facet_options=dict(col="age_mid", wrap=6),
    ...     fig_options=dict(figsize=(18, 12)),
    ... )
    >>> fig
    >>> # plot result as age series
    >>> fig = plot_result(
    ...     data_sel,
    ...     x="age_mid",
    ...     y_dots=["obs_rate"],
    ...     y_line=["truth", "regmod_smooth"],
    ...     dots_options=dict(obs_rate=dict(color="grey")),
    ...     facet_options=dict(col="year_id", wrap=6),
    ...     fig_options=dict(figsize=(18, 12)),
    ... )
    >>> fig

    """
    fig = plt.Figure(**fig_options)
    so.Plot(data, x=x).facet(**facet_options).on(fig).plot()
    axes = fig.get_axes()
    by = [
        facet_options.get(key)
        for key in ["col", "row"]
        if facet_options.get(key) is not None
    ]

    if by:
        keys = [ax.get_title().split(" | ") for ax in axes]
        data_list = []
        for key in keys:
            selection = " & ".join([f"{k} == {v}" for k, v in zip(by, key)])
            data_list.append(data.query(selection))
    else:
        data_list = [data]

    for ax, df in zip(axes, data_list):
        for y in y_dots:
            ax.scatter(df[x], df[y], label=y, **dots_options.get(y, {}))
        for y in y_line:
            ax.plot(df[x], df[y], label=y, **line_options.get(y, {}))

    # plot posinf and neginf
    ylim = ax.get_ylim()
    for ax, df in zip(axes, data_list):
        for y in y_dots:
            df = df.query(f"{y} in [-inf, inf]").reset_index(drop=True)
            if not df.empty:
                df[y] = df[y].clip(*ylim)
                ax.scatter(df[x], df[y], label=y, **dots_options.get(y, {}))
        ax.set_ylim(ylim)

    fig.legend(*ax.get_legend_handles_labels(), loc="center right")
    return fig
