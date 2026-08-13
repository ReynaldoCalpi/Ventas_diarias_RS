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

    st.sidebar.header("📁 Carga de Archivos Base")
    file_move = st.sidebar.file_uploader("Subir Entrada de Diario (move.xlsx)", type=["xlsx"])
    file_line = st.sidebar.file_uploader("Subir Líneas de Diario (line.xlsx)", type=["xlsx"])

    if file_move and file_line:
        try:
            move = pd.read_excel(file_move)
            line = pd.read_excel(file_line)
            
            # Mapeo exacto basado en la estructura de Odoo encontrada ('Número')
            df = pd.merge(line, move, on='Número', suffixes=('_line', '_move'))
            
            # Validar métricas clave con nombres reales
            total_venta = df['Total Facturado'].sum() if 'Total Facturado' in df.columns else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Venta Total Acumulada", f"${total_venta:,.2f}")
            col2.metric("Transacciones Totales", len(df['Número'].unique()))
            col3.metric("Registros Procesados", len(df))

            st.divider()

            # Gráfico de Top Productos
            if 'Product' in df.columns and 'Total Facturado' in df.columns:
                st.subheader("🏆 Productos Top Ventas")
                top_productos = df.groupby('Product')['Total Facturado'].sum().sort_values(ascending=False).head(10)
                fig_top = px.bar(top_productos, orientation='h', color=top_productos.values, 
                                 labels={'value': 'Monto ($)', 'Product': 'Producto'})
                st.plotly_chart(fig_top, use_container_width=True)

            # Consulta Detallada por Documento
            st.subheader("🔍 Consulta Detallada por Transacción")
            dte_lista = df['Número'].unique()
            dte_seleccionado = st.selectbox("Selecciona un documento para ver detalle:", dte_lista)
            
            if dte_seleccionado:
                detalle = df[df['Número'] == dte_seleccionado]
                cols_a_mostrar = [c for c in ['Product', 'Cantidad Facturada', 'Precio Facturado', 'Total Facturado', 'Fecha de factura'] if c in detalle.columns]
                st.dataframe(detalle[cols_a_mostrar], use_container_width=True)

        except Exception as e:
            st.error(f"Error procesando los datos: {e}")
    else:
        st.info("👈 Sube ambos archivos Excel en la barra lateral para generar el análisis automático de productos y ventas.")

if __name__ == "__main__":
    main()
