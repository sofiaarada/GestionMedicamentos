import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import pickle
import os
from app.database import engine

# Ruta para guardar modelos
MODELS_DIR = os.path.join(os.path.dirname(__file__), "modelos")
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

def extraer_datos_demanda():
    """
    Se conecta a la base de datos y extrae un DataFrame con el historial
    de consumo (SALIDAS) de los medicamentos.
    """
    print("Iniciando extracción de datos desde base de datos SQLite...")
    
    query = """
        SELECT 
            DATE(m.fecha_movimiento) as fecha, 
            med.nombre as medicamento, 
            m.cantidad_movimiento as cantidad_consumida
        FROM movimientos m
        JOIN lotes l ON m.id_lote = l.id_lote
        JOIN medicamentos med ON l.id_medicamento = med.id_medicamento
        WHERE m.tipo_movimiento = 'SALIDA'
        ORDER BY fecha DESC
    """
    
    try:
        # Pandas ejecuta la consulta y convierte el resultado en un DataFrame
        df = pd.read_sql(query, engine)
        
        print("✅ ¡Datos extraídos con éxito!")
        print(f"Total de registros encontrados: {len(df)}")
        print("-" * 50)
        
        # Mostramos las primeras filas para verificar
        if len(df) > 0:
            print(df.head())
        else:
            print("⚠️  No hay datos de movimientos registrados aún")
        
        return df
    
    except Exception as e:
        print(f"❌ Error al extraer los datos: {e}")
        return None

def preprocesar_datos(df):
    """
    Preprocesa los datos para el modelo de ML:
    - Agrupa por medicamento
    - Calcula estadísticas
    - Crea features
    """
    if df is None or len(df) == 0:
        print("⚠️  No hay datos para preprocesar")
        return None
    
    print("\nPreprocesando datos...")
    
    try:
        # Agrupar por medicamento y calcular estadísticas
        stats_por_medicamento = df.groupby('medicamento').agg({
            'cantidad_consumida': ['sum', 'mean', 'std', 'min', 'max', 'count']
        }).round(2)
        
        # Crear features simples
        features_data = []
        for medicamento in df['medicamento'].unique():
            datos_med = df[df['medicamento'] == medicamento]['cantidad_consumida'].values
            
            if len(datos_med) > 0:
                features_data.append({
                    'medicamento': medicamento,
                    'consumo_total': datos_med.sum(),
                    'consumo_promedio': datos_med.mean(),
                    'consumo_max': datos_med.max(),
                    'consumo_min': datos_med.min(),
                    'desv_estandar': datos_med.std() if len(datos_med) > 1 else 0,
                    'cantidad_registros': len(datos_med)
                })
        
        df_features = pd.DataFrame(features_data)
        
        print(f"✅ Datos preprocesados. {len(df_features)} medicamentos con datos")
        print(df_features.head())
        
        return df_features
    
    except Exception as e:
        print(f"❌ Error al preprocesar: {e}")
        return None

def entrenar_modelo(df_features):
    """
    Entrena un modelo de regresión para predecir demanda
    """
    if df_features is None or len(df_features) == 0:
        print("⚠️  No hay datos para entrenar el modelo")
        return None
    
    print("\nEntrenando modelo de predicción de demanda...")
    
    try:
        # Separar características y target
        X = df_features[['consumo_promedio', 'cantidad_registros']].values
        y = df_features['consumo_total'].values
        
        # Si no hay suficientes datos, usamos un modelo simple
        if len(X) < 2:
            print("⚠️  Datos insuficientes para entrenar. Usando modelo por defecto.")
            return None
        
        # Entrenar modelo Random Forest
        modelo = RandomForestRegressor(n_estimators=10, random_state=42, max_depth=5)
        modelo.fit(X, y)
        
        # Calcular score
        score = modelo.score(X, y)
        print(f"✅ Modelo entrenado exitosamente")
        print(f"R² Score: {score:.4f}")
        
        # Guardar modelo
        modelo_path = os.path.join(MODELS_DIR, "modelo_demanda.pkl")
        with open(modelo_path, 'wb') as f:
            pickle.dump(modelo, f)
        print(f"💾 Modelo guardado en: {modelo_path}")
        
        return modelo
    
    except Exception as e:
        print(f"❌ Error al entrenar modelo: {e}")
        return None

def predecir_demanda(medicamento_id, consumo_promedio, cantidad_registros):
    """
    Predice la demanda futura de un medicamento
    """
    try:
        modelo_path = os.path.join(MODELS_DIR, "modelo_demanda.pkl")
        
        if not os.path.exists(modelo_path):
            print("⚠️  Modelo no encontrado. Ejecute primero el entrenamiento.")
            return None
        
        with open(modelo_path, 'rb') as f:
            modelo = pickle.load(f)
        
        # Realizar predicción
        X_pred = np.array([[consumo_promedio, cantidad_registros]])
        prediccion = modelo.predict(X_pred)[0]
        
        return max(prediccion, 0)  # No permitir predicciones negativas
    
    except Exception as e:
        print(f"❌ Error al predecir: {e}")
        return None

def pipeline_completo():
    """
    Ejecuta todo el pipeline de ML: extracción, preprocesamiento y entrenamiento
    """
    print("=" * 60)
    print("INICIANDO PIPELINE DE MACHINE LEARNING")
    print("=" * 60)
    
    # 1. Extrae datos
    df = extraer_datos_demanda()
    
    if df is None or len(df) == 0:
        print("\n⚠️  Pipeline finalizado: No hay datos para procesar")
        return False
    
    # 2. Preprocesa
    df_features = preprocesar_datos(df)
    
    if df_features is None or len(df_features) == 0:
        print("\n⚠️  Pipeline finalizado: No hay features para entrenar")
        return False
    
    # 3. Entrena modelo
    modelo = entrenar_modelo(df_features)
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETADO ✅")
    print("=" * 60)
    
    return True

def generar_datos_prueba():
    """
    Genera datos de prueba para demostrar el funcionamiento del ML
    Crea medicamentos, lotes y movimientos ficticios
    """
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.models import Categoria, Medicamento, Lote, Usuario, Movimiento
    from datetime import datetime, timedelta
    import random
    
    print("\n🔄 Generando datos de prueba...")
    
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        medicamentos_existentes = db.query(Medicamento).count()
        if medicamentos_existentes > 0:
            print("✅ La base de datos ya contiene datos")
            return True
        
        # Crear categoría
        categoria = Categoria(nombre="Analgésicos")
        db.add(categoria)
        db.flush()
        
        # Crear medicamentos
        medicamentos = [
            Medicamento(nombre="Paracetamol 500mg", id_categoria=categoria.id_categoria, 
                       unidad_medida="Tabletas", stock_minimo_alerta=20),
            Medicamento(nombre="Ibuprofeno 200mg", id_categoria=categoria.id_categoria, 
                       unidad_medida="Tabletas", stock_minimo_alerta=15),
            Medicamento(nombre="Aspirina 100mg", id_categoria=categoria.id_categoria, 
                       unidad_medida="Tabletas", stock_minimo_alerta=25)
        ]
        
        for med in medicamentos:
            db.add(med)
        db.flush()
        
        # Crear usuario
        usuario = Usuario(nombre="Admin", cargo="Administrador", 
                         correo="admin@medicamentos.com", password="admin123")
        db.add(usuario)
        db.flush()
        
        # Crear lotes y movimientos
        for med in medicamentos:
            lote = Lote(
                id_medicamento=med.id_medicamento,
                cantidad_inicial=500,
                cantidad_actual=500,
                fecha_entrada=datetime.now().date(),
                fecha_vencimiento=(datetime.now() + timedelta(days=365)).date()
            )
            db.add(lote)
            db.flush()
            
            # Crear movimientos de prueba (salidas)
            for i in range(10):
                movimiento = Movimiento(
                    id_lote=lote.id_lote,
                    id_usuario=usuario.id_usuario,
                    tipo_movimiento='SALIDA',
                    motivo_movimiento='Dispensación',
                    cantidad_movimiento=random.randint(5, 20),
                    fecha_movimiento=datetime.now() - timedelta(days=random.randint(0, 30))
                )
                db.add(movimiento)
        
        db.commit()
        print("✅ Datos de prueba generados exitosamente")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al generar datos de prueba: {e}")
        return False
    finally:
        db.close()

# Bloque de prueba: Esto solo se ejecuta si corremos este archivo directamente
if __name__ == "__main__":
    # Generar datos de prueba si es necesario
    generar_datos_prueba()
    
    # Ejecutar pipeline completo
    pipeline_completo()