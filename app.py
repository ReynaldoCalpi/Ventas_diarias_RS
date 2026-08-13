import streamlit as st
import pandas as pd
import pdfplumber

# Configuración inicial de la página
st.set_page_config(
    page_title="Control Diario de Ventas",
    page_icon="📊",
    layout="wide"
)

def extraer_datos_pdf(archivo_pdf):
    """Extrae tablas de un PDF, limpia nulos y formatea como texto seguro para la UI."""
    try:
        with pdfplumber.open(archivo_pdf) as pdf:
            datos = []
            for pagina in pdf.pages:
                tabla = pagina.extract_table()
                if tabla:
                    datos.extend(tabla)
        
        if not datos:
            return None
        
        # Crear DataFrame usando la primera fila como cabecera si es coherente, 
        # o construirlo de forma tabular estándar
        df = pd.DataFrame(datos[1:], columns=datos[0])
        
        # Limpieza estricta: rellenar nulos y convertir todo el DataFrame a string 
        # para evitar por completo problemas de serialización JSON en st.dataframe
        df = df.fillna("").astype(str)
        # Reemplazar strings literales de "nan" o "None" por vacíos
        df = df.replace(to_replace=["nan", "None", "NoneType"], value="")
        
        return df
    except Exception as e:
        st.error(f"Error procesando el PDF: {e}")
        return None

def main():
    st.title("📈 Control Diario de Ventas - Supermercado")
    st.markdown("Panel gerencial para la lectura de Libros de Ventas (Consumidor Final y Créditos Fiscales).")
    st.divider()

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛒 Consumidor Final")
        pdf_cf = st.file_uploader("Subir PDF Consumidor Final", type=["pdf"], key="cf")
        
    with col2:
        st.subheader("🏢 Créditos Fiscales")
        pdf_ccf = st.file_uploader("Subir PDF Créditos Fiscales", type=["pdf"], key="ccf")

    st.divider()

    # Procesamiento del archivo de Consumidor Final
    if pdf_cf:
        st.info("Procesando Consumidor Final...")
        df_cf = extraer_datos_pdf(pdf_cf)
        if df_cf is not None and not df_cf.empty:
            st.success("¡Archivo procesado exitosamente!")
            st.write("Vista previa de datos extraídos:")
            st.dataframe(df_cf, use_container_width=True)
        else:
            st.warning("No se pudieron extraer tablas válidas del archivo de Consumidor Final.")

    # Procesamiento del archivo de Crédito Fiscal
    if pdf_ccf:
        st.info("Procesando Créditos Fiscales...")
        df_ccf = extraer_datos_pdf(pdf_ccf)
        if df_ccf is not None and not df_ccf.empty:
            st.success("¡Archivo procesado exitosamente!")
            st.write("Vista previa de datos extraídos:")
            st.dataframe(df_ccf, use_container_width=True)
        else:
            st.warning("No se pudieron extraer tablas válidas del archivo de Créditos Fiscales.")

if __name__ == "__main__":
    main()
