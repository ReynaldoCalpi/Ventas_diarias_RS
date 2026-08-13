import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard RI Consultores", layout="wide")

# Inicialización de carpeta de datos
if not os.path.exists('data'):
    os.makedirs('data')

def cargar_historico():
    """Combina todos los archivos procesados en la carpeta /data."""
    archivos = [f for f in os.listdir('data') if f.endswith('.csv')]
    if not archivos: return pd.DataFrame()
    return pd.concat([pd.read_csv(f'data/{f}') for f in archivos])

def main():
    # 1. Sistema de "Acceso" (Muy sencillo)
    modo = st.sidebar.radio("Navegación", ["Dashboard Gerencial", "Admin: Carga de Datos"])

    if modo == "Admin: Carga de Datos":
        st.sidebar.header("🔑 Acceso Administrador")
        file_move = st.file_uploader("Entrada de Diario (move.xlsx)", type=["xlsx"])
        file_line = st.file_uploader("Líneas de Diario (line.xlsx)", type=["xlsx"])
        mes_archivo = st.text_input("Nombre del mes (ej: Agosto_2026)")
        
        if st.button("Procesar y Guardar"):
            df = pd.merge(pd.read_excel(file_line), pd.read_excel(file_move), on='Número')
            df.to_csv(f'data/{mes_archivo}.csv', index=False)
            st.success(f"Datos de {mes_archivo} guardados.")

    else:
        st.title("📊 Dashboard Gerencial - RI Consultores")
        df_hist = cargar_historico()
        
        if df_hist.empty:
            st.warning("No hay datos históricos cargados. Contacte al admin.")
        else:
            # Comparativa Mensual
            st.subheader("📈 Comparativa Mensual de Ventas")
            ventas_mensuales = df_hist.groupby('Mes')['Total Facturado'].sum().reset_index()
            fig = px.bar(ventas_mensuales, x='Mes', y='Total Facturado', title="Ventas por Mes")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
