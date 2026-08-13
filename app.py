import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(
    page_title="Control Diario de Ventas",
    page_icon="📊",
    layout="wide"
)

def extraer_texto_pdf(archivo_pdf):
    """Extrae todo el texto línea por línea para analizar la estructura real del reporte fiscal."""
    texto_completo = []
    try:
        with pdfplumber.open(archivo_pdf) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    texto_completo.append(f"--- PÁGINA {i+1} ---\n" + texto)
        return "\n".join(texto_completo)
    except Exception as e:
        return f"Error leyendo el PDF: {e}"

def main():
    st.title("📈 Control Diario de Ventas - Supermercado")
    st.markdown("Panel gerencial para la lectura de Libros de Ventas.")
    st.divider()

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛒 Consumidor Final")
        pdf_cf = st.file_uploader("Subir PDF Consumidor Final", type=["pdf"], key="cf")
        
    with col2:
        st.subheader("🏢 Créditos Fiscales")
        pdf_ccf = st.file_uploader("Subir PDF Créditos Fiscales", type=["pdf"], key="ccf")

    st.divider()

    if pdf_cf:
        st.info("Analizando estructura del PDF de Consumidor Final...")
        
        # 1. Intentar extracción por tabla tradicional
        df_tabla = None
        try:
            with pdfplumber.open(pdf_cf) as pdf:
                tablas = []
                for pagina in pdf.pages:
                    t = pagina.extract_table()
                    if t:
                        tablas.extend(t)
                if tablas:
                    df_tabla = pd.DataFrame(tablas[1:], columns=tablas[0]).fillna("").astype(str)
        except Exception:
            pass

        if df_tabla is not None and not df_tabla.empty:
            st.success("¡Tabla detectada automáticamente!")
            st.dataframe(df_tabla, use_container_width=True)
        else:
            st.warning("⚠️ El PDF no tiene una estructura de tabla formal legible por coordenadas. Mostrando modo diagnóstico de texto:")
            
            # Mostrar texto bruto para entender cómo viene estructurado el reporte fiscal
            texto_bruto = extraer_texto_pdf(pdf_cf)
            st.text_area("Texto extraído del PDF (Copia un fragmento si necesitas ayuda para adaptarlo):", texto_bruto, height=300)
            
            st.info("💡 **Recomendación de Arquitectura:** Si este reporte no se deja leer como tabla, lo ideal será habilitar también la opción de subir archivos en formato **Excel (.xlsx)** si tu sistema contable te lo permite exportar directamente.")

if __name__ == "__main__":
    main()
