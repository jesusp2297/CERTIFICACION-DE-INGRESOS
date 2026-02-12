import streamlit as st
from docx import Document
import io
import re

st.set_page_config(page_title="Generador Final", layout="centered")

def extraer_etiquetas_simples(archivos):
    etiquetas = set()
    for archivo in archivos:
        try:
            doc = Document(archivo)
            for p in doc.paragraphs:
                encontrados = re.findall(r"\{\{(.*?)\}\}", p.text)
                for e in encontrados: etiquetas.add(e.strip())
            for t in doc.tables:
                for f in t.rows:
                    for c in f.cells:
                        encontrados = re.findall(r"\{\{(.*?)\}\}", c.text)
                        for e in encontrados: etiquetas.add(e.strip())
        except: pass
    return sorted(list(etiquetas))

def reemplazar_texto(doc, datos):
    # Reemplazar en párrafos
    for p in doc.paragraphs:
        for clave, valor in datos.items():
            if f"{{{{{clave}}}}}" in p.text:
                p.text = p.text.replace(f"{{{{{clave}}}}}", valor)
    # Reemplazar en tablas
    for tabla in doc.tables:
        for fila in tabla.rows:
            for celda in fila.cells:
                for clave, valor in datos.items():
                    if f"{{{{{clave}}}}}" in celda.text:
                        celda.text = celda.text.replace(f"{{{{{clave}}}}}", valor)

st.title("📄 Generador de Documentos (Modo Seguro)")
st.write("Esta versión ignora los errores técnicos y acepta nombres largos.")

plantillas = ["certificacion.docx", "anexo.docx"]
lista = extraer_etiquetas_simples(plantillas)

if lista:
    with st.form("form_seguro"):
        datos_usuario = {}
        for etiqueta in lista:
            datos_usuario[etiqueta] = st.text_input(f"Escribe {etiqueta}:")
        
        boton = st.form_submit_button("GENERAR")

    if boton:
        for p_nombre in plantillas:
            try:
                doc = Document(p_nombre)
                reemplazar_texto(doc, datos_usuario)
                
                output = io.BytesIO()
                doc.save(output)
                output.seek(0)
                
                st.download_button(f"📥 Descargar {p_nombre}", output, f"Listo_{p_nombre}")
            except Exception as e:
                st.error(f"Error con {p_nombre}: {e}")
        st.success("¡Hecho! Si algún campo no cambió, revisa que esté escrito igual en el Word.")
else:
    st.warning("Sube tus archivos Word a GitHub para empezar.")
