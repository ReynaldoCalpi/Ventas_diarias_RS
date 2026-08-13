import streamlit as st
import pandas as pd
import pdfplumber
import io

# Configuración de página optimizada para visualización limpia
st.set_page_config(
    page_title="Control de Ventas - Supermercado",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo visual amigable y tipografía clara para lectura rápida
st.markdown("""
    <style>
        .main-title { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; }
        .sub-title { font-size: 1.1rem; color: #4B5563; }
        .metric-card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

def extraer_datos_pdf(archivo_pdf):
    """
    Función base para procesar el PDF del libro de ventas.
    Extrae texto/tablas estructuradas según el estándar de reportes fiscales.
    """
    datos = []
    with pdfplumber.open(archivo_pdf) as pdf:
        for pagina in pdf.pages:
            tabla = pagina.extract_table()
            if tabla:
                datos.extend(tabla)
    
    if datos:
        # Convertir a DataFrame asumiendo estructura estándar de libro fiscal
        df = pd.DataFrame(datos[1:], columns=datos[0] if len(datos) > 0 else None)
        return df
    return pd.DataFrame()

def main():
    st.markdown('<p class="main-title">📈 Control Diario de Ventas</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Resumen financiero actualizado para la toma de decisiones gerenciales.</p>', unsafe_allow_html=True)
    st.divider()

    # Sección de Carga de Archivos (Fácil e intuitivo)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛒 Consumidor Final")
        pdf_cf = st.file_uploader("Subir PDF de Consumidores Finales", type=["pdf"], key="cf")
        
    with col2:
        st.subheader("🏢 Créditos Fiscales")
        pdf_ccf = st.file_uploader("Subir PDF de Créditos Fiscales", type=["pdf"], key="ccf")

    st.divider()

    # Simulación de visualización ejecututiva (Se conectará con la extracción real en la siguiente iteración)
    st.markdown("### 📊 Resultados Acumulados del Mes")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Venta Total Acumulada", value="$0.00", delta="Actualizado hoy")
    with m2:
        st.metric(label="Consumidor Final", value="$0.00", delta="0.0%")
    with m3:
        st.metric(label="Créditos Fiscales", value="$0.00", delta="0.0%")

    # Área de validación de datos cargados
    if pdf_cf or pdf_ccf:
        st.info("Archivo(s) detectado(s). Procesando información para mostrar el consolidado diario...")
        if pdf_cf:
            df_resultado = extraer_datos_pdf(pdf_cf)
            if not df_resultado.empty:
                st.write("Vista previa de datos extraídos (Consumidor Final):")
                st.dataframe(df_resultado.head(5), use_container_width=True)
    else:
        st.warning("⚠️ Por favor, suba al menos un reporte en PDF para comenzar a visualizar las ventas.")

if __name__ == "__main__":
    main()