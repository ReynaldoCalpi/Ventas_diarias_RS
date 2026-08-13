import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard RI Consultores", layout="wide", page_icon="📊")

# Inicialización de la carpeta de almacenamiento persistente
if not os.path.exists('data'):
    os.makedirs('data')

def cargar_historico():
    """Carga y concatena todos los archivos mensuales guardados en la carpeta /data."""
    archivos = [f for f in os.listdir('data') if f.endswith('.csv')]
    if not archivos:
        return pd.DataFrame()
    
    dfs = []
    for f in archivos:
        df_temp = pd.read_csv(f'data/{f}')
        if 'Mes' not in df_temp.columns:
            df_temp['Mes'] = f.replace('.csv', '')
        dfs.append(df_temp)
        
    return pd.concat(dfs, ignore_index=True)

def main():
    # Menú lateral de navegación (Oculto o reservado para ti, el Admin)
    st.sidebar.markdown("### ⚙️ Panel de Control")
    modo = st.sidebar.radio("Navegación", ["Dashboard Gerencial", "Admin: Carga de Datos"])

    if modo == "Admin: Carga de Datos":
        st.sidebar.markdown("---")
        st.sidebar.header("🔑 Carga de Histórico Mensual")
        file_move = st.sidebar.file_uploader("Entrada de Diario (move.xlsx)", type=["xlsx"])
        file_line = st.sidebar.file_uploader("Líneas de Diario (line.xlsx)", type=["xlsx"])
        mes_archivo = st.text_input("Identificador del Mes (Ej: Agosto_2026)", value="Agosto_2026")
        
        if st.button("Procesar y Guardar en Historial"):
            if file_move and file_line and mes_archivo:
                try:
                    move = pd.read_excel(file_move)
                    line = pd.read_excel(file_line)
                    
                    # Merge con la columna real de Odoo ('Número')
                    df = pd.merge(line, move, on='Número', suffixes=('_line', '_move'))
                    df['Mes'] = mes_archivo
                    
                    # Guardar en persistencia local
                    ruta_archivo = f'data/{mes_archivo}.csv'
                    df.to_csv(ruta_archivo, index=False)
                    st.sidebar.success(f"¡Datos de {mes_archivo} guardados correctamente!")
                except Exception as e:
                    st.sidebar.error(f"Error al procesar los archivos: {e}")
            else:
                st.sidebar.warning("Por favor, suba ambos archivos y asigne un nombre al mes.")

    else:
        # VISTA PRINCIPAL DEL DUEÑO (Gerencial, limpia y detallada)
        st.title("📊 Dashboard Gerencial - RI Consultores")
        st.markdown("Control ejecutivo de ventas, inventarios y análisis por producto.")
        st.divider()

        df_hist = cargar_historico()
        
        if df_hist.empty:
            st.warning("⚠️ No hay datos históricos en la base de datos local. Utiliza la opción **Admin: Carga de Datos** en la barra lateral para registrar el primer mes.")
        else:
            if 'Total Facturado' in df_hist.columns and 'Mes' in df_hist.columns:
                
                # KPIs Generales
                total_venta_global = df_hist['Total Facturado'].sum()
                col1, col2, col3 = st.columns(3)
                col1.metric("💰 Venta Total Histórica", f"${total_venta_global:,.2f}")
                col2.metric("📄 Transacciones Únicas", len(df_hist['Número'].unique()) if 'Número' in df_hist.columns else len(df_hist))
                col3.metric("📅 Meses Registrados", len(df_hist['Mes'].unique()))

                st.divider()

                # Comparativa Mensual
                st.subheader("📈 Comparativa de Ventas por Mes")
                ventas_mensuales = df_hist.groupby('Mes')['Total Facturado'].sum().reset_index()
                
                fig = px.bar(
                    ventas_mensuales, 
                    x='Mes', 
                    y='Total Facturado', 
                    text_auto='.2s',
                    color='Mes',
                    labels={'Total Facturado': 'Venta Total ($)', 'Mes': 'Periodo'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                st.divider()

                # --- SECCIÓN RECUPERADA: PRODUCTOS TOP Y DETALLE POR DOCUMENTO ---
                col_left, col_right = st.columns(2)

                with col_left:
                    if 'Product' in df_hist.columns:
                        st.subheader("🏆 Top 10 Productos Más Vendidos")
                        top_productos = df_hist.groupby('Product')['Total Facturado'].sum().sort_values(ascending=False).head(10)
                        fig_top = px.bar(
                            top_productos, 
                            orientation='h', 
                            color=top_productos.values,
                            labels={'value': 'Monto Total ($)', 'Product': 'Producto'}
                        )
                        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                        st.plotly_chart(fig_top, use_container_width=True)

                with col_right:
                    st.subheader("🔍 Detalle por Transacción (DTE)")
                    if 'Número' in df_hist.columns:
                        dte_lista = df_hist['Número'].unique()
                        dte_seleccionado = st.selectbox("Selecciona un documento de venta:", dte_lista)
                        
                        if dte_seleccionado:
                            detalle = df_hist[df_hist['Número'] == dte_seleccionado]
                            cols_a_mostrar = [c for c in ['Product', 'Cantidad Facturada', 'Precio Facturado', 'Total Facturado', 'Fecha de factura'] if c in detalle.columns]
                            st.dataframe(detalle[cols_a_mostrar], use_container_width=True)
            else:
                st.error("Los datos cargados no contienen las columnas requeridas para el análisis.")

if __name__ == "__main__":
    main()
