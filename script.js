async function cargarDatos() {
const contenedor = document.getElementById('resultados');
contenedor.innerHTML = 'Cargando datos oficiales...';


// Simulación inicial (luego se sustituye por datos reales)
const datos = [
{
titulo: 'Bolsa de Técnico en Educación Infantil',
fecha: '2026-01-05',
entidad: 'Ayuntamiento de Santander',
enlace: 'https://www.santander.es'
}
];


contenedor.innerHTML = '';
datos.forEach(item => {
contenedor.innerHTML += `
<p><strong>${item.titulo}</strong><br>
${item.entidad} – ${item.fecha}<br>
<a href="${item.enlace}" target="_blank">Ver convocatoria</a></p>
`;
});
}
