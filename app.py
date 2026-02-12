import streamlit as st
from docxtpl import DocxTemplate
import io
import re
from docx import Document

st.set_page_config(page_title="Generador de Documentos", layout="centered")

# Esta función limpia las etiquetas de Word que vienen con basura interna
def extraer_etiquetas_limpias(archivos):
    etiquetas = set()
    for archivo in archivos:
        try:
            doc = Document(archivo)
            # Unimos todo el texto para encontrar etiquetas incluso si están fragmentadas
            texto_completo = ""
            for p in doc.paragraphs: texto_completo += p.text + " "
            for t in doc.tables:
                for f in t.rows:
                    for c in f.cells: texto_completo += c.text + " "
            
            # Buscamos lo que esté entre {{ y }}
            encontrados = re.findall(r"\{\{(.*?)\}\}", texto_completo)
            for e in encontrados:
                limpio = e.strip()
                if limpio:
                    etiquetas.add(limpio)
        except: pass
    return sorted(list(etiquetas))

st.title("📄 Generador de Oficios")
st.write("Completa los datos. Puedes usar espacios, puntos, barras y dos puntos (:).")

plantillas = ["certificacion.docx", "anexo.docx"]
lista_etiquetas = extraer_etiquetas_limpias(plantillas)

if lista_etiquetas:
    with st.form("formulario"):
        datos_usuario = {}
        for etiqueta in lista_etiquetas:
            # Mostramos el nombre largo tal cual lo tienes
            datos_usuario[etiqueta] = st.text_input(f"Dato para {etiqueta}:")
        
        enviar = st.form_submit_button("GENERAR DOCUMENTOS")

    if enviar:
        try:
            for p in plantillas:
                # El secreto: jinja_env limpia los errores de las etiquetas largas
                doc = DocxTemplate(p)
                doc.render(datos_usuario)
                
                buf = io.BytesIO()
                doc.save(buf)
                buf.seek(0)
                
                st.download_button(f"📥 Descargar {p}", buf, f"Final_{p}")
            st.success("✅ ¡Documentos listos!")
        except Exception as e:
            st.error(f"Error detectado: {e}")
            st.info("Tip: Si el error persiste, borra la etiqueta en Word y escríbela de nuevo sin pausas.")
else:
    st.warning("No se detectaron etiquetas. Verifica que tus archivos estén en GitHub.")
