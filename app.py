import streamlit as st
from docxtpl import DocxTemplate
import io
import re
from docx import Document

st.set_page_config(page_title="Generador Automático", layout="centered")

st.title("📄 Generador Inteligente")
st.write("La app detectará automáticamente los campos de tus plantillas.")

def extraer_etiquetas(archivos):
    etiquetas = set()
    for archivo in archivos:
        try:
            doc = Document(archivo)
            # Buscar en todos los párrafos
            for p in doc.paragraphs:
                encontrados = re.findall(r"\{\{(.*?)\}\}", p.text)
                for e in encontrados:
                    etiquetas.add(e.strip())
            # Buscar en todas las tablas
            for tabla in doc.tables:
                for fila in tabla.rows:
                    for celda in fila.cells:
                        encontrados = re.findall(r"\{\{(.*?)\}\}", celda.text)
                        for e in encontrados:
                            etiquetas.add(e.strip())
        except:
            pass
    return sorted(list(etiquetas))

# Intentar extraer etiquetas de tus archivos subidos
plantillas = ["certificacion.docx", "anexo.docx"]
lista_etiquetas = extraer_etiquetas(plantillas)

if not lista_etiquetas:
    st.error("No se detectaron etiquetas {{}} en los archivos. Revisa tus plantillas.")
else:
    with st.form("dynamic_form"):
        st.subheader("Completa los datos detectados:")
        datos_usuario = {}
        
        # Crear un campo de texto por cada etiqueta encontrada
        for etiqueta in lista_etiquetas:
            datos_usuario[etiqueta] = st.text_input(f"Escribe: {etiqueta}")
        
        boton = st.form_submit_button("GENERAR DOCUMENTOS")

    if boton:
        try:
            # Procesar Certificación
            doc1 = DocxTemplate("certificacion.docx")
            doc1.render(datos_usuario)
            out1 = io.BytesIO(); doc1.save(out1); out1.seek(0)
            
            # Procesar Anexo
            doc2 = DocxTemplate("anexo.docx")
            doc2.render(datos_usuario)
            out2 = io.BytesIO(); doc2.save(out2); out2.seek(0)
            
            st.success("✅ ¡Documentos listos!")
            st.download_button("📥 Descargar Certificación", out1, "Certificacion.docx")
            st.download_button("📥 Descargar Anexo", out2, "Anexo.docx")
        except Exception as e:
            st.error(f"Error al procesar: {e}")
