import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import duckdb
    import marimo as mo
    import pandas as pd

    return duckdb, mo, pd


@app.cell
def _(mo):
    mo.md(
        """
        # Análisis del experimento

        **Decisión que depende de este análisis:** _escríbela aquí_.

        1. Validez (SRM) · 2. Potencia · 3. Efecto · 4. CUPED · 5. Segmentos · 6. Recomendación
        """
    )
    return


@app.cell
def _(duckdb):
    con = duckdb.connect()
    experimentos = con.execute("SELECT * FROM 'data/experiments.parquet'").df()
    experimentos
    return con, experimentos


@app.cell
def _(mo):
    mo.md("## 1. Validez: ¿el reparto coincide con el diseñado?\n\nTODO: usa `analysis.srm_pvalue`.")
    return


@app.cell
def _(mo):
    mo.md("## 2. Efecto\n\nTODO: diferencia de medias con intervalo (`analysis.diff_in_means`).")
    return


@app.cell
def _(mo):
    mo.md("## 3. CUPED\n\nTODO: ajusta con una covariable previa y compara la anchura del intervalo.")
    return


@app.cell
def _(mo):
    mo.md("## 4. Recomendación\n\nTODO: decisión, confianza, riesgos y siguiente paso.")
    return


if __name__ == "__main__":
    app.run()
