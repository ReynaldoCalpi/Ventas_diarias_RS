import streamlit as st
import pandas as pd
import pdfplumber

# ... (mantener configuraciones iniciales)

def extraer_datos_pdf(archivo_pdf):
    datos = []
    with pdfplumber.open(archivo_pdf) as pdf:
        for pagina in pdf.pages:
            tabla = pagina.extract_table()
            if tabla:
                datos.extend(tabla)
    
    if datos:
        df = pd.DataFrame(datos[1:], columns=datos[0])
        
        # Limpieza crítica: Convertir NaN a None para evitar errores de serialización JSON
        df = df.where(pd.notnull(df), None)
        return df
    return pd.DataFrame()

def main():
    # ... (mantener el resto del código igual)
    
    # Dentro del bloque donde procesas el archivo:
    if pdf_cf:
        df_resultado = extraer_datos_pdf(pdf_cf)
        if not df_resultado.empty:
            st.write("Vista previa de datos extraídos:")
            # Se añade un manejo seguro antes de renderizar
            st.dataframe(df_resultado.fillna(""), use_container_width=True)
            
            # Cálculo base (ejemplo para la siguiente iteración)
            # st.session_state['total_cf'] = df_resultado['Total'].sum()
