const API_URL = "http://127.0.0.1:8000";

// =============================================
// FUNCIONES GLOBALES
// =============================================

function mostrarAlerta(tipo, titulo, mensaje) {
    const alerta = document.getElementById("alertaEntrenamiento");
    const tituloAlerta = document.getElementById("tituloAlerta");
    const textoAlerta = document.getElementById("textoAlerta");
    
    alerta.className = `alert alert-${tipo} d-block`;
    tituloAlerta.innerText = titulo + ":";
    textoAlerta.innerText = mensaje;
}

// =============================================
// ENTRENAR MODELO
// =============================================

const btnEntrenarModelo = document.getElementById("btnEntrenarModelo");

if (btnEntrenarModelo) {
    btnEntrenarModelo.addEventListener("click", async () => {
        btnEntrenarModelo.disabled = true;
        btnEntrenarModelo.innerText = "Entrenando...";

        try {
            const response = await fetch(`${API_URL}/predicciones/entrenar`);
            const data = await response.json();

            if (response.ok) {
                mostrarAlerta("success", "Éxito", `${data.mensaje} - Modelo: ${data.modelo}`);
                // Recargar predicciones
                cargarReportePredicciones();
            } else {
                mostrarAlerta("warning", "⚠️ Advertencia", data.mensaje);
            }
        } catch (error) {
            mostrarAlerta("danger", "Error", "No se pudo conectar al servidor");
            console.error(error);
        } finally {
            btnEntrenarModelo.disabled = false;
            btnEntrenarModelo.innerText = "Entrenar Modelo";
        }
    });
}

// =============================================
// CARGAR REPORTE DE PREDICCIONES
// =============================================

async function cargarReportePredicciones() {
    try {
        console.log("Iniciando carga de reporte...");
        const response = await fetch(`${API_URL}/predicciones/reporte`);
        console.log("Response status:", response.status);
        
        const data = await response.json();
        console.log("Data recibida:", data);

        const contenedor = document.getElementById("contenedorPredicciones");
        contenedor.innerHTML = "";

        if (data.total_medicamentos === 0) {
            contenedor.innerHTML = `
                <div class="col-12 text-center text-muted">
                    <p>No hay medicamentos con predicciones disponibles</p>
                </div>
            `;
            return;
        }

        data.medicamentos.forEach(med => {
            const tarjeta = document.createElement("div");
            tarjeta.className = "col-md-6 col-lg-4 mb-3";
            tarjeta.innerHTML = `
                <div class="card card-prediccion h-100">
                    <div class="card-body">
                        <h5 class="card-title">${med.medicamento}</h5>
                        <div class="mb-3">
                            <span class="badge badge-prediccion bg-success">
                                Predicción: ${med.prediccion_proximos_30_dias} unidades
                            </span>
                        </div>
                        <small class="text-muted d-block">
                             Consumo histórico (30 días): ${med.consumo_historico_30_dias} unidades<br>
                             Promedio diario: ${med.consumo_promedio} unidades<br>
                             Registros: ${med.registros}
                        </small>
                    </div>
                </div>
            `;
            contenedor.appendChild(tarjeta);
        });

    } catch (error) {
        console.error("Error cargando reporte:", error);
        const contenedor = document.getElementById("contenedorPredicciones");
        contenedor.innerHTML = `
            <div class="col-12 text-center text-danger">
                <p>Error al cargar las predicciones: ${error.message}</p>
            </div>
        `;
    }
}

// =============================================
// CARGAR MEDICAMENTOS PARA SELECTOR
// =============================================

async function cargarMedicamentosSelector() {
    try {
        const response = await fetch(`${API_URL}/medicamentos/`);
        const medicamentos = await response.json();

        const select = document.getElementById("selectMedicamento");
        select.innerHTML = '<option selected disabled>Selecciona un medicamento...</option>';

        medicamentos.forEach(med => {
            const option = document.createElement("option");
            option.value = JSON.stringify({
                id: med.id_medicamento,
                nombre: med.nombre,
                unidad: med.unidad_medida
            });
            option.innerText = med.nombre;
            select.appendChild(option);
        });

    } catch (error) {
        console.error("Error cargando medicamentos:", error);
    }
}

// =============================================
// PREDICCIÓN INDIVIDUAL
// =============================================

const btnPredecirIndividual = document.getElementById("btnPredecirIndividual");

if (btnPredecirIndividual) {
    btnPredecirIndividual.addEventListener("click", async () => {
        const select = document.getElementById("selectMedicamento");
        const valor = select.value;

        if (!valor) {
            alert("Por favor selecciona un medicamento");
            return;
        }

        try {
            const medicamento = JSON.parse(valor);
            
            // Obtener datos del medicamento desde el reporte
            const responseReporte = await fetch(`${API_URL}/predicciones/reporte`);
            const reporte = await responseReporte.json();
            
            const medData = reporte.medicamentos.find(m => m.medicamento_id === medicamento.id);
            
            if (!medData) {
                alert("No hay datos de predicción para este medicamento");
                return;
            }

            // Mostrar resultado
            const resultado = document.getElementById("resultadoIndividual");
            document.getElementById("nombreMedIndividual").innerText = medicamento.nombre;
            document.getElementById("prediccionIndividual").innerText = `${medData.prediccion_proximos_30_dias} ${medicamento.unidad}`;
            document.getElementById("consumoHistorico").innerText = `${medData.consumo_historico_30_dias} ${medicamento.unidad}`;
            document.getElementById("promedioIndividual").innerText = `${medData.consumo_promedio} ${medicamento.unidad}/día`;
            
            resultado.className = "alert alert-success d-block";

        } catch (error) {
            alert("Error al obtener la predicción");
            console.error(error);
        }
    });
}

// =============================================
// CARGAR AL INICIO
// =============================================

window.addEventListener("load", () => {
    cargarReportePredicciones();
    cargarMedicamentosSelector();
});
