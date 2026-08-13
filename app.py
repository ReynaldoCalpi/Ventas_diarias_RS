import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Gerencial", layout="wide")

@st.cache_data
def cargar_datos():
    # Carga de los archivos que proporcionaste
    move = pd.read_excel("Entrada de diario (account.move).xlsx")
    line = pd.read_excel("Journal Item (account.move.line).xlsx")
    # Join para relacionar productos con facturas
    df = pd.merge(line, move, left_on='Move', right_on='Name', suffixes=('_line', '_move'))
    return df

def main():
    st.title("📊 Inteligencia de Ventas - RI Consultores")
    df = cargar_datos()

    # 1. KPIs Generales
    total_venta = df['Debit_line'].sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Venta Total Acumulada", f"${total_venta:,.2f}")
    col2.metric("Transacciones Totales", len(df['Move'].unique()))
    col3.metric("Productos Activos", len(df['Account_line'].unique()))

    st.divider()

    # 2. Top Productos (Basado en Journal Items)
    st.subheader("🏆 Productos Top Ventas")
    top_productos = df.groupby('Name_line')['Debit_line'].sum().sort_values(ascending=False).head(10)
    fig_top = px.bar(top_productos, orientation='h', color=top_productos.values, 
                     labels={'value': 'Monto ($)', 'Name_line': 'Producto'})
    st.plotly_chart(fig_top, use_container_width=True)

    # 3. Consulta Detallada por DTE
    st.subheader("🔍 Consulta Detallada de Factura")
    dte_seleccionado = st.selectbox("Selecciona un DTE (Factura) para ver detalle:", df['Move'].unique())
    
    if dte_seleccionado:
        detalle = df[df['Move'] == dte_seleccionado]
        st.table(detalle[['Name_line', 'Quantity_line', 'Debit_line']])

if __name__ == "__main__":
    main()
