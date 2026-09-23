import React from 'react';
import Icono from './Iconos';

/**
 * Panel de consumo del agente de IA. Solo lo ve el rol admin.
 *
 * Sirve para dos cosas: seguir el gasto mientras se usa el sistema, y tener cifras
 * concretas para hablar de la rentabilidad del agente.
 *
 * Los análisis sin consumo registrado se informan por separado en lugar de contarse
 * como gasto cero. Son los que se generaron antes de que el sistema empezara a
 * registrar el consumo, y presentarlos como gratis sería engañoso.
 *
 * Props:
 * - consumo: respuesta de GET /api/ia/consumo
 * - cargando / error: estado de la carga
 * - alRecargar: vuelve a pedir los datos
 */

function montoUSD(valor, decimalesMin = 4, decimalesMax = 6) {
  return (valor ?? 0).toLocaleString('es-CL', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimalesMin,
    maximumFractionDigits: decimalesMax,
  });
}

function numero(valor) {
  return (valor ?? 0).toLocaleString('es-CL');
}

function ConsumoIA({ consumo, cargando, error, alRecargar }) {
  if (cargando) {
    return <div className="state-message">Cargando consumo del agente...</div>;
  }

  if (error) {
    return (
      <div className="panel">
        <div className="panel-cuerpo">
          <div className="alert-error">
            <Icono nombre="alerta" />
            <span>{error}</span>
          </div>
        </div>
      </div>
    );
  }

  if (!consumo) return null;

  const {
    total_analisis: total,
    analisis_sin_consumo: sinConsumo,
    tokens_entrada: tokensEntrada,
    tokens_salida: tokensSalida,
    costo_total_usd: costoTotal,
    costo_promedio_usd: promedio,
    presupuesto_usd: presupuesto,
    porcentaje_usado: porcentaje,
    por_tipo: porTipo,
    por_modelo: porModelo,
    por_dia: porDia,
    configuracion: config,
  } = consumo;

  const restante = presupuesto != null ? presupuesto - costoTotal : null;

  // Con el presupuesto y el costo promedio se puede estimar cuántos análisis más
  // entran. Es la cifra más útil para decidir si el agente es viable.
  const analisisRestantes =
    restante != null && promedio ? Math.floor(restante / promedio) : null;

  // El día con más gasto define la escala de las barras
  const maximoDiario = porDia.reduce((max, d) => Math.max(max, d.costo_usd), 0);

  return (
    <>
      {/* ── Indicadores ── */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-encabezado">
            <Icono nombre="tendencia" tamano={13} />
            <span className="kpi-label">Gastado</span>
          </div>
          <div className="kpi-numero">{montoUSD(costoTotal)}</div>
          <div className="kpi-detalle">
            {presupuesto != null
              ? `${porcentaje < 0.01 ? '<0,01' : porcentaje.toFixed(2)}% de ${montoUSD(presupuesto, 2, 2)}`
              : 'Sin presupuesto declarado'}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-encabezado">
            <Icono nombre="baseDatos" tamano={13} />
            <span className="kpi-label">Disponible</span>
          </div>
          <div className="kpi-numero">
            {restante != null ? montoUSD(restante, 2, 4) : '—'}
          </div>
          <div className="kpi-detalle">
            {analisisRestantes != null
              ? `alcanza para unos ${numero(analisisRestantes)} análisis más`
              : 'declara IA_PRESUPUESTO_USD para verlo'}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-encabezado">
            <Icono nombre="panel" tamano={13} />
            <span className="kpi-label">Análisis</span>
          </div>
          <div className="kpi-numero">{numero(total)}</div>
          <div className="kpi-detalle">
            {sinConsumo > 0
              ? `${numero(sinConsumo)} sin datos de consumo`
              : 'todos con consumo registrado'}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-encabezado">
            <Icono nombre="etiqueta" tamano={13} />
            <span className="kpi-label">Costo promedio</span>
          </div>
          <div className="kpi-numero">
            {promedio != null ? montoUSD(promedio) : '—'}
          </div>
          <div className="kpi-detalle">
            {numero(tokensEntrada)} enviados · {numero(tokensSalida)} recibidos
          </div>
        </div>
      </div>

      {total === 0 && (
        <div className="panel">
          <div className="state-message empty">
            <Icono nombre="tendencia" tamano={20} />
            <span className="vacio-titulo">Todavía no hay consumo registrado</span>
            <span className="vacio-detalle">
              Las cifras aparecen a medida que se generan resúmenes y recomendaciones
              desde la ficha de un lead.
            </span>
          </div>
        </div>
      )}

      {/* ── Desglose por tipo y por modelo ── */}
      {total > 0 && (
        <div className="grid-dos">
          <div className="panel">
            <div className="panel-encabezado">
              <span className="panel-titulo">Por tipo de análisis</span>
            </div>
            <div className="table-wrapper">
              <table className="leads-table">
                <thead>
                  <tr>
                    <th>Tipo</th>
                    <th>Cantidad</th>
                    <th>Tokens</th>
                    <th>Costo</th>
                  </tr>
                </thead>
                <tbody>
                  {porTipo.map((fila) => (
                    <tr key={fila.etiqueta}>
                      <td className="celda-principal">{fila.etiqueta}</td>
                      <td className="col-numero">{numero(fila.cantidad)}</td>
                      <td className="col-numero">
                        {numero(fila.tokens_entrada + fila.tokens_salida)}
                      </td>
                      <td className="col-numero">{montoUSD(fila.costo_usd)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="panel">
            <div className="panel-encabezado">
              <span className="panel-titulo">Por modelo</span>
            </div>
            <div className="table-wrapper">
              <table className="leads-table">
                <thead>
                  <tr>
                    <th>Modelo</th>
                    <th>Cantidad</th>
                    <th>Tokens</th>
                    <th>Costo</th>
                  </tr>
                </thead>
                <tbody>
                  {porModelo.map((fila) => (
                    <tr key={fila.etiqueta}>
                      <td className="celda-principal">{fila.etiqueta}</td>
                      <td className="col-numero">{numero(fila.cantidad)}</td>
                      <td className="col-numero">
                        {numero(fila.tokens_entrada + fila.tokens_salida)}
                      </td>
                      <td className="col-numero">{montoUSD(fila.costo_usd)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── Evolución diaria ── */}
      {porDia.length > 0 && (
        <div className="panel">
          <div className="panel-encabezado">
            <span className="panel-titulo">Gasto por día</span>
            <button className="btn-secondary" onClick={alRecargar}>
              Actualizar
            </button>
          </div>
          <div className="panel-cuerpo">
            <div className="distribucion-lista">
              {porDia.map((dia) => (
                <div key={dia.etiqueta} className="distribucion-item dia">
                  <span className="distribucion-label">
                    {new Date(dia.etiqueta + 'T00:00:00').toLocaleDateString('es-CL', {
                      day: '2-digit',
                      month: 'short',
                    })}
                  </span>
                  <div className="distribucion-pista">
                    <div
                      className="distribucion-barra info"
                      style={{
                        width: maximoDiario > 0 ? `${(dia.costo_usd / maximoDiario) * 100}%` : '0%',
                      }}
                    />
                  </div>
                  <span className="distribucion-valor ancho">{montoUSD(dia.costo_usd)}</span>
                  <span className="distribucion-extra">{numero(dia.cantidad)} análisis</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Configuración vigente ── */}
      {config && (
        <div className="panel">
          <div className="panel-encabezado">
            <span className="panel-titulo">Configuración del agente</span>
          </div>
          <div className="panel-cuerpo">
            <div className="ficha-resumen sin-borde">
              <div className="ficha-dato">
                <span className="ficha-dato-label">Modelo</span>
                <span className="ficha-dato-valor">
                  <span>{config.modelo || 'sin configurar'}</span>
                </span>
              </div>
              <div className="ficha-dato">
                <span className="ficha-dato-label">Tope de tokens por respuesta</span>
                <span className="ficha-dato-valor">
                  <span>{numero(config.max_tokens)}</span>
                </span>
              </div>
              <div className="ficha-dato">
                <span className="ficha-dato-label">Precio por millón de tokens</span>
                <span className="ficha-dato-valor">
                  <span>
                    {montoUSD(config.precio_entrada_usd_millon, 2, 4)} entrada ·{' '}
                    {montoUSD(config.precio_salida_usd_millon, 2, 4)} salida
                  </span>
                </span>
              </div>
              <div className="ficha-dato">
                <span className="ficha-dato-label">Envía temperatura</span>
                <span className="ficha-dato-valor">
                  <span>{config.envia_temperatura ? 'sí' : 'no'}</span>
                </span>
              </div>
            </div>

            <p className="nota-prioridad">
              Los costos son estimaciones calculadas con los precios configurados en el
              backend. El valor que manda es el del panel de facturación del proveedor.
              La configuración se lee al arrancar el servidor: si se cambia el archivo
              .env hay que reiniciarlo para que tome efecto.
            </p>
          </div>
        </div>
      )}
    </>
  );
}

export default ConsumoIA;
