export function paginar(items, pagina = 1, tamano = 10) {
  const paginas = Math.max(1, Math.ceil(items.length / tamano));
  const actual = Math.max(1, Math.min(paginas, pagina));
  const inicio = (actual - 1) * tamano;
  return { items: items.slice(inicio, inicio + tamano), actual, paginas,
    desde: items.length ? inicio + 1 : 0, hasta: Math.min(inicio + tamano, items.length) };
}
