import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard RI Consultores", layout="wide", page_icon="📊")

# Inicialización segura de la carpeta de almacenamiento persistente
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
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False

    st.sidebar.markdown("### ⚙️ Panel de Control")
    modo = st.sidebar.radio("Navegación", ["Dashboard Gerencial", "Admin: Carga de Datos"])

    if modo == "Admin: Carga de Datos":
        st.sidebar.markdown("---")
        st.sidebar.header("🔑 Acceso Administrador")
        
        PASSWORD_ADMIN = "RI2026*" 
        
        if not st.session_state.admin_autenticado:
            password_input = st.sidebar.text_input("Contraseña de Admin", type="password")
            if st.sidebar.button("Ingresar"):
                if password_input == PASSWORD_ADMIN:
                    st.session_state.admin_autenticado = True
                    st.sidebar.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.sidebar.error("Contraseña incorrecta.")
        else:
            st.sidebar.success("Sesión de Admin Activa")
            if st.sidebar.button("Cerrar Sesión"):
                st.session_state.admin_autenticado = False
                st.rerun()
                
            st.sidebar.markdown("---")
            st.sidebar.header("📁 Carga de Histórico Mensual")
            file_move = st.file_uploader("Entrada de Diario (move.xlsx)", type=["xlsx"])
            file_line = st.file_uploader("Líneas de Diario (line.xlsx)", type=["xlsx"])
            mes_archivo = st.text_input("Identificador del Mes (Ej: Agosto_2026)", value="Agosto_2026")
            
            if st.button("Procesar y Guardar en Historial"):
                if file_move and file_line and mes_archivo:
                    try:
                        move = pd.read_excel(file_move)
                        line = pd.read_excel(file_line)
                        
                        df = pd.merge(line, move, on='Número', suffixes=('_line', '_move'))
                        df['Mes'] = mes_archivo
                        
                        ruta_archivo = f'data/{mes_archivo}.csv'
                        df.to_csv(ruta_archivo, index=False)
                        st.sidebar.success(f"¡Datos de {mes_archivo} guardados correctamente!")
                    except Exception as e:
                        st.sidebar.error(f"Error al procesar los archivos: {e}")
                else:
                    st.sidebar.warning("Por favor, suba ambos archivos y asigne un nombre al mes.")

    else:
        st.title("📊 Dashboard Gerencial - RI Consultores")
        st.markdown("Control ejecutivo de ventas, inventarios y análisis por periodo.")
        st.divider()

        df_hist = cargar_historico()
        
        if df_hist.empty:
            st.warning("⚠️ No hay datos históricos en la base de datos local. El administrador debe cargar el primer mes desde el panel protegido.")
        else:
            if 'Total Facturado' in df_hist.columns and 'Mes' in df_hist.columns:
                
                meses_disponibles = sorted(df_hist['Mes'].unique())
                
                col_sel1, col_sel2 = st.columns([2, 4])
                with col_sel1:
                    mes_seleccionado = st.selectbox("📅 Seleccionar Mes a Consultar:", meses_disponibles, index=len(meses_disponibles)-1)
                
                df_mes = df_hist[df_hist['Mes'] == mes_seleccionado]

                st.markdown(f"### 📌 Resumen Activo para: **{mes_seleccionado}**")
                
                venta_mes = df_mes['Total Facturado'].sum()
                transacciones_mes = len(df_mes['Número'].unique()) if 'Número' in df_mes.columns else len(df_mes)
                
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric(f"💰 Ventas Acumuladas ({mes_seleccionado})", f"${venta_mes:,.2f}")
                kpi2.metric(f"📄 Transacciones ({mes_seleccionado})", f"{transacciones_mes:,}")
                kpi3.metric("📅 Total Meses en Historial", len(meses_disponibles))

                st.divider()

                col_left, col_right = st.columns(2)

                with col_left:
                    if 'Product' in df_mes.columns:
                        st.subheader(f"🏆 Top 10 Productos ({mes_seleccionado})")
                        
                        # Agrupar sumando tanto el total facturado como las cantidades facturadas si existen
                        if 'Cantidad Facturada' in df_mes.columns:
                            top_productos = df_mes.groupby('Product').agg({
                                'Total Facturado': 'sum',
                                'Cantidad Facturada': 'sum'
                            }).reset_index().sort_values(by='Total Facturado', ascending=False).head(10)
                            
                            # Crear una columna de texto combinada: Cantidad + Monto
                            top_productos['Etiqueta'] = top_productos.apply(
                                lambda row: f"{row['Cantidad Facturada']:,.1f} un. | ${row['Total Facturado']:,.2f}", axis=1
                            )
                        else:
                            top_productos = df_mes.groupby('Product')['Total Facturado'].sum().reset_index().sort_values(by='Total Facturado', ascending=False).head(10)
                            top_productos['Etiqueta'] = top_productos['Total Facturado'].apply(lambda x: f"${x:,.2f}")

                        fig_top = px.bar(
                            top_productos, 
                            x='Total Facturado',
                            y='Product',
                            orientation='h', 
                            text='Etiqueta',
                            labels={'Total Facturado': 'Monto Total ($)', 'Product': 'Producto'}
                        )
                        fig_top.update_traces(textposition='outside')
                        fig_top.update_layout(
                            yaxis={'categoryorder':'total ascending'}, 
                            showlegend=False,
                            xaxis_title="Monto Total ($)",
                            yaxis_title=""
                        )
                        st.plotly_chart(fig_top, use_container_width=True)

                with col_right:
                    st.subheader(f"🔍 Detalle por Transacción ({mes_seleccionado})")
                    if 'Número' in df_mes.columns:
                        dte_lista = df_mes['Número'].unique()
                        dte_seleccionado = st.selectbox("Selecciona un documento de venta:", dte_lista)
                        
                        if dte_seleccionado:
                            detalle = df_mes[df_mes['Número'] == dte_seleccionado]
                            cols_a_mostrar = [c for c in ['Product', 'Cantidad Facturada', 'Precio Facturado', 'Total Facturado', 'Fecha de factura'] if c in detalle.columns]
                            st.dataframe(detalle[cols_a_mostrar], use_container_width=True)

                st.divider()

                st.subheader("📈 Comparativa Histórica de Ventas por Mes")
                ventas_mensuales = df_hist.groupby('Mes')['Total Facturado'].sum().reset_index()
                
                fig_comp = px.bar(
                    ventas_mensuales, 
                    x='Mes', 
                    y='Total Facturado', 
                    text_auto='.2s',
                    color='Mes',
                    labels={'Total Facturado': 'Venta Total ($)', 'Mes': 'Periodo'}
                )
                fig_comp.update_layout(showlegend=False)
                st.plotly_chart(fig_comp, use_container_width=True)

            else:
                st.error("Los datos cargados no contienen las columnas requeridas para el análisis.")

if __name__ == "__main__":
    main()
