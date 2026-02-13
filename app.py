import streamlit as st
from docx import Document
import io
import re

# Configuración de página
st.set_page_config(page_title="Generador Pro", layout="centered")

def extraer_etiquetas_del_doc(archivo_bytes):
    """
    Lee un archivo en memoria y extrae las etiquetas {{variable}}.
    Retorna un set de etiquetas encontradas.
    """
    etiquetas = set()
    try:
        doc = Document(archivo_bytes)
        
        # 1. Buscar en párrafos
        for p in doc.paragraphs:
            # Usamos regex para encontrar {{algo}}
            encontrados = re.findall(r"\{\{(.*?)\}\}", p.text)
            for e in encontrados:
                etiquetas.add(e.strip())
        
        # 2. Buscar en tablas
        for t in doc.tables:
            for row in t.rows:
                for cell in row.cells:
                    # En tablas, el texto también puede estar en párrafos dentro de celdas
                    for p in cell.paragraphs:
                        encontrados = re.findall(r"\{\{(.*?)\}\}", p.text)
                        for e in encontrados:
                            etiquetas.add(e.strip())
    except Exception as e:
        st.error(f"Error leyendo el archivo: {e}")
    
    return etiquetas

def reemplazar_texto(doc, datos):
    """
    Reemplaza las claves por valores en el documento.
    NOTA: Al asignar p.text, se puede perder formato (negrita/color) 
    si el estilo no estaba aplicado a todo el párrafo.
    """
    for clave, valor in datos.items():
        buscar = f"{{{{{clave}}}}}" # Esto genera string "{{clave}}"
        
        if not valor:
            valor = "" # Evitar errores si el campo está vacío

        # Reemplazo en párrafos normales
        for p in doc.paragraphs:
            if buscar in p.text:
                # inline=True intenta preservar mejor el estilo
                p.text = p.text.replace(buscar, valor)

        # Reemplazo en tablas
        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    for p in celda.paragraphs:
                        if buscar in p.text:
                            p.text = p.text.replace(buscar, valor)
    return doc

# --- INTERFAZ DE USUARIO ---

st.title("📄 DATOS DEL CLIENTE")
st.markdown("""
Sube tus plantillas de Word (`.docx`). El sistema detectará automáticamente
las variables entre llaves dobles, por ejemplo: `{{nombre}}`, `{{cedula}}`.
""")

# 1. Widget de carga de archivos (Reemplaza las rutas fijas)
archivos_subidos = st.file_uploader(
    "Cargar Plantillas (.docx)", 
    type=["docx"], 
    accept_multiple_files=True
)

if archivos_subidos:
    # Set para guardar todas las etiquetas únicas de todos los archivos
    etiquetas_globales = set()

    # 2. Fase de Análisis: Extraer etiquetas
    for archivo in archivos_subidos:
        # Importante: seek(0) asegura que leemos desde el principio
        archivo.seek(0) 
        tags_doc = extraer_etiquetas_del_doc(archivo)
        etiquetas_globales.update(tags_doc)

    lista_unica = sorted(list(etiquetas_globales))

    if lista_unica:
        st.divider()
        st.subheader("📝 Completar Información")
        
        with st.form("form_final"):
            datos_usuario = {}
            # Crear columnas para que el formulario sea más compacto
            cols = st.columns(2)
            
            for i, etiqueta in enumerate(lista_unica):
                label_bonito = etiqueta.replace("_", " ").upper()
                # Alternar columnas
                col_actual = cols[i % 2]
                datos_usuario[etiqueta] = col_actual.text_input(label_bonito)
            
            st.warning("⚠️ Nota: Si tu plantilla tiene palabras en **negrita** o *cursiva* justo donde está la variable, el formato podría perderse al reemplazar.")
            boton = st.form_submit_button("🚀 GENERAR DOCUMENTOS", use_container_width=True)

        # 3. Fase de Generación y Descarga
        if boton:
            st.success("✅ ¡Archivos generados correctamente!")
            st.subheader("Descargas:")
            
            # Usamos columnas para los botones de descarga
            cols_descarga = st.columns(len(archivos_subidos))

            for idx, archivo_orig in enumerate(archivos_subidos):
                try:
                    # Rebobinamos el archivo original antes de procesarlo de nuevo
                    archivo_orig.seek(0)
                    doc_final = Document(archivo_orig)
                    
                    # Aplicar reemplazos
                    reemplazar_seguro = reemplazar_texto(doc_final, datos_usuario)
                    
                    # Guardar en memoria (buffer)
                    buffer_salida = io.BytesIO()
                    doc_final.save(buffer_salida)
                    buffer_salida.seek(0)
                    
                    nombre_descarga = f"FINAL_{archivo_orig.name}"
                    
                    # Botón de descarga
                    cols_descarga[idx].download_button(
                        label=f"📥 {archivo_orig.name}",
                        data=buffer_salida,
                        file_name=nombre_descarga,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"btn_{idx}"
                    )
                except Exception as e:
                    st.error(f"Error procesando {archivo_orig.name}: {e}")

    else:
        st.info("No se detectaron etiquetas `{{variable}}` en los archivos subidos. Revisa el formato.")

else:
    st.info("Esperando archivos... Por favor sube tus plantillas .docx")
