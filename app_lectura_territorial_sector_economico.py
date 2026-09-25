# streamlit run app_lectura_territorial_sector_economico.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y CSS GLOBAL
# ==========================================
st.set_page_config(page_title="Inteligencia Operativa y Territorial", layout="wide")

st.markdown("""
    <style>
    /* Estilos Tarjetas KPI */
    .kpi-card { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px; height: 140px; margin-bottom: 20px; }
    .kpi-title { color: #6b7280; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px; }
    .kpi-value { color: #111827; font-size: 2.2rem; font-weight: 700; margin-bottom: 5px; line-height: 1.2; }
    .kpi-value-small { font-size: 1rem; color: #9ca3af; font-weight: 500; }
    .kpi-subtext { color: #6b7280; font-size: 0.85rem; display: flex; align-items: center; gap: 5px; }
    .progress-bar-bg { background-color: #e5e7eb; border-radius: 999px; height: 8px; width: 100%; margin: 10px 0; }
    .progress-bar-fill { background-color: #2563eb; border-radius: 999px; height: 8px; }
    
    /* Estilos Encabezados y Contenedores */
    .header-badge { padding: 6px 16px; border-radius: 999px; font-size: 0.8rem; font-weight: bold; float: right; margin-top: 15px; }
    .overtitle { color: #6b7280; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: -10px; }
    .st-emotion-cache-1wivap2 { border-radius: 15px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    
    /* Estilos Alertas Tablas */
    .alert-box-red { background-color: #fef2f2; border: 1px solid #fca5a5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .alert-box-blue { background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CARGA CENTRALIZADA DE DATOS
# ==========================================
@st.cache_data
def cargar_datasets():
    try:
        # Carga Operatividad Territorial
        df = pd.read_csv("data/df_operatividad_territorial.csv")
        for col in ['departamento', 'municipio', 'area_metropolitana', 'nombre_pdet', 'sector']:
            df[col] = df[col].astype(str).replace('nan', 'No aplica')
        df['area_metropolitana'] = df['area_metropolitana'].replace('No', 'No aplica')
        df['nombre_pdet'] = df['nombre_pdet'].replace('No PDET', 'No aplica')
        df['pnis'] = df['pnis'].astype(str)

        # Carga Catálogo Operativo
        df_cat = pd.read_csv("data/df_catalogo_operativo.csv")
        for col in ['departamento', 'municipio', 'area_metropolitana', 'nombre_pdet', 'sector', 'articulo']:
            df_cat[col] = df_cat[col].astype(str).replace('nan', 'No aplica')
        df_cat['area_metropolitana'] = df_cat['area_metropolitana'].replace('No', 'No aplica')
        df_cat['nombre_pdet'] = df_cat['nombre_pdet'].replace('No PDET', 'No aplica')
        df_cat['pnis'] = df_cat['pnis'].astype(str)

        return df, df_cat
    except Exception as e:
        st.error(f"Error cargando archivos: {e}")
        st.stop()

df, df_cat = cargar_datasets()

# ==========================================
# 3. LÓGICA DE ESTADO Y FILTROS EN CASCADA ÚNICOS
# ==========================================
filtro_keys = ['ventana', 'sector', 'depto', 'muni', 'area', 'pdet', 'pnis']

def reset_filtros():
    st.session_state.ventana = "12_meses"
    st.session_state.sector = "Todos"
    st.session_state.depto = "Todos"
    st.session_state.muni = "Todos"
    st.session_state.area = "Todas"
    st.session_state.pdet = "Todas"
    st.session_state.pnis = "Todas"

for key in filtro_keys:
    if key not in st.session_state:
        if key == 'ventana': st.session_state[key] = "12_meses"
        else: st.session_state[key] = "Todos" if key in ['sector', 'depto', 'muni'] else "Todas"

def opciones_filtradas(columna_target, valor_actual, key_filtro):
    df_temp = df[df['ventana_temporal'] == st.session_state.ventana]
    
    if key_filtro != 'sector' and st.session_state.sector != "Todos":
        df_temp = df_temp[df_temp['sector'] == st.session_state.sector]
    if key_filtro != 'depto' and st.session_state.depto != "Todos":
        df_temp = df_temp[df_temp['departamento'] == st.session_state.depto]
    if key_filtro != 'muni' and st.session_state.muni != "Todos":
        df_temp = df_temp[df_temp['municipio'] == st.session_state.muni]
    if key_filtro != 'area' and st.session_state.area != "Todas":
        df_temp = df_temp[df_temp['area_metropolitana'] == st.session_state.area]
    if key_filtro != 'pdet' and st.session_state.pdet != "Todas":
        df_temp = df_temp[df_temp['nombre_pdet'] == st.session_state.pdet]
    if key_filtro != 'pnis' and st.session_state.pnis != "Todas":
        estado_pnis = "True" if st.session_state.pnis == "Sí" else "False"
        df_temp = df_temp[df_temp['pnis'] == estado_pnis]

    base_label = "Todas" if key_filtro in ['area', 'pdet', 'pnis'] else "Todos"
    
    if key_filtro == 'pnis':
        pnis_vivos = df_temp['pnis'].unique()
        op_list = [base_label]
        if "True" in pnis_vivos: op_list.append("Sí")
        if "False" in pnis_vivos: op_list.append("No")
    else:
        opciones_vivas = sorted(df_temp[columna_target].unique().tolist())
        op_list = [base_label] + opciones_vivas

    if valor_actual not in op_list:
        st.session_state[key_filtro] = base_label
        
    return op_list

op_sectores = opciones_filtradas('sector', st.session_state.sector, 'sector')
op_deptos = opciones_filtradas('departamento', st.session_state.depto, 'depto')
op_muni = opciones_filtradas('municipio', st.session_state.muni, 'muni')
op_areas = opciones_filtradas('area_metropolitana', st.session_state.area, 'area')
op_pdets = opciones_filtradas('nombre_pdet', st.session_state.pdet, 'pdet')
op_pnis = opciones_filtradas('pnis', st.session_state.pnis, 'pnis')

# --- Renderizado del Panel Visual de Filtros ---
col_tit, col_btn = st.columns([8, 2])
with col_tit: st.markdown("### ⚙️ Panel de Filtros Entrelazados")
with col_btn:
    st.write("")
    st.button("🔄 Restablecer Filtros", on_click=reset_filtros, use_container_width=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.selectbox("🕒 Ventana Temporal", ["12_meses", "6_meses", "3_meses"], key="ventana")
    st.selectbox("🎯 Sector", op_sectores, key="sector")
with col2:
    st.selectbox("📍 Departamento", op_deptos, key="depto")
    st.selectbox("🗺️ Municipio", op_muni, key="muni")
with col3:
    st.selectbox("🏙️ Área Metropolitana", op_areas, key="area")
    st.selectbox("🕊️ Zona PDET", op_pdets, key="pdet")
with col4:
    st.selectbox("🌱 Zona PNIS", op_pnis, key="pnis")

st.divider()

# ==========================================
# 4. PREPARACIÓN DE DATAFRAMES (TRES NIVELES)
# ==========================================
# 4.1 df_f: Totalmente filtrado para Tarjetas (KPIs) y Tablas
df_f = df[df['ventana_temporal'] == st.session_state.ventana].copy()
if st.session_state.sector != "Todos": df_f = df_f[df_f['sector'] == st.session_state.sector]
if st.session_state.depto != "Todos": df_f = df_f[df_f['departamento'] == st.session_state.depto]
if st.session_state.muni != "Todos": df_f = df_f[df_f['municipio'] == st.session_state.muni]
if st.session_state.area != "Todas": df_f = df_f[df_f['area_metropolitana'] == st.session_state.area]
if st.session_state.pdet != "Todas": df_f = df_f[df_f['nombre_pdet'] == st.session_state.pdet]
if st.session_state.pnis != "Todas":
    estado_pnis = "True" if st.session_state.pnis == "Sí" else "False"
    df_f = df_f[df_f['pnis'] == estado_pnis]

# 4.2 df_cat_f: Totalmente filtrado para el Acordeón del Catálogo Penal
df_cat_f = df_cat[df_cat['ventana_temporal'] == st.session_state.ventana].copy()
if st.session_state.sector != "Todos": df_cat_f = df_cat_f[df_cat_f['sector'] == st.session_state.sector]
if st.session_state.depto != "Todos": df_cat_f = df_cat_f[df_cat_f['departamento'] == st.session_state.depto]
if st.session_state.muni != "Todos": df_cat_f = df_cat_f[df_cat_f['municipio'] == st.session_state.muni]
if st.session_state.area != "Todas": df_cat_f = df_cat_f[df_cat_f['area_metropolitana'] == st.session_state.area]
if st.session_state.pdet != "Todas": df_cat_f = df_cat_f[df_cat_f['nombre_pdet'] == st.session_state.pdet]
if st.session_state.pnis != "Todas":
    estado_pnis = "True" if st.session_state.pnis == "Sí" else "False"
    df_cat_f = df_cat_f[df_cat_f['pnis'] == estado_pnis]

# 4.3 df_geo: Parcialmente filtrado (Sin Sector ni Municipio) para la base de las Gráficas
df_geo = df[df['ventana_temporal'] == st.session_state.ventana].copy()
if st.session_state.depto != "Todos": df_geo = df_geo[df_geo['departamento'] == st.session_state.depto]
if st.session_state.area != "Todas": df_geo = df_geo[df_geo['area_metropolitana'] == st.session_state.area]
if st.session_state.pdet != "Todas": df_geo = df_geo[df_geo['nombre_pdet'] == st.session_state.pdet]
if st.session_state.pnis != "Todas":
    estado_pnis = "True" if st.session_state.pnis == "Sí" else "False"
    df_geo = df_geo[df_geo['pnis'] == estado_pnis]

df_geo['es_priorizada'] = (df_geo['nombre_pdet'] != "No aplica") | (df_geo['pnis'] == "True")
df_geo['presion_prio_valor'] = df_geo['presion_ponderada'] * df_geo['es_priorizada']


# ==========================================
# 5. MÓDULO 1: TARJETAS KPI Y CATÁLOGO
# ==========================================
# --- Matemáticas KPI ---
if st.session_state.sector == "Todos":
    df_muni_puro = df_f.groupby(['departamento', 'municipio'], as_index=False).agg(
        Hechos_Muni=('total_hechos_muni', 'first'),
        Capturas_Muni=('capturas_totales_muni', 'first')
    )
    tot_hechos = int(df_muni_puro['Hechos_Muni'].sum())
    tot_capturas = int(df_muni_puro['Capturas_Muni'].sum())
    tot_presion = df_f['presion_ponderada'].sum()
    tot_unidades_criticas = int(df_f['unidades_criticas'].sum())
    sev_media = (tot_presion / tot_capturas) if tot_capturas > 0 else 0.0
else:
    tot_hechos = int(df_f['total_hechos_sector'].sum())
    tot_capturas = int(df_f['capturas_sector'].sum())
    tot_presion = df_f['presion_ponderada'].sum()
    tot_unidades_criticas = int(df_f['unidades_criticas'].sum())
    sev_media = (tot_presion / tot_capturas) if tot_capturas > 0 else 0.0

mask_priorizada = (df_f['nombre_pdet'] != "No aplica") | (df_f['pnis'] == "True")
presion_priorizada = df_f.loc[mask_priorizada, 'presion_ponderada'].sum()
pct_presion_prio = (presion_priorizada / tot_presion * 100) if tot_presion > 0 else 0.0
sectores_activos = df_f[df_f['capturas_sector'] > 0]['sector'].nunique()

df_base = df[df['ventana_temporal'] == st.session_state.ventana]
presion_nacional_total = df_base['presion_ponderada'].sum()
cuota_esfuerzo = (tot_presion / presion_nacional_total * 100) if presion_nacional_total > 0 else 0.0

# --- Lógica Badge ---
if st.session_state.sector != "Todos":
    if tot_unidades_criticas >= 70: badge_text = "🛡️ EXPOSICIÓN SECTORIAL: CRÍTICA"; badge_color = "#dc2626"
    elif tot_unidades_criticas >= 35: badge_text = "🛡️ EXPOSICIÓN SECTORIAL: ALTA"; badge_color = "#ea580c"
    elif tot_unidades_criticas >= 15: badge_text = "🛡️ EXPOSICIÓN SECTORIAL: MEDIA"; badge_color = "#ca8a04"
    else: badge_text = "🛡️ EXPOSICIÓN SECTORIAL: BAJA"; badge_color = "#16a34a"
else:
    badge_color = "#1d4ed8"
    if st.session_state.muni != "Todos": badge_text = "🛡️ EXPOSICIÓN: NIVEL LOCAL"
    elif st.session_state.pdet != "Todas" or st.session_state.area != "Todas" or st.session_state.depto != "Todos": badge_text = "🛡️ EXPOSICIÓN: NIVEL REGIONAL"
    else: badge_text = "🛡️ EXPOSICIÓN: NIVEL PAÍS"

# --- Render Tarjetas ---
with st.container(border=True):
    if st.session_state.sector == "Todos":
        if st.session_state.muni != "Todos": overtitle = "CONSOLIDADO MUNICIPAL"; maintitle = f"Dinámica en {st.session_state.muni}"
        elif st.session_state.pdet != "Todas" and st.session_state.pdet != "No aplica": overtitle = "CONSOLIDADO SUBREGIONAL PDET"; maintitle = f"Subregión: {st.session_state.pdet}"
        elif st.session_state.area != "Todas" and st.session_state.area != "No aplica": overtitle = "CONSOLIDADO METROPOLITANO"; maintitle = f"Área: {st.session_state.area}"
        elif st.session_state.depto != "Todos": overtitle = "CONSOLIDADO DEPARTAMENTAL"; maintitle = f"Dinámica en {st.session_state.depto}"
        else: overtitle = "CONSOLIDADO NACIONAL"; maintitle = "Consolidado Global Multisectorial"

        st.markdown(f"""
            <div style='margin-bottom: 25px;'>
                <div class='header-badge' style='background-color: {badge_color}; color: white;'>{badge_text}</div>
                <div class='overtitle'>{overtitle}</div>
                <h2 style='color: #111827; font-weight: 800; margin-top: 10px;'>{maintitle}</h2>
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>TOTAL CAPTURAS</div><div class='kpi-value'>{tot_capturas:,.0f}</div><div class='kpi-subtext'>❖ {sectores_activos} sectores nacionales</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>TOTAL HECHOS</div><div class='kpi-value'>{tot_hechos:,.0f}</div><div class='kpi-subtext'>📄 Consolidado nacional</div></div>""", unsafe_allow_html=True)
        with c3:
            ancho_barra = min((sev_media / 5.00) * 100, 100)
            st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>SEVERIDAD MEDIA</div><div class='kpi-value'>{sev_media:.2f} <span class='kpi-value-small'>/ 5.00</span></div><div class='progress-bar-bg'><div class='progress-bar-fill' style='width: {ancho_barra}%;'></div></div><div class='kpi-subtext'>Gravedad promedio del delito imputado por captura.</div></div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>% PRESIÓN PRIORIZADA (PDET/PNIS)</div><div style='color: #2563eb;' class='kpi-value'>{pct_presion_prio:.1f}%</div><div class='kpi-subtext' style='margin-top: 15px;'>Focalización en zonas institucionales</div></div>""", unsafe_allow_html=True)

    else:
        st.markdown(f"""
            <div style='margin-bottom: 25px;'>
                <div class='header-badge' style='background-color: {badge_color}; color: white;'>{badge_text}</div>
                <div class='overtitle'>LECTURA FOCALIZADA SECTORIAL</div>
                <h2 style='color: #111827; font-weight: 800; margin-top: 10px;'>Sector Económico: {st.session_state.sector}</h2>
            </div>
        """, unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>TOTAL CAPTURAS</div><div class='kpi-value'>{tot_capturas:,.0f}</div><div class='kpi-subtext'>📚 Registradas en el sector</div></div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>% PRESIÓN</div><div class='kpi-value'>{cuota_esfuerzo:.1f}%</div><div class='kpi-subtext'>📄 Cuota del esfuerzo judicial nacional.</div></div>""", unsafe_allow_html=True)
        with k3:
            ancho_barra = min((sev_media / 5.00) * 100, 100)
            st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>SEVERIDAD MEDIA</div><div class='kpi-value'>{sev_media:.2f} <span class='kpi-value-small'>/ 5.00</span></div><div class='progress-bar-bg'><div class='progress-bar-fill' style='width: {ancho_barra}%;'></div></div><div class='kpi-subtext'>Gravedad promedio del delito imputado.</div></div>""", unsafe_allow_html=True)
        with k4:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>% PRESIÓN PRIORIZADA (PDET/PNIS)</div><div style='color: #2563eb;' class='kpi-value'>{pct_presion_prio:.1f}%</div><div class='kpi-subtext' style='margin-top: 15px;'>Focalización en zonas institucionales</div></div>""", unsafe_allow_html=True)

    # --- Render Acordeón Catálogo ---
    st.markdown("<br>", unsafe_allow_html=True)
    top_articulos = df_cat_f.groupby(['sector', 'articulo', 'tipo_relacion', 'peso'], as_index=False).agg(capturas=('capturas', 'sum'))
    top_articulos = top_articulos[top_articulos['capturas'] > 0].sort_values(by='capturas', ascending=False).reset_index(drop=True)
    num_articulos_activos = len(top_articulos)
    
    titulo_acordeon = f"Catálogo de Top Artículos Penales Asociados ({st.session_state.sector})" if st.session_state.sector != "Todos" else "Catálogo de Top Artículos Penales Consolidados"

    with st.expander(f"📖 **{titulo_acordeon}**   `{num_articulos_activos} artículos`"):
        if num_articulos_activos > 0:
            top_articulos.columns = ["SECTOR", "ARTÍCULO DEL CÓDIGO PENAL", "TIPO DE RELACIÓN", "PESO PONDERADO", "CAPTURAS REGISTRADAS"]
            top_articulos["TIPO DE RELACIÓN"] = top_articulos["TIPO DE RELACIÓN"].str.capitalize().astype("category")
            st.dataframe(top_articulos, use_container_width=True, hide_index=True, height=350, column_config={"PESO PONDERADO": st.column_config.NumberColumn(format="%d"), "CAPTURAS REGISTRADAS": st.column_config.NumberColumn(format="%d")})
        else:
            st.info("No hay capturas registradas para la selección actual.")


# ==========================================
# 6. MÓDULO 2: GRÁFICAS DE PLOTLY
# ==========================================
st.markdown("### Gráficas de Inteligencia Operativa y Dinámicas Territoriales")
col_g1, col_g2 = st.columns(2)

# --- Preparación Gráfico 1 ---
df_plot_sector = df_geo.copy()
if st.session_state.muni != "Todos": 
    df_plot_sector = df_plot_sector[df_plot_sector['municipio'] == st.session_state.muni]

df_plot1 = df_plot_sector.groupby('sector', as_index=False).agg(
    Total_Capturas=('capturas_sector', 'sum'),
    Total_Presion=('presion_ponderada', 'sum'),
    Presion_Prio=('presion_prio_valor', 'sum')
)
df_plot1['Severidad'] = np.where(df_plot1['Total_Capturas'] > 0, df_plot1['Total_Presion'] / df_plot1['Total_Capturas'], 0)
df_plot1['Pct_Prio'] = np.where(df_plot1['Total_Presion'] > 0, (df_plot1['Presion_Prio'] / df_plot1['Total_Presion']) * 100, 0)
df_plot1['Label'] = df_plot1['sector'].str[:4].str.capitalize()
df_plot1 = df_plot1[df_plot1['Total_Capturas'] > 0].reset_index(drop=True)

# --- Preparación Gráfico 2 ---
muni_activo = st.session_state.muni
sector_activo = st.session_state.sector
df_plot_base2 = df_geo.copy()

if muni_activo == "Todos":
    if sector_activo == "Todos": 
        df_plot2 = df_plot_base2.groupby('municipio', as_index=False).agg(Amenaza=('total_hechos_muni', 'first'), Respuesta=('capturas_totales_muni', 'first'))
    else:
        df_plot_base2 = df_plot_base2[df_plot_base2['sector'] == sector_activo]
        df_plot2 = df_plot_base2.groupby('municipio', as_index=False).agg(Amenaza=('total_hechos_sector', 'sum'), Respuesta=('capturas_sector', 'sum'))
        
    df_plot2 = df_plot2[(df_plot2['Amenaza'] > 0) | (df_plot2['Respuesta'] > 0)]
    df_plot2['log_amenaza'] = np.log1p(df_plot2['Amenaza'])
    df_plot2['log_respuesta'] = np.log1p(df_plot2['Respuesta'])
    df_plot2 = df_plot2.sort_values(by=['Amenaza', 'Respuesta'], ascending=False).head(100).reset_index(drop=True)
    df_plot2['label_punto'] = df_plot2['municipio']
    subtitulo_g2 = f"Muestra: {len(df_plot2)} Municipios (Escala Pseudo-Log)"
else:
    df_plot_base2 = df_plot_base2[df_plot_base2['municipio'] == muni_activo]
    df_plot2 = df_plot_base2.groupby('sector', as_index=False).agg(Amenaza=('total_hechos_sector', 'sum'), Respuesta=('capturas_sector', 'sum'))
    df_plot2 = df_plot2[(df_plot2['Amenaza'] > 0) | (df_plot2['Respuesta'] > 0)]
    df_plot2['log_amenaza'] = np.log1p(df_plot2['Amenaza'])
    df_plot2['log_respuesta'] = np.log1p(df_plot2['Respuesta'])
    df_plot2['label_punto'] = df_plot2['sector']
    subtitulo_g2 = f"Muestra: {len(df_plot2)} Sectores en {muni_activo} (Escala Pseudo-Log)"

# --- Render Gráfico 1 ---
with col_g1:
    with st.container(border=True):
        st.markdown("#### Volumen vs. Severidad")
        st.markdown("<span style='color: #9ca3af; font-size: 0.9rem;'>Eje X: Capturas | Eje Y: Severidad (1-5) | Tamaño: Presión | Color: % Priorizada</span>", unsafe_allow_html=True)
        if df_plot1.empty:
            st.warning("No hay datos sectoriales para graficar con los filtros actuales.")
        else:
            opacidades1 = [1.0 if (s == sector_activo or sector_activo == "Todos") else 0.4 for s in df_plot1['sector']]
            grosores_borde1 = [3 if s == sector_activo else 0 for s in df_plot1['sector']]
            colores_borde1 = ['#dc2626' if s == sector_activo else 'rgba(0,0,0,0)' for s in df_plot1['sector']]
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df_plot1['Total_Capturas'], y=df_plot1['Severidad'], mode='markers+text',
                text=df_plot1['Label'], textposition='middle center', textfont=dict(color='white', size=11, family="Arial"),
                marker=dict(size=df_plot1['Total_Presion'], sizemode='area', sizeref=2.*max(df_plot1['Total_Presion'])/(80.**2) if max(df_plot1['Total_Presion'])>0 else 1, sizemin=15, color=df_plot1['Pct_Prio'], colorscale='Viridis', opacity=opacidades1, line=dict(width=grosores_borde1, color=colores_borde1), showscale=True, colorbar=dict(title=dict(text="Escala % Presión Priorizada:", side="top"), orientation="h", y=-0.25, x=0.5, xanchor="center", yanchor="top", len=0.7, thickness=15)),
                hoverinfo='text', hovertext="<b>" + df_plot1['sector'] + "</b><br>Capturas: " + df_plot1['Total_Capturas'].astype(str) + "<br>Severidad: " + df_plot1['Severidad'].round(2).astype(str) + "<br>Priorización: " + df_plot1['Pct_Prio'].round(1).astype(str) + "%"
            ))
            fig1.update_layout(height=550, plot_bgcolor='white', xaxis=dict(title="<b>Total Capturas</b>", showgrid=True, gridcolor='#f3f4f6', gridwidth=1, griddash='dot', zeroline=False), yaxis=dict(title="<b>Severidad Media (1.00 - 5.00)</b>", range=[0.8, 5.2], showgrid=True, gridcolor='#f3f4f6', gridwidth=1, griddash='dot', zeroline=False), margin=dict(l=40, r=40, t=40, b=80))
            if sector_activo != "Todos":
                fig1.add_annotation(text=f"♦ <b>Activo:</b><br>{sector_activo}", align='left', showarrow=False, xref='paper', yref='paper', x=0.98, y=1.05, bgcolor="#fee2e2", bordercolor="#fca5a5", font=dict(color="#b91c1c", size=12))
                if sector_activo in df_plot1['sector'].values:
                    burbuja_activa = df_plot1[df_plot1['sector'] == sector_activo].iloc[0]
                    fig1.add_annotation(x=burbuja_activa['Total_Capturas'], y=burbuja_activa['Severidad'], text="★", showarrow=False, font=dict(color="#dc2626", size=18), yshift=20, xshift=-20)
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

# --- Render Gráfico 2 ---
with col_g2:
    with st.container(border=True):
        st.markdown("#### Amenaza vs. Respuesta")
        st.markdown(f"<span style='color: #9ca3af; font-size: 0.9rem;'>Eje X: Hechos (Amenaza) | Eje Y: Capturas (Respuesta) | {subtitulo_g2}</span>", unsafe_allow_html=True)
        if df_plot2.empty:
            st.warning("No hay datos territoriales para graficar con los filtros actuales.")
        else:
            mid_log_amenaza = df_plot2['log_amenaza'].median() if len(df_plot2) > 0 else 0
            mid_log_respuesta = df_plot2['log_respuesta'].median() if len(df_plot2) > 0 else 0
            
            colores, para_leyenda = [], []
            for i, row in df_plot2.iterrows():
                if row['log_amenaza'] >= mid_log_amenaza and row['log_respuesta'] >= mid_log_respuesta: c, l = "#f97316", "Foco Activo de Contención"
                elif row['log_amenaza'] < mid_log_amenaza and row['log_respuesta'] >= mid_log_respuesta: c, l = "#1f77b4", "Control Operativo / Interdicción"
                elif row['log_amenaza'] >= mid_log_amenaza and row['log_respuesta'] < mid_log_respuesta: c, l = "#dc2626", "Alerta: Alta Amenaza / Vacío Operativo"
                else: c, l = "#22c55e", "Zona Estable"
                colores.append(c); para_leyenda.append(l)

            df_plot2['Color'] = colores; df_plot2['Categoria'] = para_leyenda
            fig2 = go.Figure()
            max_x = df_plot2['log_amenaza'].max() * 1.05 if not df_plot2.empty else 10
            max_y = df_plot2['log_respuesta'].max() * 1.05 if not df_plot2.empty else 10

            fig2.add_shape(type="rect", x0=0, y0=0, x1=max_x, y1=max_y, fillcolor="#fffbeb", opacity=0.3, layer="below", line_width=0)
            for categoria, color in zip(["Foco Activo de Contención", "Control Operativo / Interdicción", "Alerta: Alta Amenaza / Vacío Operativo", "Zona Estable"], ["#f97316", "#1f77b4", "#dc2626", "#22c55e"]):
                df_cat_plot = df_plot2[df_plot2['Categoria'] == categoria]
                if not df_cat_plot.empty:
                    if muni_activo == "Todos": opacidades2, grosores_borde2, colores_borde2 = [1.0]*len(df_cat_plot), [1]*len(df_cat_plot), ['white']*len(df_cat_plot)
                    else:
                        opacidades2 = [1.0 if (s == sector_activo or sector_activo == "Todos") else 0.4 for s in df_cat_plot['label_punto']]
                        grosores_borde2 = [3 if s == sector_activo else 1 for s in df_cat_plot['label_punto']]
                        colores_borde2 = ['#dc2626' if s == sector_activo else 'white' for s in df_cat_plot['label_punto']]
                    fig2.add_trace(go.Scatter(x=df_cat_plot['log_amenaza'], y=df_cat_plot['log_respuesta'], mode='markers+text', name=categoria, text=df_cat_plot['label_punto'], textposition="middle right", textfont=dict(size=9, color="#4b5563"), marker=dict(size=10, color=color, opacity=opacidades2, line=dict(width=grosores_borde2, color=colores_borde2)), hoverinfo='text', hovertext="<b>" + df_cat_plot['label_punto'] + "</b><br>Hechos Reales: " + df_cat_plot['Amenaza'].astype(str) + "<br>Capturas Reales: " + df_cat_plot['Respuesta'].astype(str)))

            fig2.add_vline(x=mid_log_amenaza, line_width=2, line_dash="dash", line_color="#9ca3af")
            fig2.add_hline(y=mid_log_respuesta, line_width=2, line_dash="dash", line_color="#9ca3af")
            font_prop = dict(size=9)
            fig2.add_annotation(x=max_x*0.75, y=max_y*0.95, text="<b>Foco Activo de Contención</b>", showarrow=False, font=dict(color="#ea580c", **font_prop))
            fig2.add_annotation(x=max_x*0.25, y=max_y*0.95, text="<b>Control Operativo / Interdicción</b>", showarrow=False, font=dict(color="#1d4ed8", **font_prop))
            fig2.add_annotation(x=max_x*0.75, y=max_y*0.05, text="<b>Alerta: Alta Amenaza / Vacío Operativo</b>", showarrow=False, font=dict(color="#b91c1c", **font_prop))
            fig2.add_annotation(x=max_x*0.10, y=max_y*0.05, text="<b>Zona Estable</b>", showarrow=False, font=dict(color="#15803d", **font_prop))

            if muni_activo != "Todos":
                fig2.add_annotation(text=f"♦ <b>Dinámica Interna:</b><br>{muni_activo}", align='left', showarrow=False, xref='paper', yref='paper', x=0.98, y=1.05, bgcolor="#f0fdf4", bordercolor="#bbf7d0", font=dict(color="#166534", size=12))
                if sector_activo != "Todos" and sector_activo in df_plot2['label_punto'].values:
                    sec_row = df_plot2[df_plot2['label_punto'] == sector_activo].iloc[0]
                    fig2.add_annotation(x=sec_row['log_amenaza'], y=sec_row['log_respuesta'], text="★", showarrow=False, font=dict(color="#dc2626", size=18), yshift=15, xshift=-15)

            fig2.update_layout(height=550, plot_bgcolor='white', xaxis=dict(title="<b>Hechos Criminales (Escala Pseudo-Log)</b>", showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(title="<b>Capturas (Escala Pseudo-Log)</b>", showgrid=False, zeroline=False, showticklabels=False), margin=dict(l=40, r=40, t=40, b=80), legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", yanchor="top", font=dict(size=10)))
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})


# ==========================================
# 7. MÓDULO 3: TABLAS DE FOCALIZACIÓN
# ==========================================
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("### Tablas de Acción Territorial y Focalización")
st.markdown("<span style='color: #6b7280; font-size: 0.95rem;'>Priorización operativa para toma de decisiones y despliegue de fuerza</span>", unsafe_allow_html=True)

df_tabla = df_f.copy()

if not df_tabla.empty:
    mid_log_h = np.log1p(df_tabla['total_hechos_sector']).median()
    mid_log_c = np.log1p(df_tabla['capturas_sector']).median()

    log_h = np.log1p(df_tabla['total_hechos_sector'])
    log_c = np.log1p(df_tabla['capturas_sector'])

    cond_foco = (log_h >= mid_log_h) & (log_c >= mid_log_c)
    cond_control = (log_h < mid_log_h) & (log_c >= mid_log_c)
    cond_vacio = (log_h >= mid_log_h) & (log_c < mid_log_c)

    df_tabla['CUADRANTE OPERATIVO'] = "Zona Estable"
    df_tabla.loc[cond_vacio, 'CUADRANTE OPERATIVO'] = "Alerta: Alta Amenaza / Vacío Operativo"
    df_tabla.loc[cond_foco, 'CUADRANTE OPERATIVO'] = "Foco Activo de Contención"
    df_tabla.loc[cond_control, 'CUADRANTE OPERATIVO'] = "Control Operativo / Interdicción"

    df_tabla['ZONAS ESPECIALES'] = np.where(df_tabla['nombre_pdet'] != "No aplica", "PDET", np.where(df_tabla['pnis'] == "True", "PNIS", "—"))

    df_vacios = df_tabla[df_tabla['CUADRANTE OPERATIVO'] == "Alerta: Alta Amenaza / Vacío Operativo"].copy()
    
    df_vacios_show = df_vacios[['departamento', 'municipio', 'sector', 'total_hechos_sector', 'capturas_sector', 'capturas_totales_muni', 'ratio_focalizacion_pct', 'ZONAS ESPECIALES']]
    df_vacios_show = df_vacios_show.sort_values(by='total_hechos_sector', ascending=False)
    
    df_ranking_show = df_tabla[['departamento', 'municipio', 'sector', 'ratio_focalizacion_pct', 'capturas_sector', 'capturas_totales_muni', 'total_hechos_sector', 'presion_ponderada', 'CUADRANTE OPERATIVO', 'ZONAS ESPECIALES']]
    df_ranking_show = df_ranking_show.sort_values(by=['ratio_focalizacion_pct', 'capturas_sector'], ascending=[False, False]).reset_index(drop=True)
    df_ranking_show.insert(0, '# RANK', range(1, len(df_ranking_show) + 1))

    tab1, tab2 = st.tabs([f"🚨 Alerta Vacíos Operativos  {len(df_vacios_show)}", f"📈 Ranking Especialización  {len(df_ranking_show)}"])

    with tab1:
        st.markdown("""
        <div class='alert-box-red'>
            <strong style='color: #b91c1c;'>🚨 Criterio de Alerta Temprana de Vacíos Operativos:</strong><br>
            <span style='color: #991b1b; font-size: 0.9rem;'>Municipios prioritarios donde el sector sufre hechos criminales recurrentes pero no se registran capturas o la respuesta operativa es marginal (vacío de control).</span>
        </div>
        """, unsafe_allow_html=True)#[cite: 1]
        st.dataframe(
            df_vacios_show, use_container_width=True, hide_index=True,
            column_config={
                "departamento": "DEPARTAMENTO", "municipio": "MUNICIPIO", "sector": "SECTOR AFECTADO",
                "total_hechos_sector": st.column_config.NumberColumn("HECHOS CRIMINALES", format="%d"),
                "capturas_sector": st.column_config.NumberColumn("CAPTURAS SECTOR", format="%d"),
                "capturas_totales_muni": st.column_config.NumberColumn("CAPTURAS TOTALES", format="%d"),
                "ratio_focalizacion_pct": st.column_config.NumberColumn("FOCALIZACIÓN (%)", format="%.1f%%"),
                "ZONAS ESPECIALES": "ZONAS ESPECIALES"
            }
        )

    with tab2:
        st.markdown("""
        <div class='alert-box-blue'>
            <strong style='color: #1d4ed8;'>📈 Criterio de Especialización Operativa:</strong><br>
            <span style='color: #1e3a8a; font-size: 0.9rem;'>Municipios ordenados descendentemente indicando el peso relativo que tiene este sector en la operatividad total del municipio.</span>
        </div>
        """, unsafe_allow_html=True)#[cite: 2]
        st.dataframe(
            df_ranking_show, use_container_width=True, hide_index=True,
            column_config={
                "# RANK": st.column_config.NumberColumn("# RANK", width="small"),
                "departamento": "DEPARTAMENTO", "municipio": "MUNICIPIO", "sector": "SECTOR",
                "ratio_focalizacion_pct": st.column_config.NumberColumn("FOCALIZACIÓN (%)", format="%.1f%%"),
                "capturas_sector": st.column_config.NumberColumn("CAPTURAS SECTOR", format="%d"),
                "capturas_totales_muni": st.column_config.NumberColumn("CAPTURAS TOTALES", format="%d"),
                "total_hechos_sector": st.column_config.NumberColumn("HECHOS SECTOR", format="%d"),
                "presion_ponderada": st.column_config.NumberColumn("PRESIÓN PONDERADA", format="%d"),
                "CUADRANTE OPERATIVO": "CUADRANTE OPERATIVO", "ZONAS ESPECIALES": "INSTITUCIONAL"
            }
        )
else:
    st.info("No hay datos suficientes para generar las tablas con los filtros actuales.")