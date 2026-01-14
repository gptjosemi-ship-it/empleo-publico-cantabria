async function cargarDatos() {
  const contenedor = document.getElementById("resultados");
  contenedor.innerHTML = "Cargando convocatorias...";

  try {
    const respuesta = await fetch("datos.json");
    const datos = await respuesta.json();

    contenedor.innerHTML = "";

    datos.forEach(item => {
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

