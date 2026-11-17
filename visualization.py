import matplotlib.pyplot as plt
import pandas as pd


def create_visualization(
    df,
    chart_type,
    x_column,
    y_column,
    chart_title="Shopit Analytics"
):
    """
    Create a visualization from the actual SQL result DataFrame.
    """

    if df is None:
        print("No data available for visualization.")
        return None

    if df.empty:
        print("DataFrame is empty. Cannot create visualization.")
        return None

    if not x_column or not y_column:
        print("X or Y column not provided.")
        return None

    if x_column not in df.columns:
        print(f"Column '{x_column}' not found in DataFrame.")
        print("Available columns:", list(df.columns))
        return None

    if y_column not in df.columns:
        print(f"Column '{y_column}' not found in DataFrame.")
        print("Available columns:", list(df.columns))
        return None

    # Create a copy so the original DataFrame is not modified
    plot_df = df.copy()

    # Convert Y column to numeric when possible
    plot_df[y_column] = pd.to_numeric(
        plot_df[y_column],
        errors="coerce"
    )

    # Remove invalid values
    plot_df = plot_df.dropna(subset=[x_column, y_column])

    if plot_df.empty:
        print("No valid data available for plotting.")
        return None

    plt.figure(figsize=(10, 6))

    # --------------------------------------------------
    # BAR CHART
    # --------------------------------------------------

    if chart_type == "bar":

        plt.bar(
            plot_df[x_column].astype(str),
            plot_df[y_column]
        )

        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(chart_title)

        plt.xticks(rotation=45, ha="right")

    # --------------------------------------------------
    # LINE CHART
    # --------------------------------------------------

    elif chart_type == "line":

        plt.plot(
            plot_df[x_column].astype(str),
            plot_df[y_column],
            marker="o"
        )

        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(chart_title)

        plt.xticks(rotation=45, ha="right")

    # --------------------------------------------------
    # PIE CHART
    # --------------------------------------------------

    elif chart_type == "pie":

        plt.pie(
            plot_df[y_column],
            labels=plot_df[x_column].astype(str),
            autopct="%1.1f%%"
        )

        plt.title(chart_title)

    # --------------------------------------------------
    # SCATTER CHART
    # --------------------------------------------------

    elif chart_type == "scatter":

        plt.scatter(
            plot_df[x_column],
            plot_df[y_column]
        )

        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(chart_title)

    else:

        print(f"Unsupported chart type: {chart_type}")
        return None

    plt.tight_layout()

    # Show chart
    plt.show()

    return True