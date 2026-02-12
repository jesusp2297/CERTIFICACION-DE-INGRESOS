import streamlit as st
from docx import Document
import io
import re

# Optimización para móvil: layout wide ayuda a usar mejor el ancho de pantalla
st.set_page_config(page_title="Generador Pro", layout="centered")

def extraer_etiquetas_sin_repetir(archivos):
    etiquetas = set()
    for archivo in archivos:
        try:
            doc = Document(archivo)
            # Buscar en párrafos
            for p in doc.paragraphs:
                encontrados = re.findall(r"\{\{(.*?)\}\}", p.text)
                for e in encontrados: etiquetas.add(e.strip())
            # Buscar en tablas
            for t in doc.tables:
                for f in t.rows:
                    for c in f.cells:
                        encontrados = re.findall(r"\{\{(.*?)\}\}", c.text)
                        for e in encontrados: etiquetas.add(e.strip())
        except: pass
    return sorted(list(etiquetas))

def reemplazar_manteniendo_formato(doc, datos):
    """
    Busca y reemplaza etiquetas manteniendo negritas, fuentes y colores.
    """
    for clave, valor in datos.items():
        buscar = f"{{{{{clave}}}}}"
        # Reemplazar en párrafos
        for p in doc.paragraphs:
            if buscar in p.text:
                for run in p.runs:
                    if buscar in run.text:
                        run.text = run.text.replace(buscar, valor)
        # Reemplazar en tablas
        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    for p_celda in celda.paragraphs:
                        if buscar in p_celda.text:
                            for run in p_celda.runs:
                                if buscar in run.text:
                                    run.text = run.text.replace(buscar, valor)

# --- INTERFAZ MÓVIL ---
st.title("📄 DATOS DEL CLIENTE")
st.markdown("---") # Línea separadora para orden visual

plantillas = ["certificacion.docx", "anexo.docx"]
lista_unica = extraer_etiquetas_sin_repetir(plantillas)

if lista_unica:
    # Usamos un contenedor con borde para que se vea mejor en móviles
    with st.container():
        with st.form("form_seguro"):
            st.subheader("📝 Complete la Información")
            datos_usuario = {}
            
            # En móvil es mejor una casilla debajo de la otra (por defecto)
            for etiqueta in lista_unica:
                label_bonito = etiqueta.replace("_", " ").upper()
                datos_usuario[etiqueta] = st.text_input(label_bonito, placeholder=f"Escriba aquí...")
            
            # Botón grande para fácil acceso táctil
            boton = st.form_submit_button("🚀 GENERAR DOCUMENTOS", use_container_width=True)

    if boton:
        st.divider()
        # En móvil, botones de descarga uno al lado del otro si son cortos
        col1, col2 = st.columns(2)
        
        for i, p_nombre in enumerate(plantillas):
            try:
                doc = Document(p_nombre)
                reemplazar_manteniendo_formato(doc, datos_usuario)
                
                output = io.BytesIO()
                doc.save(output)
                output.seek(0)
                
                # Turno de cada botón en su columna
                if i == 0:
                    col1.download_button(f"📥 CERTIFICACIÓN", output, f"Certificacion_{p_nombre}", use_container_width=True)
                else:
                    col2.download_button(f"📥 ANEXO", output, f"Anexo_{p_nombre}", use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error: {e}")
        
        st.balloons() # Animación de éxito para confirmar que terminó
else:
    st.warning("⚠️ No se detectaron etiquetas. Verifique sus archivos en GitHub.")
