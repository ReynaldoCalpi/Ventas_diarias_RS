import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Control de Ventas - RI Consultores",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Inteligencia de Ventas - RI Consultores")
    st.markdown("Panel gerencial avanzado para supervisión de cajas, inventarios y ventas.")
    st.divider()

    # Barra lateral para carga dinámica de archivos de contabilidad
    st.sidebar.header("📁 Carga de Archivos Base")
    file_move = st.sidebar.file_uploader("Subir Entrada de Diario (move.xlsx)", type=["xlsx"])
    file_line = st.sidebar.file_uploader("Subir Líneas de Diario (line.xlsx)", type=["xlsx"])

    if file_move and file_line:
        try:
            move = pd.read_excel(file_move)
            line = pd.read_excel(file_line)
            
            # Relacionar facturas con líneas de productos de forma segura
            df = pd.merge(line, move, left_on='Move', right_on='Name', suffixes=('_line', '_move'))
            
            # KPIs Principales
            total_venta = df['Debit_line'].sum() if 'Debit_line' in df.columns else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Venta Total Acumulada", f"${total_venta:,.2f}")
            col2.metric("Transacciones Totales", len(df['Move'].unique()))
            col3.metric("Registros Procesados", len(df))

            st.divider()

            # Gráfico de Top Productos
            if 'Name_line' in df.columns and 'Debit_line' in df.columns:
                st.subheader("🏆 Productos Top Ventas")
                top_productos = df.groupby('Name_line')['Debit_line'].sum().sort_values(ascending=False).head(10)
                fig_top = px.bar(top_productos, orientation='h', color=top_productos.values, 
                                 labels={'value': 'Monto ($)', 'Name_line': 'Producto'})
                st.plotly_chart(fig_top, use_container_width=True)

            # Consulta Detallada por DTE
            st.subheader("🔍 Consulta Detallada por Transacción (DTE)")
            dte_lista = df['Move'].unique()
            dte_seleccionado = st.selectbox("Selecciona un documento para ver detalle:", dte_lista)
            
            if dte_seleccionado:
                detalle = df[df['Move'] == dte_seleccionado]
                cols_a_mostrar = [c for c in ['Name_line', 'Quantity_line', 'Debit_line', 'Date_move'] if c in detalle.columns]
                st.dataframe(detalle[cols_a_mostrar], use_container_width=True)

        except Exception as e:
            st.error(f"Error al procesar los archivos de Excel: {e}")
    else:
        st.info("👈 Por favor, sube los archivos de Excel de contabilidad (**Entrada de diario** y **Journal Item**) en la barra lateral para habilitar los gráficos y la analítica detallada.")

if __name__ == "__main__":
    main()
