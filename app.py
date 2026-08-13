import streamlit as st
import pandas as pd
import pdfplumber

# Configuración inicial
st.set_page_config(page_title="Control de Ventas", layout="wide")

def extraer_datos_pdf(archivo_pdf):
    """Extrae tablas de un PDF y devuelve un DataFrame limpio."""
    try:
        with pdfplumber.open(archivo_pdf) as pdf:
            datos = []
            for pagina in pdf.pages:
                tabla = pagina.extract_table()
                if tabla:
                    datos.extend(tabla)
        
        if not datos:
            return None
        
        # Crear DF y limpiar NaN
        df = pd.DataFrame(datos[1:], columns=datos[0])
        return df.fillna("")
    except Exception as e:
        st.error(f"Error procesando el PDF: {e}")
        return None

def main():
    st.title("📈 Control Diario de Ventas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pdf_cf = st.file_uploader("Subir PDF Consumidor Final", type=["pdf"])
        
    with col2:
        pdf_ccf = st.file_uploader("Subir PDF Créditos Fiscales", type=["pdf"])

    st.divider()

    # Procesamiento
    if pdf_cf:
        st.write("Procesando Consumidor Final...")
        df = extraer_datos_pdf(pdf_cf)
        if df is not None:
            st.success("Archivo procesado exitosamente")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No se pudieron extraer tablas del archivo.")

if __name__ == "__main__":
    main()
