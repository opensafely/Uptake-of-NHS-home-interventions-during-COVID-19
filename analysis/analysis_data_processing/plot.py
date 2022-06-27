import matplotlib.pyplot as plt
import pandas as pd


def produce_plot(
    df: pd.DataFrame,
    x_label: str = None,
    y_label: str = None,
    figure_size: tuple = (20, 10),
):
    """Function to produce plot of all dataframe columns"""
    fig, ax = plt.subplots(figsize=figure_size)
    df.replace(["[REDACTED]"], np.nan).plot(ax=ax)
    plt.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=20)
    plt.xlabel(x_label, fontsize=20)
    plt.ylabel(y_label, fontsize=20)
    plt.title("\n".join(wrap(title)), fontsize=40)



def produce_pivot_plot(
    homecare_type: str,
    counts_df: pd.DataFrame,
    code: str,
    term: str,
    column_name: str,
    variable_title: str,
    pivot_values: str,
    reorder_legend: list = None,
):
    """Function to create timeseries of code of interest broken down
    by variable of interest"""

    # Pivot based on column of interest
    pivot_df = counts_df.pivot(
        index="index_date",
        columns=column_name,
        values=pivot_values,
    )

    # Produce plot
    plot_title = 'Patients with "' + term + '" code, grouped by ' + variable_title
    produce_plot(pivot_df, plot_title, x_label="Date", y_label="Percentage")

    # Reorder legend if required
    if reorder_legend is not None:
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(
            [handles[i] for i in reorder_legend],
            [labels[i] for i in reorder_legend],
            loc="upper left",
            bbox_to_anchor=(1.0, 1.0),
            fontsize=20,
        )

    # Save plot
    plt.savefig(
        "output/"
        + homecare_type
        + "_plot_code_"
        + code
        + "_"
        + column_name
        + "_timeseries.png",
        bbox_inches="tight",
    )


def homecare_title(homecare_type):
    """Function to return title for plots based on homecare type"""
    if homecare_type == "oximetry":
        title = "Pulse Oximetry Codes"
    elif homecare_type == "bp":
        title = "Blood Pressure Monitoring Codes"
    elif homecare_type == "proactive":
        title = "Procative Care Code"
    return title
