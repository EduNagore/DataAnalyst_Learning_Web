from datakit.data import load_table
from scipy.stats import chisquare
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

assignments = load_table("experiment_assignments")
metrics = load_table("experiment_metrics")
print(assignments.groupby(["experiment_id", "variant"]).size().head(6))


def hay_srm(assignments, experiment_id, esperado=(0.5, 0.5), alpha=0.001):
    """True si el reparto control/tratamiento se desvía de lo esperado (SRM)."""
    # TODO: cuenta clientes por variante y aplica un test chi-cuadrado.
    ...


def analizar_efecto(metrics, experiment_id):
    """Devuelve {'diferencia', 'lift', 'ic95': (inf, sup), 'p_valor'} de la métrica principal."""
    # TODO: compara tratamiento y control con un test t de Welch.
    ...
