import streamlit as st
from docxtpl import DocxTemplate
import io
import re
from docx import Document

st.set_page_config(page_title="Generador Inteligente", layout="centered")

st.title("📄 Generador Inteligente")

def extraer_etiquetas(archivos):
    etiquetas = set()
    for archivo in archivos:
        try:
            doc = Document(archivo)
            # Buscar en párrafos y tablas
            fuentes = [p.text for p in doc.paragraphs]
            for tabla in doc.tables:
                for fila in tabla.rows:
                    for celda in fila.cells:
                        fuentes.append(celda.text)
            
            for texto in fuentes:
                # Esta expresión regular es más flexible
                encontrados = re.findall(r"\{\{\s*(.*?)\s*\}\}", texto)
                for e in encontrados:
                    # Limpiamos espacios y caracteres raros
                    limpio = e.strip().replace(" ", "_")
                    if limpio:
                        etiquetas.add(limpio)
        except:
            pass
    return sorted(list(etiquetas))

plantillas = ["certificacion.docx", "anexo.docx"]
lista_etiquetas = extraer_etiquetas(plantillas)

if not lista_etiquetas:
    st.warning("⚠️ No se detectaron etiquetas. Asegúrate de subir certificacion.docx y anexo.docx")
else:
    with st.form("dynamic_form"):
        st.subheader("Completa los datos:")
        datos_usuario = {}
        for etiqueta in lista_etiquetas:
            datos_usuario[etiqueta] = st.text_input(f"Ingresa {etiqueta}:")
        
        boton = st.form_submit_button("GENERAR DOCUMENTOS")

    if boton:
        try:
            # Procesar ambos archivos
            for nombre_p in plantillas:
                doc = DocxTemplate(nombre_p)
                # El render necesita las claves exactas como están en el Word
                doc.render(datos_usuario)
                out = io.BytesIO()
                doc.save(out)
                out.seek(0)
                st.download_button(f"📥 Descargar {nombre_p}", out, f"Final_{nombre_p}")
            
            st.success("✅ ¡Proceso completado!")
        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.info("Revisa que en el Word no uses tildes o espacios dentro de {{ }}")
