from datakit.data import load_table
from scipy.stats import chisquare
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

assignments = load_table("experiment_assignments")
metrics = load_table("experiment_metrics")


def hay_srm(assignments, experiment_id, esperado=(0.5, 0.5), alpha=0.001):
    """True si el reparto control/tratamiento se desvía de lo esperado (SRM)."""
    sub = assignments[assignments["experiment_id"] == experiment_id]
    observado = [int((sub["variant"] == v).sum()) for v in ("control", "tratamiento")]
    total = sum(observado)
    # f_exp son CONTEOS esperados (n * proporción), no proporciones.
    p_valor = chisquare(observado, f_exp=[total * p for p in esperado]).pvalue
    return bool(p_valor < alpha)


def analizar_efecto(metrics, experiment_id):
    """Devuelve {'diferencia', 'lift', 'ic95': (inf, sup), 'p_valor'} de la métrica principal."""
    sub = metrics[metrics["experiment_id"] == experiment_id]
    principal = sub["metric_name"].iloc[0]
    sub = sub[sub["metric_name"] == principal]
    control = sub.loc[sub["variant"] == "control", "value"].to_numpy()
    tratamiento = sub.loc[sub["variant"] == "tratamiento", "value"].to_numpy()

    comparacion = CompareMeans(DescrStatsW(tratamiento), DescrStatsW(control))
    diferencia = float(tratamiento.mean() - control.mean())
    inferior, superior = comparacion.tconfint_diff(alpha=0.05, usevar="unequal")
    p_valor = float(comparacion.ttest_ind(usevar="unequal")[1])
    return {
        "diferencia": diferencia,
        "lift": diferencia / float(control.mean()),
        "ic95": (float(inferior), float(superior)),
        "p_valor": p_valor,
    }
