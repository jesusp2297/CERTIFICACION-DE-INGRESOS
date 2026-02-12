import streamlit as st
from docx import Document
import io
import re

st.set_page_config(page_title="Generador Pro", layout="centered")

def extraer_etiquetas_sin_repetir(archivos):
    etiquetas = set()
    for archivo in archivos:
        try:
            doc = Document(archivo)
            # Buscamos en el texto plano del párrafo para no fallar
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

def reemplazar_seguro(doc, datos):
    """
    Esta función une fragmentos divididos de Word antes de reemplazar
    para asegurar que no se salte ninguna etiqueta.
    """
    for clave, valor in datos.items():
        buscar = f"{{{{{clave}}}}}"
        
        # Procesar párrafos
        for p in doc.paragraphs:
            if buscar in p.text:
                # El truco: reemplazamos en el texto completo del párrafo
                # pero intentamos preservar el formato del primer run
                p.text = p.text.replace(buscar, valor)

        # Procesar tablas
        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    if buscar in celda.text:
                        for p_celda in celda.paragraphs:
                            p_celda.text = p_celda.text.replace(buscar, valor)

st.title("📄 DATOS DEL CLIENTE")
st.write("certificacion de ingresos")

plantillas = ["certificacion.docx", "anexo.docx"]
lista_unica = extraer_etiquetas_sin_repetir(plantillas)

if lista_unica:
    with st.form("form_final"):
        datos_usuario = {}
        for etiqueta in lista_unica:
            label_bonito = etiqueta.replace("_", " ").upper()
            datos_usuario[etiqueta] = st.text_input(label_bonito)
        
        boton = st.form_submit_button("🚀 GENERAR Y DESCARGAR", use_container_width=True)

    if boton:
        # Contenedor para los botones de descarga
        st.subheader("✅ ¡Listo! Descarga tus archivos:")
        cols = st.columns(len(plantillas))
        
        for i, p_nombre in enumerate(plantillas):
            try:
                doc = Document(p_nombre)
                reemplazar_seguro(doc, datos_usuario)
                
                output = io.BytesIO()
                doc.save(output)
                output.seek(0)
                
                cols[i].download_button(
                    label=f"📥 {p_nombre.upper()}",
                    data=output,
                    file_name=f"FINAL_{p_nombre}",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error en {p_nombre}: {e}")
else:
    st.warning("No se detectaron etiquetas. Verifica tus archivos.")
        )
