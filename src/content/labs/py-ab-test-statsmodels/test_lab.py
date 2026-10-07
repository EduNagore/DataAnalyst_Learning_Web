from datakit.data import load_table
from datakit.testing import assert_close
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW


def _esperado(metrics, experiment_id):
    sub = metrics[metrics["experiment_id"] == experiment_id]
    sub = sub[sub["metric_name"] == sub["metric_name"].iloc[0]]
    c = sub.loc[sub["variant"] == "control", "value"].to_numpy()
    t = sub.loc[sub["variant"] == "tratamiento", "value"].to_numpy()
    cm = CompareMeans(DescrStatsW(t), DescrStatsW(c))
    lo, hi = cm.tconfint_diff(alpha=0.05, usevar="unequal")
    return {
        "diferencia": float(t.mean() - c.mean()),
        "lift": float(t.mean() - c.mean()) / float(c.mean()),
        "ic95": (float(lo), float(hi)),
        "p_valor": float(cm.ttest_ind(usevar="unequal")[1]),
    }


def test_srm_detecta_el_experimento_con_asignacion_rota(ns):
    """hay_srm detecta el problema de asignación de exp-reco-engine"""
    resultado = ns["hay_srm"](load_table("experiment_assignments"), "exp-reco-engine")
    assert resultado is True, (
        "exp-reco-engine reparte ~56 % / 44 % en vez de 50 / 50 con 20.000 clientes: "
        "eso es un SRM. Comprueba que usas conteos esperados (n * proporción) en chisquare."
    )


def test_srm_no_da_falsas_alarmas(ns):
    """hay_srm no salta en un experimento con asignación sana (exp-checkout-v2)"""
    resultado = ns["hay_srm"](load_table("experiment_assignments"), "exp-checkout-v2")
    assert resultado is False, "exp-checkout-v2 está bien repartido (≈ 50 / 50): no debería marcarse como SRM."


def test_efecto_devuelve_las_claves_esperadas(ns):
    """analizar_efecto devuelve diferencia, lift, ic95 y p_valor"""
    resultado = ns["analizar_efecto"](load_table("experiment_metrics"), "exp-checkout-v2")
    assert isinstance(resultado, dict), "analizar_efecto debe devolver un diccionario."
    faltan = [k for k in ("diferencia", "lift", "ic95", "p_valor") if k not in resultado]
    assert not faltan, f"Faltan claves en el diccionario: {', '.join(faltan)}."


def test_efecto_cifras_de_exp_checkout(ns):
    """Las cifras del efecto de exp-checkout-v2 coinciden con las esperadas"""
    metrics = load_table("experiment_metrics")
    resultado = ns["analizar_efecto"](metrics, "exp-checkout-v2")
    esperado = _esperado(metrics, "exp-checkout-v2")
    assert_close(resultado["diferencia"], esperado["diferencia"], 1e-9, "La diferencia")
    assert_close(resultado["lift"], esperado["lift"], 1e-9, "El lift")
    assert_close(resultado["ic95"][0], esperado["ic95"][0], 1e-9, "El límite inferior del IC")
    assert_close(resultado["ic95"][1], esperado["ic95"][1], 1e-9, "El límite superior del IC")
    assert_close(resultado["p_valor"], esperado["p_valor"], 1e-9, "El p-valor")


def test_efecto_usa_solo_la_metrica_principal(ns):
    """En el holdout geográfico solo se analiza la métrica principal, no la de atribución last-click"""
    metrics = load_table("experiment_metrics")
    resultado = ns["analizar_efecto"](metrics, "exp-social-ads-geo-holdout")
    esperado = _esperado(metrics, "exp-social-ads-geo-holdout")
    assert_close(resultado["lift"], esperado["lift"], 1e-9, "El lift de la métrica principal")


def test_hidden_funciona_con_otros_datos(ns):
    """Funciona también con otro conjunto de datos (test oculto)"""
    assignments = load_table("experiment_assignments", variant=True)
    metrics = load_table("experiment_metrics", variant=True)
    assert ns["hay_srm"](assignments, "exp-reco-engine") is True, "No detecta el SRM con datos más pequeños."
    assert ns["hay_srm"](assignments, "exp-checkout-v2") is False, "Falsa alarma de SRM con datos más pequeños."
    resultado = ns["analizar_efecto"](metrics, "exp-checkout-v2")
    assert_close(resultado["p_valor"], _esperado(metrics, "exp-checkout-v2")["p_valor"], 1e-9, "El p-valor")
