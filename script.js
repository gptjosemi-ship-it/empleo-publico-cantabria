async function cargarDatos() {
  const contenedor = document.getElementById("resultados");
  contenedor.innerHTML = "Cargando convocatorias...";

  try {
    const respuesta = await fetch("datos.json");
    const datos = await respuesta.json();

contenedor.innerHTML = "";

// === FILTRO DE FECHAS ===
const filtro = document.getElementById("filtroFecha")?.value || "todas";
const hoy = new Date();

let datosFiltrados = datos;

if (filtro === "1mes") {
  datosFiltrados = datos.filter(item => {
    const fecha = new Date(item.fecha);
    return (hoy - fecha) / (1000 * 60 * 60 * 24) <= 30;
  });
}

if (filtro === "6meses") {
  datosFiltrados = datos.filter(item => {
    const fecha = new Date(item.fecha);
    return (hoy - fecha) / (1000 * 60 * 60 * 24) <= 180;
  });
}

// === MOSTRAR RESULTADOS ===
datosFiltrados.forEach(item => {

      contenedor.innerHTML += `
        <p>
          <strong>${item.titulo}</strong><br>
          ${item.entidad} – ${item.fecha}<br>
          <a href="${item.enlace}" target="_blank">Ver convocatoria</a>
        </p>
      `;
    });
  } catch (error) {
    contenedor.innerHTML = "Error al cargar los datos.";
  }
}

