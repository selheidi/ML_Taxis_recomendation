import pandas as pd
from fastapi import FastAPI
import uvicorn 
#instanciar la aplicación

app = FastAPI()

# DataFrame que se utiliza en las funciones de la API
df = pd.read_csv('demanda_taxi_amarillo_pronostrico4dias_contaminacion_aire_NYC.csv')

@app.get("/")
async def read_root():
    return {"message": "Hello, this is the root endpoint!"}

@app.get("/recomendacion/{recomendacion}", name="Recomendacion")
async def sugerir_mejor_momento(inicio_horario: int, fin_horario: int, zona_partida: str, zona_destino: str):
    """
    La siguiente función retorna una recomendacion de día y horario de viaje para viajar de forma más ecológica, rápida y con menos contaminación atmosférica.
    """
    try:
        # Filtrar por rango horario y zonas de partida y destino
        filtro_rango_horario = df['hour_of_day'].between(inicio_horario, fin_horario)
        filtro_partida = (df['Partida_Zone'] == zona_partida)
        filtro_destino = (df['Destino_Zone'] == zona_destino)

        # Filtrar por categorías específicas de calidad del aire
        categorias_calidad_aire = ['Very Good', 'Good', 'Moderate']
        filtro_calidad_aire = df['Air_Quality_Index_(aqi)'].isin(categorias_calidad_aire)

        viajes_filtrados = df[filtro_rango_horario & filtro_partida & filtro_destino & filtro_calidad_aire]

        # Agrupar por día de la semana, rango horario y categoría de calidad del aire
        resumen = viajes_filtrados.groupby(['day_of_week', 'hour_of_day', 'Air_Quality_Index_(aqi)']).agg({
            'count': 'mean'
        }).reset_index()

        # Encontrar el momento con la demanda más baja y mejor calidad del aire
        mejor_momento = resumen.loc[resumen['count'].idxmin()]

        return {
            'zona_partida': zona_partida,
            'zona_destino': zona_destino,
            'dia_semana': mejor_momento['day_of_week'],
            'hora_dia': mejor_momento['hour_of_day'],
            'calidad_aire': mejor_momento['Air_Quality_Index_(aqi)'],
            'demanda_promedio': float(mejor_momento['count'])
        }
    except Exception as e:
        return {"error": str(e)}
