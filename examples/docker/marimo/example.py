import marimo

__generated_with = "0.4.0"
app = marimo.App()


@app.cell
def __():
    import pandas as pd
    return pd,


@app.cell
def __(pd):
    pd.DataFrame({"x": range(10)})
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
