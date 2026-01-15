async function cargarDatos() {
  const contenedor = document.getElementById("resultados");
  contenedor.innerHTML = "Cargando convocatorias...";

  const filtro = document.getElementById("filtroFecha").value;
  const hoy = new Date();

  try {
    const respuesta = await fetch("datos.json");
    const datos = await respuesta.json();

    contenedor.innerHTML = "";

    datos.forEach(item => {
      const fechaItem = new Date(item.fecha);
      const diferenciaDias = (hoy - fechaItem) / (1000 * 60 * 60 * 24);

      if (
        filtro === "todas" ||
        (filtro === "1mes" && diferenciaDias <= 30) ||
        (filtro === "6meses" && diferenciaDias <= 180)
      ) {
        contenedor.innerHTML += `
          <p>
            <strong>${item.titulo}</strong><br>
            ${item.entidad} – ${item.fecha}<br>
            <a href="${item.enlace}" target="_blank">Ver convocatoria</a>
          </p>
        `;
      }
    });
  } catch (error) {
    contenedor.innerHTML = "Error al cargar los datos.";
  }
}

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

