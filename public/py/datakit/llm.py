"""LLM simulado para los labs de IA (sin red, sin claves, determinista).

Responde con una lista guionizada (en orden) o con reglas por patrón. Cuenta
tokens aproximados (≈ 4 caracteres por token) y un «coste» ficticio para
poder razonar sobre presupuesto en los labs.
"""

import re
from collections.abc import Callable


class MockLLM:
    def __init__(
        self,
        script: list[str] | None = None,
        rules: list[tuple[str, str]] | None = None,
        default: str = "No tengo información suficiente.",
        eur_per_1k_tokens: float = 0.002,
    ):
        self._script = list(script or [])
        self._rules = [(re.compile(p, re.IGNORECASE), r) for p, r in (rules or [])]
        self._default = default
        self._price = eur_per_1k_tokens
        self.calls: list[dict] = []

    @staticmethod
    def count_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    def complete(self, prompt: str) -> str:
        if self._script:
            answer = self._script.pop(0)
        else:
            answer = next((r for pattern, r in self._rules if pattern.search(prompt)), self._default)
        self.calls.append(
            {
                "prompt": prompt,
                "answer": answer,
                "tokens": self.count_tokens(prompt) + self.count_tokens(answer),
            }
        )
        return answer

    @property
    def total_tokens(self) -> int:
        return sum(c["tokens"] for c in self.calls)

    @property
    def cost_eur(self) -> float:
        return self.total_tokens / 1000 * self._price


def make_callable(llm: MockLLM) -> Callable[[str], str]:
    return llm.complete
