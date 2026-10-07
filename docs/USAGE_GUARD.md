# usage-guard: pausa automática al 95 % de la ventana de 5 h

Script: [`scripts/usage-guard.mjs`](../scripts/usage-guard.mjs) (Node, sin dependencias, **sin red y sin leer credenciales**).

Objetivo: que una sesión larga de Claude Code (como la construcción de esta web) **no se quede a medias** por agotar el límite. Al llegar al 95 % de la ventana de 5 h, el agente guarda su progreso, se detiene **sin gastar tokens** y el sistema le avisa cuando la ventana se restablece para que continúe solo.

## Cómo funciona

1. **Medición** (en este orden):
   - **`statusLine` (oficial)**: Claude Code ≥ 2.1.80 envía `rate_limits.five_hour.used_percentage` y `resets_at` por stdin al comando `statusLine`. `usage-guard statusline` los guarda en `~/.claude/usage-guard/state.json`. Es la fuente fiable.
   - **Estimación local** (respaldo): suma los tokens del bloque de 5 h activo leyendo `~/.claude/projects/**/*.jsonl` (entrada + salida + creación de caché, deduplicados por mensaje). Da el porcentaje solo si has **calibrado** el límite.
2. **Freno** (`hook`, evento `PreToolUse`): antes de cada herramienta, si el uso ≥ 95 %, la deniega con una instrucción clara: guardar progreso, lanzar `wait` en segundo plano y terminar el turno. Siguen permitidos: `git add/commit/push/status/diff/log`, editar `docs/PROGRESO.md` y cualquier comando de `usage-guard.mjs`.
3. **Espera sin tokens** (`wait`): proceso en segundo plano que duerme hasta la hora de reinicio de la ventana (+30 s de margen). El agente no hace llamadas mientras tanto (0 tokens). Al terminar emite un pitido (Windows) y el sistema re-invoca al agente: _«RESTABLECIDO … continúa desde docs/PROGRESO.md»_.

## Puesta en marcha (una vez)

1. Los ajustes ya están en [`.claude/settings.json`](../.claude/settings.json) (hook + statusLine). **Claude Code pide revisar los hooks nuevos**: abre `/hooks` (o reinicia la sesión) y aprueba el hook `PreToolUse` de `usage-guard`.
2. Comprueba que mide: `node scripts/usage-guard.mjs status`.
   - Si la fuente es `statusline`, el porcentaje es el real. (En la extensión de VS Code puede que `statusLine` no se ejecute: entonces se usa la estimación.)
   - Si dice «sin calibrar», haz una calibración: mira el % de la ventana de 5 h en `/usage` y ejecuta `node scripts/usage-guard.mjs calibrate <porcentaje>` (por ejemplo `calibrate 37`). Recalibra de vez en cuando; el límite real varía con el plan, el modelo y la hora.

## Comandos

| Comando                | Qué hace                                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------------------------ |
| `status [--json]`      | Uso actual, fuente, hora de reinicio. Código de salida 10 si hay que pausar.                           |
| `wait [--threshold N]` | Espera (sin consumir tokens) hasta el reinicio. Sale al instante si el uso está por debajo del umbral. |
| `calibrate <pct>`      | Fija el límite de tokens para la estimación local.                                                     |
| `config`               | Muestra directorio de estado y configuración.                                                          |
| `statusline` / `hook`  | Uso interno (los invoca Claude Code).                                                                  |

Variables de entorno: `USAGE_GUARD_THRESHOLD` (95 por defecto), `USAGE_GUARD_TOKEN_LIMIT`, `USAGE_GUARD_DIR`, `USAGE_GUARD_MARGIN_MS`.

## Garantías y límites (honestidad)

- Con la fuente `statusline`, el 95 % es el dato real del servidor. Con la **estimación**, el bloque se ancla a la hora en punto del primer mensaje (como `ccusage`) y el límite sale de tu calibración: puede desviarse unos puntos y hasta ~1 h en la hora de reinicio. Si prefieres margen, baja el umbral (`USAGE_GUARD_THRESHOLD=90`).
- No se usa el endpoint OAuth no documentado de uso, porque obliga a leer y enviar tu token de sesión desde fuera de Claude Code (terceros lo señalan como contrario a los términos de uso). Todo lo de arriba es local u oficial.
- El hook solo actúa si está aprobado en `/hooks`; sin él, el agente aplica la norma por disciplina: ejecutar `node scripts/usage-guard.mjs status` al terminar cada lección/fase.
- Si el uso es el semanal (7 d) lo que se agota, el script lo muestra con `statusline` pero **no** lo gestiona.

Pruebas: `tests/unit/usageGuard.test.ts` (bloques de 5 h, decisión, lista de herramientas permitidas, hook/statusline/wait por CLI con estado temporal).
