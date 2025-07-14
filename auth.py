<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>GeoProtocolos</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    * {
      font-family: 'Inter', sans-serif;
      box-sizing: border-box;
    }

    html, body {
      margin: 0;
      padding: 0;
      height: 100vh;
      overflow: hidden; /* Bloquea scroll general */
    }

    .container {
      display: flex;
      flex-direction: column;
      height: 100vh;
      padding: 20px;
      gap: 10px;
    }

    .jerarquia-section {
      height: 33vh;
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
    }

    .formulario-tabla-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .formulario-section {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 20px;
    }

    .tabla-section {
      flex: 1;
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 20px;
      display: flex;
      flex-direction: column;
    }

    .scrollable-table {
      flex: 1;
      overflow-y: auto;
    }

    table {
      border-collapse: collapse;
      width: 100%;
    }

    th, td {
      font-size: 13px;
      border: 1px solid #ccc;
      padding: 4px 8px;
      text-align: center;
      white-space: nowrap;
      resize: horizontal;
      overflow: auto;
    }

    thead th {
      position: sticky;
      top: 0;
      background-color: #e2e8f0;
      z-index: 1;
    }

    .form-select, .form-control {
      font-size: 13px;
      padding: 6px 10px;
    }

    .btn-database {
      background-color: #0ea5e9;
      color: white;
      padding: 6px 16px;
      font-size: 13px;
      border: none;
      border-radius: 6px;
      margin-top: 10px;
    }

    .btn-database:hover {
      background-color: #0284c7;
    }

    textarea.form-control {
      resize: vertical;
    }

    @media (max-width: 768px) {
      .jerarquia-section, .formulario-tabla-wrapper {
        height: auto;
      }
    }
  </style>
</head>
<body>
<div class="container">
  <div class="jerarquia-section">
    <h4>Selección Jerárquica</h4>
    <div class="row g-2">
      {% for i in range(1, 6) %}
      <div class="col-md-12">
        <select class="form-select" id="nivel{{ i }}">
          <option value="">Nivel {{ i }}</option>
        </select>
      </div>
      {% endfor %}
    </div>
  </div>

  <div class="formulario-tabla-wrapper">
    <div class="formulario-section">
      <h4>Datos del Protocolo</h4>
      <div class="row g-2">
        <div class="col-md-6"><input type="text" class="form-control" placeholder="RP"></div>
        <div class="col-md-6"><input type="text" class="form-control" placeholder="Protocolo"></div>
        <div class="col-md-6">
          <select class="form-select">
            <option value="">Estado</option>
            <option value="aprobado">Aprobado</option>
            <option value="pendiente">Pendiente</option>
            <option value="rechazado">Rechazado</option>
          </select>
        </div>
        <div class="col-md-6"><input type="text" class="form-control" placeholder="Capa"></div>
        <div class="col-md-6"><input type="text" class="form-control" placeholder="PK Inicio"></div>
        <div class="col-md-6"><input type="text" class="form-control" placeholder="PK Fin"></div>
        <div class="col-md-6">
          <select class="form-select">
            <option value="">Lado</option>
            <option value="izquierdo">Izquierdo</option>
            <option value="derecho">Derecho</option>
            <option value="completa">Completa</option>
          </select>
        </div>
        <div class="col-md-6"><input type="text" class="form-control" placeholder="Espesor"></div>
        <div class="col-md-6"><input type="text" class="form-control" placeholder="TAG"></div>
        <div class="col-md-6"><input type="date" class="form-control" placeholder="Fecha Envío"></div>
        <div class="col-md-6"><input type="date" class="form-control" placeholder="Fecha Aprobación"></div>
        <div class="col-md-12"><textarea class="form-control" rows="2" placeholder="Observaciones"></textarea></div>
      </div>
      <div class="text-end">
        <button class="btn btn-database">💾 Consolidar</button>
      </div>
    </div>

    <div class="tabla-section">
      <h4>Resumen de Protocolos</h4>
      <div class="scrollable-table">
        <table class="table table-sm">
          <thead>
          <tr>
            <th>ID</th><th>RP</th><th>Protocolo</th><th>Estado</th><th>N1</th><th>N2</th>
            <th>N3</th><th>N4</th><th>N5</th><th>PK Inicio</th><th>PK Fin</th><th>Capa</th>
            <th>Lado</th><th>Espesor</th><th>TAG</th><th>Envío</th><th>Aprobación</th><th>Obs</th>
          </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<script>
  let jerarquia = {};

  async function cargarJerarquia() {
    const response = await fetch("/jerarquia");
    jerarquia = await response.json();
    poblarSelect(jerarquia, 1);
  }

  function poblarSelect(data, nivel) {
    const select = document.getElementById(`nivel${nivel}`);
    select.innerHTML = `<option value="">Nivel ${nivel}</option>`;
    for (const codigo in data) {
      const descripcion = data[codigo]?.descripcion || "";
      const option = document.createElement("option");
      option.value = `${codigo} ${descripcion}`;
      option.textContent = `${codigo} ${descripcion}`;
      select.appendChild(option);
    }
    const sinItem = document.createElement("option");
    sinItem.value = `Sin_Item_N${nivel}`;
    sinItem.textContent = "-- No Item --";
    select.appendChild(sinItem);
    for (let i = nivel + 1; i <= 5; i++) {
      const nextSelect = document.getElementById(`nivel${i}`);
      nextSelect.innerHTML = `<option value="">Nivel ${i}</option><option value="Sin_Item_N${i}">-- No Item --</option>`;
    }
  }

  function obtenerRutaHasta(nivel) {
    let ruta = [];
    for (let i = 1; i <= nivel; i++) {
      let val = document.getElementById(`nivel${i}`).value;
      if (val && !val.startsWith("Sin_Item")) ruta.push(val.split(" ")[0]);
    }
    return ruta;
  }

  function buscarSubitems(ruta) {
    let actual = jerarquia;
    for (let cod of ruta) {
      actual = actual[cod]?.subitems || {};
    }
    return actual;
  }

  function setupEventos() {
    for (let nivel = 1; nivel < 5; nivel++) {
      const select = document.getElementById(`nivel${nivel}`);
      select.addEventListener("change", () => {
        const ruta = obtenerRutaHasta(nivel);
        const subitems = buscarSubitems(ruta);
        poblarSelect(subitems, nivel + 1);
      });
    }
  }

  document.querySelector('.btn-database').addEventListener('click', () => {
    const tbody = document.querySelector('table tbody');
    const getValue = sel => document.querySelector(sel)?.value || '';
    const getText = sel => {
      const el = document.querySelector(sel);
      return el ? el.options[el.selectedIndex]?.text || '' : '';
    };
    const data = [
      tbody.rows.length + 1,
      getValue('input[placeholder="RP"]'),
      getValue('input[placeholder="Protocolo"]'),
      getText('select.form-select:nth-of-type(1)'),
      getText('#nivel1'),
      getText('#nivel2'),
      getText('#nivel3'),
      getText('#nivel4'),
      getText('#nivel5'),
      getValue('input[placeholder="PK Inicio"]'),
      getValue('input[placeholder="PK Fin"]'),
      getValue('input[placeholder="Capa"]'),
      getText('select.form-select:nth-of-type(2)'),
      getValue('input[placeholder="Espesor"]'),
      getValue('input[placeholder="TAG"]'),
      getValue('input[type="date"]:nth-of-type(1)'),
      getValue('input[type="date"]:nth-of-type(2)'),
      document.querySelector('textarea')?.value || ''
    ];
    const row = document.createElement('tr');
    for (let val of data) {
      const td = document.createElement('td');
      td.textContent = val;
      td.contentEditable = true;
      row.appendChild(td);
    }
    tbody.appendChild(row);
  });

  cargarJerarquia();
  setupEventos();
</script>
</body>
</html>
