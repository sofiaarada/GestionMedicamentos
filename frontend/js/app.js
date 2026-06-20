const API_URL = "http://127.0.0.1:8000";

const txtTotalMedicamentos = document.getElementById("txtTotalMedicamentos");
const txtStockCritico = document.getElementById("txtStockCritico");
const txtProximosVencer = document.getElementById("txtProximosVencer");

if (txtTotalMedicamentos && txtStockCritico && txtProximosVencer) {
    const cargarMetricasDashboard = async () => {
        try {
            // Solicitamos el resumen analítico al backend
            const response = await fetch(`${API_URL}/analytics/summary`);
            
            if (response.ok) {
                const data = await response.json(); // Nuestro JSON ligero
                
                txtTotalMedicamentos.innerText = data.total_medicamentos;
                txtStockCritico.innerText = data.stock_critico;
                txtProximosVencer.innerText = data.proximos_vencer;
            } else {
                console.error("Error al obtener las métricas del servidor.");
                txtTotalMedicamentos.innerText = "Error";
                txtStockCritico.innerText = "Error";
                txtProximosVencer.innerText = "Error";
            }
        } catch (error) {
            console.error("Error de red intentando cargar métricas:", error);
            txtTotalMedicamentos.innerText = "-";
            txtStockCritico.innerText = "-";
            txtProximosVencer.innerText = "-";
        }
    };

    cargarMetricasDashboard();
}


const btnProbarAPI = document.getElementById("btnProbarAPI");

if (btnProbarAPI) {
    btnProbarAPI.addEventListener("click", async () => {
        try {
            const response = await fetch(`${API_URL}/`);
            const data = await response.json(); 
            
            alert(`¡Éxito! El servidor dice: ${data.mensaje}`);
        } catch (error) {
            alert("Error: No se pudo conectar a la API. ¿Está encendido uvicorn?");
            console.error("Detalles del error:", error);
        }
    });
}

const formMedicamento = document.getElementById("formMedicamento");

if (formMedicamento) {
    formMedicamento.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const nuevoMedicamento = {
            nombre: document.getElementById("nombreInput").value,
            unidad_medida: document.getElementById("unidadInput").value,
            id_categoria: parseInt(document.getElementById("categoriaInput").value) 
        };

        try {
            const response = await fetch(`${API_URL}/medicamentos/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json" 
                },
                body: JSON.stringify(nuevoMedicamento)
            });

            if (response.ok) {
                alert("¡Medicamento guardado con éxito en la base de datos!");
                formMedicamento.reset(); 
            } else {
                const errorData = await response.json();
                alert(`Error al guardar: ${errorData.detail}`);
            }
        } catch (error) {
            alert("Error de red. Verifica la conexión con el servidor.");
            console.error(error);
        }
    });
}

const tablaMovimientosBody = document.getElementById("tablaMovimientosBody");

if (tablaMovimientosBody) {
    const cargarMovimientos = async () => {
        try {

            const response = await fetch(`${API_URL}/movimientos/`);
            
            if (response.ok) {
                const movimientos = await response.json(); 
                tablaMovimientosBody.innerHTML = "";
            
                if (movimientos.length === 0) {
                    tablaMovimientosBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No hay movimientos registrados.</td></tr>`;
                    return;
                }

                movimientos.forEach(mov => {
                    const fechaFormateada = new Date(mov.fecha_movimiento).toLocaleString();
                    
                    const badgeClass = mov.tipo_movimiento === 'ENTRADA' ? 'bg-success' : 'bg-danger';

                    const filaHTML = `
                        <tr>
                            <td>${mov.id_movimiento}</td>
                            <td><span class="badge ${badgeClass}">${mov.tipo_movimiento}</span></td>
                            <td>${mov.motivo_movimiento}</td>
                            <td>${mov.cantidad_movimiento}</td>
                            <td>${fechaFormateada}</td>
                        </tr>
                    `;
                    tablaMovimientosBody.innerHTML += filaHTML;
                });
            } else {
                tablaMovimientosBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error al cargar los datos del servidor.</td></tr>`;
            }
        } catch (error) {
            console.error("Error fetching movimientos:", error);
            tablaMovimientosBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error de red. Asegúrate de que FastAPI esté corriendo.</td></tr>`;
        }
    };
    cargarMovimientos();
}

// ==========================================
// LÓGICA VISTA 4: PREDICCIONES DE MACHINE LEARNING
// ==========================================
const btnPredecir = document.getElementById("btnPredecir");
const resultadoPrediccion = document.getElementById("resultadoPrediccion");

if (btnPredecir) {
    btnPredecir.addEventListener("click", async () => {
        const idMedicamento = document.getElementById("inputPredictId").value;
        
        if (!idMedicamento) {
            alert("Por favor, ingresa el ID de un medicamento.");
            return;
        }

        // Cambiar el botón a estado de "Cargando"
        btnPredecir.innerText = "Calculando...";
        btnPredecir.disabled = true;

        try {
            // Hacemos la petición GET a nuestro endpoint de predicción
            const response = await fetch(`${API_URL}/predicciones/${idMedicamento}`);
            const data = await response.json();

            if (response.ok) {
                // Llenamos la tarjeta con los datos de la IA
                document.getElementById("resNombre").innerText = data.medicamento;
                document.getElementById("resCantidad").innerText = data.prediccion_proximo_mes;
                document.getElementById("resConfianza").innerText = `Precisión del modelo: ${data.confianza}`;
                
                // Mostramos la tarjeta (quitando la clase d-none de Bootstrap)
                resultadoPrediccion.classList.remove("d-none");
                resultadoPrediccion.classList.remove("bg-danger");
                resultadoPrediccion.classList.add("bg-success");
            } else {
                // Si hay error (ej. Medicamento no encontrado o sin datos)
                document.getElementById("resNombre").innerText = "Error";
                document.getElementById("resCantidad").innerText = "-";
                document.getElementById("resConfianza").innerText = data.detail || data.mensaje;
                
                resultadoPrediccion.classList.remove("d-none");
                resultadoPrediccion.classList.remove("bg-success");
                resultadoPrediccion.classList.add("bg-danger");
            }
        } catch (error) {
            alert("Error de conexión con el servidor de IA.");
            console.error(error);
        } finally {
            // Restaurar el botón
            btnPredecir.innerText = "Consultar IA";
            btnPredecir.disabled = false;
        }
    });
}