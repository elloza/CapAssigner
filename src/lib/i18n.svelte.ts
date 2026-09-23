// Bilingual strings (Spanish by default) and the reactive language setting.

import { formatCapacitance as fc, localNumber, setDecimalComma } from './units';
import type { Check } from './form';

export type Lang = 'es' | 'en';

function duration(s: number): string {
  if (s < 1) return `${Math.max(1, Math.round(s * 1000))} ms`;
  if (s < 60) return localNumber(`${s < 10 ? s.toFixed(1) : Math.round(s)} s`);
  return `${Math.floor(s / 60)} min ${Math.round(s % 60)} s`;
}

const es = {
  appName: 'CapAssigner',
  tagline: 'Síntesis de redes de condensadores con capacidad equivalente objetivo',
  tabSolve: 'Resolver',
  tabTheory: 'Teoría y métodos',
  tabAbout: 'Acerca de',
  mode: 'Problema',
  modeAll: 'Usar todos los condensadores',
  modeAllHint: 'Cada condensador de la lista se usa exactamente una vez (ejercicio clásico).',
  modeInventory: 'Elegir de un inventario',
  modeInventoryHint: 'Escoge las mejores combinaciones de 1 a K piezas de una serie E o de tu cajón.',
  target: 'Capacidad objetivo',
  capacitors: 'Condensadores',
  capacitorsHint: 'Separados por espacios, comas o saltos de línea. Ej.: 3pF 2pF 3pF 1pF · 4n7 · 2,2µF · 1e-11 · 170/71pF',
  defaultUnit: 'Unidad si no se indica',
  inventorySource: 'Inventario',
  eSeries: 'Serie E',
  customList: 'Mi cajón',
  decades: 'Décadas',
  from: 'desde',
  to: 'hasta',
  valuesCount: (n: number) => `${n} valores disponibles, cantidad ilimitada`,
  stockHint: 'Formato «valor×cantidad», p. ej. 10pF×2 4.7pF×3. Sin «×» = ilimitado.',
  maxParts: 'Máximo de piezas',
  minParts: 'Mínimo de piezas',
  topology: 'Topologías',
  topoSP: 'Serie-paralelo',
  topoBridge: 'Serie-paralelo + puentes',
  topoAll: 'Todas las redes',
  topoHint: '«Todas» incluye cualquier red de dos terminales (puentes y núcleos 3-conexos), hasta 8 piezas en «usar todos».',
  topoDisabled: 'Con más de 8 piezas solo se exploran redes serie-paralelo (las demás topologías son millones de combinaciones).',
  tolerance: 'Error aceptable',
  partTolerance: 'Tolerancia de las piezas',
  results: 'Resultados',
  solve: 'Buscar redes',
  cancel: 'Cancelar',
  examples: 'Ejemplos',
  estimate: 'Estimación',
  instant: 'instantáneo',
  estExhaustive: 'búsqueda exhaustiva',
  estBounded: 'búsqueda con cota garantizada',
  longWarn: 'Puede tardar un rato. Puedes cancelar en cualquier momento.',
  computing: 'Buscando redes…',
  progress: 'Progreso',
  elapsed: 'Transcurrido',
  remaining: 'Restante',
  runningHint: 'El cálculo se hace en tu navegador, en segundo plano; la página sigue respondiendo.',
  cancelled: 'Búsqueda cancelada.',
  outOfMemory: 'El navegador se ha quedado sin memoria para esta búsqueda. Reduce el número de piezas o de valores, o elige solo serie-paralelo.',
  emptyTitle: 'Encuentra la mejor asociación de condensadores',
  emptySteps: [
    'Escribe la capacidad objetivo y los condensadores disponibles.',
    'Elige si hay que usarlos todos o escoger de un inventario.',
    'Pulsa «Buscar redes»: verás las mejores redes, su esquema y la verificación exacta.',
  ],
  tryExample: 'O prueba un ejemplo:',
  errorsIn: 'No se entiende',
  exhaustive: 'Búsqueda exhaustiva',
  exhaustiveHint: (scope: string) => `Se han considerado todas las ${scope}: no existe ninguna mejor.`,
  approximate: 'Búsqueda con cota garantizada',
  approximateHint: (scope: string, b: string) =>
    `Entre las ${scope}, ninguna puede mejorar el error del primer resultado en más de ${b}.`,
  partial: 'Búsqueda parcial',
  partialHint: (b: string) =>
    `Para las redes serie-paralelo la cota es ${b}; algunas redes con puentes u otros núcleos no se han explorado por su coste (reduce piezas o valores para incluirlas).`,
  scopeSP: 'redes serie-paralelo',
  scopeBridge: 'redes serie-paralelo y con puentes',
  scopeAll: 'redes de dos terminales (cualquier topología)',
  stats: (states: number, entries: number, ms: number) =>
    `${states.toLocaleString('es')} estados · ${entries.toLocaleString('es')} valores · ${duration(ms / 1000)}`,
  colRank: '#',
  colCeq: 'C equivalente',
  colError: 'Error',
  colParts: 'Piezas',
  colNetwork: 'Red',
  within: 'dentro del error aceptable',
  outside: 'fuera del error aceptable',
  detail: 'Solución',
  diagram: 'Esquema',
  legend: '∥ = paralelo · — = serie',
  chartTitle: 'Dónde caen las soluciones respecto al objetivo',
  chartTarget: 'objetivo',
  chartParts: (p: number) => `${p} ${p === 1 ? 'pieza' : 'piezas'}`,
  chartNote: 'Error relativo con signo en escala logarítmica simétrica; la banda verde es el error aceptable. Pulsa un punto para ver esa solución.',
  verification: 'Verificación independiente',
  verifiedOk: 'Verificado: análisis nodal, balance de energía y conservación de carga coinciden.',
  verifiedBad: 'La verificación ha fallado',
  exactValue: 'Valor exacto',
  exactError: 'Error exacto',
  exactZero: '0 (solución exacta)',
  interval: 'Intervalo con tolerancias',
  intervalHint: (t: string) => `Si cada pieza varía ±${t}, C_eq queda en este intervalo (la red es monótona y homogénea).`,
  parts: 'Piezas y reparto',
  colPart: 'Pieza',
  colValue: 'Valor',
  colVoltage: 'Tensión',
  colCharge: 'Carga',
  colEnergy: 'Energía',
  partsHint:
    'Con 1 V entre A y B. La tensión al cuadrado es la sensibilidad absoluta ∂C_eq/∂C_i; la columna Energía es la sensibilidad relativa (suma 100 %).',
  statSpread: 'Error típico con piezas independientes',
  statHint: (t: string, k: string) => `si cada pieza tiene un error independiente de ±${t}, se promedian: √Σw² = ${k}`,
  export: 'Exportar',
  copy: 'Copiar',
  copied: 'Copiado',
  download: 'Descargar',
  share: 'Enlace al problema',
  language: 'Idioma',
  theme: 'Tema',
  offline: 'Todo se calcula en tu navegador (Rust → WebAssembly). No se envía ningún dato.',
  changelog: 'Novedades',
  check: (c: Check): string => {
    switch (c.code) {
      case 'unreachableLow':
        return `Objetivo inalcanzable: ninguna red baja de ${fc(c.min)} (todo en serie). Se mostrarán las más cercanas.`;
      case 'unreachableHigh':
        return `Objetivo inalcanzable: ninguna red supera ${fc(c.max)} (todo en paralelo). Se mostrarán las más cercanas.`;
      case 'spread':
        return `Los valores difieren en unas ${c.decades} décadas. En serie mandan los pequeños y en paralelo los grandes; ¿están bien las unidades?`;
      case 'tiny':
        return `${fc(c.value)} es menor que las capacidades parásitas típicas (0,1–1 pF): el montaje real no lo respetará.`;
      case 'huge':
        return `${fc(c.value)} es un supercondensador. ¿Querías otra unidad (µF, nF)? Revisa también la unidad por defecto.`;
      case 'ratio':
        return 'El objetivo y los valores difieren en más de 150 órdenes de magnitud: revisa las unidades.';
      case 'classes':
        return `Con existencias limitadas se admiten como mucho 32 valores distintos (hay ${c.count}). Quita valores o deja la cantidad ilimitada.`;
    }
  },
  duration,
};

export type Strings = typeof es;

const en: Strings = {
  appName: 'CapAssigner',
  tagline: 'Synthesis of capacitor networks with a target equivalent capacitance',
  tabSolve: 'Solve',
  tabTheory: 'Theory & methods',
  tabAbout: 'About',
  mode: 'Problem',
  modeAll: 'Use every capacitor',
  modeAllHint: 'Each capacitor in the list is used exactly once (classic exercise).',
  modeInventory: 'Pick from an inventory',
  modeInventoryHint: 'Finds the best combinations of 1 to K parts from an E-series or your own drawer.',
  target: 'Target capacitance',
  capacitors: 'Capacitors',
  capacitorsHint: 'Separated by spaces, commas or new lines. E.g. 3pF 2pF 3pF 1pF · 4n7 · 2.2µF · 1e-11 · 170/71pF',
  defaultUnit: 'Unit when omitted',
  inventorySource: 'Inventory',
  eSeries: 'E-series',
  customList: 'My drawer',
  decades: 'Decades',
  from: 'from',
  to: 'to',
  valuesCount: (n: number) => `${n} values available, unlimited quantity`,
  stockHint: 'Write "value×count", e.g. 10pF×2 4.7pF×3. No "×" = unlimited.',
  maxParts: 'Maximum parts',
  minParts: 'Minimum parts',
  topology: 'Topologies',
  topoSP: 'Series-parallel',
  topoBridge: 'Series-parallel + bridges',
  topoAll: 'All networks',
  topoHint: '"All" includes any two-terminal network (bridges and 3-connected cores), up to 8 parts in "use all".',
  topoDisabled: 'With more than 8 parts only series-parallel networks are explored (other topologies mean millions of combinations).',
  tolerance: 'Acceptable error',
  partTolerance: 'Part tolerance',
  results: 'Results',
  solve: 'Find networks',
  cancel: 'Cancel',
  examples: 'Examples',
  estimate: 'Estimate',
  instant: 'instant',
  estExhaustive: 'exhaustive search',
  estBounded: 'search with a guaranteed bound',
  longWarn: 'This may take a while. You can cancel at any time.',
  computing: 'Searching networks…',
  progress: 'Progress',
  elapsed: 'Elapsed',
  remaining: 'Remaining',
  runningHint: 'The computation runs in your browser, in the background; the page stays responsive.',
  cancelled: 'Search cancelled.',
  outOfMemory: 'The browser ran out of memory for this search. Use fewer parts or values, or choose series-parallel only.',
  emptyTitle: 'Find the best capacitor combination',
  emptySteps: [
    'Type the target capacitance and the capacitors you have.',
    'Choose whether all must be used or picked from an inventory.',
    'Press "Find networks": you get the best networks, their schematics and exact verification.',
  ],
  tryExample: 'Or try an example:',
  errorsIn: 'Cannot read',
  exhaustive: 'Exhaustive search',
  exhaustiveHint: (scope: string) => `Every one of the ${scope} was considered: none is better.`,
  approximate: 'Search with a guaranteed bound',
  approximateHint: (scope: string, b: string) =>
    `Among the ${scope}, none can improve on the first result's error by more than ${b}.`,
  partial: 'Partial search',
  partialHint: (b: string) =>
    `For series-parallel networks the bound is ${b}; some networks with bridges or other cores were not explored because of their cost (use fewer parts or values to include them).`,
  scopeSP: 'series-parallel networks',
  scopeBridge: 'series-parallel and bridge networks',
  scopeAll: 'two-terminal networks (any topology)',
  stats: (states: number, entries: number, ms: number) =>
    `${states.toLocaleString('en')} states · ${entries.toLocaleString('en')} values · ${duration(ms / 1000)}`,
  colRank: '#',
  colCeq: 'Equivalent C',
  colError: 'Error',
  colParts: 'Parts',
  colNetwork: 'Network',
  within: 'within the acceptable error',
  outside: 'outside the acceptable error',
  detail: 'Solution',
  diagram: 'Schematic',
  legend: '∥ = parallel · — = series',
  chartTitle: 'Where the solutions fall relative to the target',
  chartTarget: 'target',
  chartParts: (p: number) => `${p} ${p === 1 ? 'part' : 'parts'}`,
  chartNote: 'Signed relative error on a symmetric log scale; the green band is the acceptable error. Click a dot to see that solution.',
  verification: 'Independent verification',
  verifiedOk: 'Verified: nodal analysis, energy balance and charge conservation agree.',
  verifiedBad: 'Verification failed',
  exactValue: 'Exact value',
  exactError: 'Exact error',
  exactZero: '0 (exact solution)',
  interval: 'Tolerance interval',
  intervalHint: (t: string) => `If every part varies by ±${t}, C_eq stays in this interval (the network is monotone and homogeneous).`,
  parts: 'Parts and sharing',
  colPart: 'Part',
  colValue: 'Value',
  colVoltage: 'Voltage',
  colCharge: 'Charge',
  colEnergy: 'Energy',
  partsHint:
    'For 1 V across A–B. The squared voltage is the absolute sensitivity ∂C_eq/∂C_i; the Energy column is the relative sensitivity (sums to 100 %).',
  statSpread: 'Typical error with independent parts',
  statHint: (t: string, k: string) => `if each part has an independent ±${t} error they average out: √Σw² = ${k}`,
  export: 'Export',
  copy: 'Copy',
  copied: 'Copied',
  download: 'Download',
  share: 'Link to this problem',
  language: 'Language',
  theme: 'Theme',
  offline: 'Everything runs in your browser (Rust → WebAssembly). No data leaves it.',
  changelog: 'Changelog',
  check: (c: Check): string => {
    switch (c.code) {
      case 'unreachableLow':
        return `Unreachable target: no network goes below ${fc(c.min)} (all in series). The closest ones will be shown.`;
      case 'unreachableHigh':
        return `Unreachable target: no network goes above ${fc(c.max)} (all in parallel). The closest ones will be shown.`;
      case 'spread':
        return `The values differ by about ${c.decades} decades. Small parts dominate in series and large ones in parallel; are the units right?`;
      case 'tiny':
        return `${fc(c.value)} is below typical stray capacitance (0.1–1 pF): a real build will not honour it.`;
      case 'huge':
        return `${fc(c.value)} is a supercapacitor. Did you mean another unit (µF, nF)? Check the default unit too.`;
      case 'ratio':
        return 'The target and the values differ by more than 150 orders of magnitude: check the units.';
      case 'classes':
        return `Limited stock accepts at most 32 distinct values (there are ${c.count}). Remove values or make the quantity unlimited.`;
    }
  },
  duration,
};

function initialLang(): Lang {
  try {
    const saved = localStorage.getItem('capassigner.lang');
    if (saved === 'es' || saved === 'en') return saved;
  } catch {
    // Storage unavailable (private mode): fall through.
  }
  return typeof navigator !== 'undefined' && navigator.language.startsWith('en') ? 'en' : 'es';
}

export const i18n = $state({ lang: initialLang() as Lang });
setDecimalComma(i18n.lang === 'es');

export function setLang(l: Lang): void {
  i18n.lang = l;
  setDecimalComma(l === 'es');
  try {
    localStorage.setItem('capassigner.lang', l);
  } catch {
    // Ignore: the choice just won't persist.
  }
  document.documentElement.lang = l;
}

export function t(): Strings {
  return i18n.lang === 'es' ? es : en;
}
