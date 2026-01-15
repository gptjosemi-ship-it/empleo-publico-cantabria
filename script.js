async function cargarDatos() {
  const contenedor = document.getElementById("resultados");
  const filtro = document.getElementById("filtroFecha").value;

  contenedor.innerHTML = "Cargando convocatorias...";

  try {
    const respuesta = await fetch("datos.json");
    const datos = await respuesta.json();

    contenedor.innerHTML = "";

    const hoy = new Date();

    datos.forEach(item => {
      const fechaConvocatoria = new Date(item.fecha);
      const diferenciaDias = (hoy - fechaConvocatoria) / (1000 * 60 * 60 * 24);
        (hoy.getFullYear() - fechaConvocatoria.getFullYear()) * 12 +
        (hoy.getMonth() - fechaConvocatoria.getMonth());

      // APLICAR FILTRO
      if (
  filtro === "todas" ||
  (filtro === "1" && diferenciaDias <= 30) ||
  (filtro === "6" && diferenciaDias <= 180)
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

