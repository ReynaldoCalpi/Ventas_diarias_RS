import xmlrpc.client
import streamlit as st
import pandas as pd

def get_odoo_connection():
    # Obtener credenciales de los Secrets de Streamlit Cloud
    url = st.secrets["odoo"]["url"]
    db = st.secrets["odoo"]["db"]
    username = st.secrets["odoo"]["username"]
    password = st.secrets["odoo"]["api_key"]

    # Autenticación
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    
    # Proxy para llamadas a modelos
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    
    return models, db, uid, password

def fetch_odoo_data(start_date):
    """Extrae facturas publicadas desde una fecha dada."""
    models, db, uid, password = get_odoo_connection()
    
    # Dominio de búsqueda: solo facturas de cliente publicadas
    domain = [
        ('move_type', '=', 'out_invoice'),
        ('state', '=', 'posted'),
        ('invoice_date', '>=', start_date)
    ]
    
    # 1. Buscar IDs de las facturas
    ids = models.execute_kw(db, uid, password, 'account.move', 'search', [domain])
    
    if not ids:
        return None
    
    # 2. Leer datos de las facturas (campos clave para tu dashboard)
    # Nota: invoice_line_ids son los IDs de las líneas asociadas
    facturas = models.execute_kw(db, uid, password, 'account.move', 'read', [ids], 
                                 {'fields': ['name', 'invoice_date', 'amount_total', 'invoice_line_ids', 'partner_id']})
    
    return facturas

def get_line_details(line_ids):
    """Extrae el detalle específico de las líneas de factura."""
    models, db, uid, password = get_odoo_connection()
    lineas = models.execute_kw(db, uid, password, 'account.move.line', 'read', [line_ids],
                               {'fields': ['product_id', 'quantity', 'price_unit', 'price_subtotal']})
    return lineas