import streamlit as st
from docx import Document
import io
import re

st.set_page_config(page_title="Generador Final", layout="centered")

def extraer_etiquetas_sin_repetir(archivos):
    # Usamos un set() para que no se guarden duplicados
    etiquetas = set()
    for archivo in archivos:
        try:
            doc = Document(archivo)
            # Buscar en párrafos
            for p in doc.paragraphs:
                encontrados = re.findall(r"\{\{(.*?)\}\}", p.text)
                for e in encontrados: 
                    etiquetas.add(e.strip()) # .add() ignora si ya existe
            # Buscar en tablas
            for t in doc.tables:
                for f in t.rows:
                    for c in f.cells:
                        encontrados = re.findall(r"\{\{(.*?)\}\}", c.text)
                        for e in encontrados: 
                            etiquetas.add(e.strip())
        except: pass
    return sorted(list(etiquetas)) # Lo devolvemos ordenado alfabéticamente

def reemplazar_texto(doc, datos):
    for p in doc.paragraphs:
        for clave, valor in datos.items():
            if f"{{{{{clave}}}}}" in p.text:
                p.text = p.text.replace(f"{{{{{clave}}}}}", valor)
    for tabla in doc.tables:
        for fila in tabla.rows:
            for celda in fila.cells:
                for clave, valor in datos.items():
                    if f"{{{{{clave}}}}}" in celda.text:
                        celda.text = celda.text.replace(f"{{{{{clave}}}}}", valor)

st.title("📄 Generador de Documentos")
st.write("Ahora con casillas únicas (sin repetidos).")

plantillas = ["certificacion.docx", "anexo.docx"]
# Aquí llamamos a la nueva función "limpia"
lista_unica = extraer_etiquetas_sin_repetir(plantillas)

if lista_unica:
    with st.form("form_seguro"):
        datos_usuario = {}
        for etiqueta in lista_unica:
            # Creamos una sola casilla por cada etiqueta diferente
            label_bonito = etiqueta.replace("_", " ").capitalize()
            datos_usuario[etiqueta] = st.text_input(f"{label_bonito}:")
        
        boton = st.form_submit_button("GENERAR DOCUMENTOS")

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
        st.success("¡Hecho! Los datos se aplicaron a todos los documentos.")
else:
    st.warning("Sube tus archivos Word a GitHub para empezar.")
