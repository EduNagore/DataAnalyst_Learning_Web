import pytest
from evaluate import classify, same_result, wilson_interval
from guard import strip_literals, validate_sql, with_limit


@pytest.mark.parametrize(
    ("sql", "esperado"),
    [
        ("SELECT COUNT(*) FROM customers", (True, "ok")),
        ("WITH a AS (SELECT * FROM orders) SELECT COUNT(*) FROM a", (True, "ok")),
        ("SELECT 'DROP TABLE x' AS texto", (True, "ok")),
        ("", (False, "vacia")),
        ("SELECT 1; DROP TABLE customers", (False, "multiples_sentencias")),
        ("DROP TABLE customers", (False, "no_es_select")),
        ("SELECT * FROM read_csv('/etc/passwd')", (False, "funcion_prohibida:read_csv")),
        ("SELECT * FROM secretos", (False, "tabla_no_permitida:secretos")),
    ],
)
def test_validate_sql(sql, esperado):
    assert validate_sql(sql) == esperado


def test_strip_literals_y_limit():
    assert "drop" not in strip_literals("SELECT 'drop table' AS t").lower()
    limitada = with_limit("SELECT * FROM orders", 10)
    assert "10" in limitada and "orders" in limitada


def test_same_result_ignora_orden_y_redondeos():
    assert same_result([("a", 1.0), ("b", 2.0)], [("b", 2.001), ("a", 1.0)])
    assert not same_result([("a", 1.0)], [("a", 2.0)])


def test_classify():
    assert classify(True, [(1,)], [(1,)], None) == "correcta"
    assert classify(True, [(1,)], [(2,)], None) == "resultado_distinto"
    assert classify(True, [(1,)], None, "SQL error") == "error_ejecucion"
    assert classify(False, None, None, "ABSTENCION") == "abstencion_correcta"
    assert classify(True, [(1,)], None, "ABSTENCION") == "abstencion_innecesaria"


def test_wilson():
    low, high = wilson_interval(4, 10)
    assert low == pytest.approx(0.168, abs=0.002)
    assert high == pytest.approx(0.687, abs=0.002)
