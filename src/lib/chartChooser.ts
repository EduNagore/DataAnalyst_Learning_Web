export type Intent = 'comparar' | 'tiempo' | 'distribucion' | 'relacion' | 'composicion' | 'exacto';

export interface Variant {
  id: string;
  /** Situación concreta que distingue esta variante. */
  when: string;
  /** Gráfico recomendado. */
  chart: string;
  /** Por qué funciona (canal perceptivo). */
  why: string;
  /** Qué evitar en esta situación. */
  avoid: string;
}

export interface IntentInfo {
  label: string;
  question: string;
  variants: Variant[];
}

export const INTENTS: Record<Intent, IntentInfo> = {
  comparar: {
    label: 'Comparar categorías',
    question: '¿Qué categoría es mayor y por cuánto?',
    variants: [
      {
        id: 'pocas',
        when: 'Hasta unas 12 categorías',
        chart: 'Barras horizontales ordenadas de mayor a menor, con el eje en cero',
        why: 'La longitud sobre una escala común es de lo que mejor percibimos; ordenar facilita el ranking y la horizontal deja leer etiquetas largas.',
        avoid:
          'Tartas o anillos, ejes que no empiezan en cero, y el orden alfabético si lo que importa es el ranking.',
      },
      {
        id: 'muchas',
        when: 'Decenas de categorías',
        chart: 'Barras de las N principales más «Otras», o una tabla con formato condicional',
        why: 'Con muchas categorías el ojo no sigue más de una docena de barras; agrupar la cola devuelve la lectura.',
        avoid: 'Un gráfico de cien barras o una leyenda de colores con decenas de entradas.',
      },
      {
        id: 'cercanas',
        when: 'Valores muy parecidos entre categorías',
        chart: 'Gráfico de puntos (dot plot) con el eje ampliado y la diferencia anotada',
        why: 'Un punto permite ampliar el eje sin el engaño de la barra truncada y deja ver diferencias pequeñas.',
        avoid: 'Barras con el eje recortado: exageran la diferencia.',
      },
    ],
  },
  tiempo: {
    label: 'Mostrar la evolución en el tiempo',
    question: '¿Cómo cambia la métrica y hay tendencia o estacionalidad?',
    variants: [
      {
        id: 'serie',
        when: 'Muchos periodos consecutivos',
        chart: 'Gráfico de líneas, con el periodo en el eje horizontal',
        why: 'La pendiente (dirección) de un segmento comunica el cambio y la línea conecta los puntos como un continuo.',
        avoid: 'Barras para series largas, áreas apiladas con muchas series y dos ejes verticales.',
      },
      {
        id: 'dos',
        when: 'Solo dos o tres momentos',
        chart: 'Gráfico de pendiente (slope) o barras agrupadas',
        why: 'Con dos puntos lo importante es el cambio y su dirección; el gráfico de pendiente lo muestra sin ruido.',
        avoid: 'Una línea que sugiere una evolución continua que no se ha medido.',
      },
      {
        id: 'estacional',
        when: 'Se quiere comparar el patrón de varios años',
        chart: 'Líneas por año superpuestas, o múltiplos pequeños (un panel por año)',
        why: 'Comparar con el mismo eje de calendario hace visible la estacionalidad y la tendencia.',
        avoid: 'Una única línea larga donde el patrón anual se pierde en el crecimiento.',
      },
    ],
  },
  distribucion: {
    label: 'Ver una distribución',
    question: '¿Cómo se reparten los valores y hay colas o extremos?',
    variants: [
      {
        id: 'una',
        when: 'Una variable numérica, muchas observaciones',
        chart: 'Histograma (con anchos razonables) o función de distribución acumulada',
        why: 'Muestra forma, centro, dispersión y colas; la acumulada permite leer percentiles directamente.',
        avoid: 'Dar solo media y desviación; histogramas con pocos o demasiados tramos.',
      },
      {
        id: 'grupos',
        when: 'Comparar la distribución entre grupos',
        chart: 'Diagramas de caja, de violín o histogramas en paneles alineados',
        why: 'Alinear las escalas permite comparar medianas, dispersión y extremos de un vistazo.',
        avoid: 'Barras con la media y una barra de error: ocultan la forma.',
      },
      {
        id: 'cola',
        when: 'Cola muy larga (importes, tiempos)',
        chart: 'Histograma con tramos de ancho doble, o eje logarítmico',
        why: 'La escala logarítmica acerca las colas y deja ver el cuerpo y los extremos a la vez.',
        avoid: 'Un eje lineal donde el 98 % de los datos queda aplastado en una esquina.',
      },
    ],
  },
  relacion: {
    label: 'Relacionar dos variables',
    question: '¿Cómo se mueven juntas dos variables numéricas?',
    variants: [
      {
        id: 'pocas',
        when: 'Cientos de puntos',
        chart: 'Diagrama de dispersión, con línea de tendencia opcional',
        why: 'La posición en dos ejes es la codificación más precisa; la nube enseña la forma, no solo la correlación.',
        avoid: 'Calcular solo el coeficiente (cuarteto de Anscombe).',
      },
      {
        id: 'muchas',
        when: 'Cientos de miles de puntos',
        chart: 'Mapa de calor 2D (hexbin) o dispersión con transparencia y muestreo',
        why: 'La densidad sustituye a los puntos solapados y deja ver dónde se concentran los datos.',
        avoid: 'Una nube opaca donde los puntos se tapan entre sí.',
      },
      {
        id: 'tercera',
        when: 'Hay una tercera variable (categoría o número)',
        chart: 'Dispersión con color (categoría) o tamaño (cantidad), o paneles por categoría',
        why: 'Separar por la tercera variable evita mezclar grupos con relaciones distintas (paradoja de Simpson).',
        avoid: 'Más de cinco o seis colores, o tamaños que se comparan por área.',
      },
    ],
  },
  composicion: {
    label: 'Mostrar la composición (partes de un todo)',
    question: '¿Qué parte del total representa cada elemento?',
    variants: [
      {
        id: 'pocas',
        when: 'Dos a cuatro partes en un momento',
        chart: 'Una barra apilada al 100 % o barras con el porcentaje anotado',
        why: 'Las longitudes alineadas se comparan mejor que los ángulos; una tarta solo es aceptable con 2 o 3 partes muy distintas.',
        avoid: 'Tartas con muchas porciones, en 3D o con porciones parecidas.',
      },
      {
        id: 'tiempo',
        when: 'La composición cambia con el tiempo',
        chart: 'Barras apiladas al 100 % por periodo, o líneas por componente',
        why: 'Permite ver cómo cambia el reparto; las líneas separadas dejan comparar cada componente.',
        avoid: 'Áreas apiladas con muchas series: solo la de abajo se compara bien.',
      },
      {
        id: 'jerarquia',
        when: 'Muchas partes con jerarquía',
        chart: 'Treemap con etiquetas, o barras agrupadas por nivel',
        why: 'El área comunica proporciones aproximadas y la anidación, aunque con menos precisión que la longitud.',
        avoid: 'Usar el treemap para comparaciones finas entre valores cercanos.',
      },
    ],
  },
  exacto: {
    label: 'Consultar valores exactos',
    question: '¿Cuál es el valor preciso de cada celda?',
    variants: [
      {
        id: 'tabla',
        when: 'Se necesitan cifras exactas o hay pocas filas',
        chart:
          'Tabla con formato (cifras alineadas a la derecha, pocos decimales y sparklines o color suave)',
        why: 'Una tabla se lee, no se percibe: es la mejor opción cuando importa el número y no la forma.',
        avoid: 'Tablas enormes sin jerarquía visual y gráficos que obligan a adivinar valores.',
      },
    ],
  },
};

export function recommend(intent: Intent, variantId: string): Variant | undefined {
  return INTENTS[intent].variants.find((v) => v.id === variantId);
}
