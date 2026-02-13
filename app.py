import streamlit as st
from docx import Document
import io
import re
import os

# Configuración optimizada para móviles
st.set_page_config(page_title="Certificador Pro", layout="centered")

# --- CONFIGURACIÓN DE ARCHIVOS FIJOS ---
PLANTILLAS_CONFIG = [
    "certificacion.docx",
    "anexo.docx"
]

def extraer_etiquetas_fijas(nombres_archivos):
    """Lee los archivos locales y extrae las etiquetas {{etiqueta}}"""
    etiquetas = set()
    for nombre in nombres_archivos:
        if os.path.exists(nombre):
            try:
                doc = Document(nombre)
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
            except Exception as e:
                st.error(f"Error leyendo {nombre}: {e}")
    return sorted(list(etiquetas))

def generar_documento(nombre_plantilla, datos):
    """Aplica los cambios a una plantilla y devuelve el buffer"""
    doc = Document(nombre_plantilla)
    for clave, valor in datos.items():
        buscar = f"{{{{{clave}}}}}"
        # Procesar párrafos
        for p in doc.paragraphs:
            if buscar in p.text:
                p.text = p.text.replace(buscar, valor)
        # Procesar tablas
        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    if buscar in celda.text:
                        for p_celda in celda.paragraphs:
                            p_celda.text = p_celda.text.replace(buscar, valor)
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output

# --- INTERFAZ ---
st.title("📄 GENERADOR RÁPIDO")
st.subheader("Certificación de Ingresos")
st.info("📱 Ideal para uso desde el celular. Llena los datos abajo.")

# Verificar si existen los archivos antes de empezar
archivos_presentes = [p for p in PLANTILLAS_CONFIG if os.path.exists(p)]

if not archivos_presentes:
    st.error("❌ No se encontraron las plantillas .docx en el servidor.")
    st.write("Asegúrate de que 'certificacion.docx' y 'anexo.docx' estén en la misma carpeta que app.py.")
else:
    # Extraer etiquetas de los archivos locales automáticamente
    lista_unica = extraer_etiquetas_fijas(archivos_presentes)

    if lista_unica:
        # Formulario optimizado para móvil
        with st.form("datos_ingreso"):
            datos_usuario = {}
            for etiqueta in lista_unica:
                label = etiqueta.replace("_", " ").upper()
                datos_usuario[etiqueta] = st.text_input(label, placeholder=f"Escribe {label.lower()}...")
            
            st.write("---")
            boton_generar = st.form_submit_button("🚀 GENERAR DOCUMENTOS", use_container_width=True)

        # La lógica de generación debe estar al mismo nivel de indentación que el 'with st.form'
        if boton_generar:
            st.success("✨ Documentos listos para descargar:")
            
            for p_nombre in archivos_presentes:
                try:
                    archivo_final = generar_documento(p_nombre, datos_usuario)
                    
                    st.download_button(
                        label=f"⬇️ DESCARGAR {p_nombre.replace('.docx', '').upper()}",
                        data=archivo_final,
                        file_name=f"LISTO_{p_nombre}",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error al procesar {p_nombre}: {e}")
    else:
        st.warning("No se encontraron etiquetas {{...}} en las plantillas.")
