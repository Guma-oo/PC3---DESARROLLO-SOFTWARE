const API_URL = "http://127.0.0.1:8000";

document.getElementById('form-crear').addEventListener('submit', async (e) => {
    e.preventDefault();
    const titulo = document.getElementById('titulo').value;
    const contenido = document.getElementById('contenido').value;

    await fetch(`${API_URL}/iniciativas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo, contenido })
    });
    
    document.getElementById('form-crear').reset();
    cargarIniciativas();
});

async function cargarIniciativas() {
    const res = await fetch(`${API_URL}/iniciativas`);
    const iniciativas = await res.json();
    const contenedor = document.getElementById('lista-iniciativas');
    contenedor.innerHTML = '';

    iniciativas.forEach(ini => {
        const adjuntosHTML = ini.adjuntos.map(ruta => {
            const nombreLimpio = ruta.split('_').slice(1).join('_') || ruta;
            return `<a href="${API_URL}/${ruta}" target="_blank" class="doc-adjunto" style="text-decoration:none; color:#2980b9;">📄 ${nombreLimpio}</a>`;
        }).join(" ") || "Ninguno";

        const div = document.createElement('div');
        div.className = 'tarjeta-iniciativa';
        div.innerHTML = `
            <h3>${ini.titulo} <span class="badge">${ini.estado}</span></h3>
            <pre style="white-space: pre-wrap; font-family: inherit;">${ini.contenido}</pre>
            <p><strong>Firmas:</strong> ${ini.firmas} / 5</p>
            <p><strong>Documentos Soporte:</strong> ${adjuntosHTML}</p>
            <p><strong>Comentarios:</strong> ${ini.comentarios.join(" | ") || "Ninguno"}</p>
            <div class="acciones">
                <button onclick="firmar('${ini.id}')">Firmar</button>
                
                <input type="text" id="comentario-${ini.id}" placeholder="Escribe un comentario...">
                <button onclick="comentar('${ini.id}')">Comentar</button>
                
                <input type="file" id="adjunto-${ini.id}" style="width: 45%; padding: 0.5rem; margin-bottom: 0;">
                <button onclick="adjuntar('${ini.id}')" style="background:#d35400;">Subir Recurso</button>
                
                <button onclick="enviar('${ini.id}')" style="background:#8e44ad; width: 100%; margin-top: 10px;">Enviar a Congreso</button>
            </div>
        `;
        contenedor.appendChild(div);
    });
}

async function firmar(id) {
    const res = await fetch(`${API_URL}/firmar/${id}`, { method: 'POST' });
    if (!res.ok) alert((await res.json()).detail);
    cargarIniciativas();
}

async function comentar(id) {
    const texto = document.getElementById(`comentario-${id}`).value;
    if (!texto) return;
    const res = await fetch(`${API_URL}/comentar/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto })
    });
    if (!res.ok) alert((await res.json()).detail);
    cargarIniciativas();
}

async function adjuntar(id) {
    const fileInput = document.getElementById(`adjunto-${id}`);
    
    if (fileInput.files.length === 0) {
        alert("Por favor selecciona un archivo de tu computadora.");
        return;
    }
    
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);


    const res = await fetch(`${API_URL}/adjuntar/${id}`, {
        method: 'POST',
        body: formData
    });
    
    if (!res.ok) alert((await res.json()).detail);
    cargarIniciativas();
}

async function enviar(id) {
    const res = await fetch(`${API_URL}/enviar/${id}`, { method: 'POST' });
    if (!res.ok) alert((await res.json()).detail);
    cargarIniciativas();
}

cargarIniciativas();