import streamlit as st
from docxtpl import DocxTemplate
import io

# Configuración para que se vea bien en celulares
st.set_page_config(page_title="Generador de Documentos", layout="centered")

st.title("📄 Generador de Oficios")
st.write("Completa los datos y descarga tus documentos.")

# Formulario de entrada
with st.form("main_form"):
    nombre = st.text_input("Nombre Completo:")
    cedula = st.text_input("Cédula / ID:")
    ingresos = st.text_input("Monto de Ingresos:")
    institucion = st.text_input("Institución:")
    profesion = st.text_input("Profesión:")
    fecha = st.date_input("Fecha del Documento")
    
    submit = st.form_submit_button("GENERAR DOCUMENTOS")

if submit:
    if not nombre or not cedula:
        st.error("⚠️ Por favor, escribe al menos el nombre y la cédula.")
    else:
        try:
            # Datos que se reemplazarán en los Word
            contexto = {
                'nombre': nombre,
                'cedula': cedula,
                'ingresos': ingresos,
                'institucion': institucion,
                'profesion': profesion,
                'fecha': fecha.strftime("%d/%m/%Y")
            }

            # Procesar Documento 1: Certificación
            doc1 = DocxTemplate("certificacion.docx")
            doc1.render(contexto)
            out1 = io.BytesIO()
            doc1.save(out1)
            out1.seek(0)

            # Procesar Documento 2: Anexo
            doc2 = DocxTemplate("anexo.docx")
            doc2.render(contexto)
            out2 = io.BytesIO()
            doc2.save(out2)
            out2.seek(0)

            st.success("✅ ¡Documentos generados con éxito!")

            # Botones de descarga
            st.download_button(
                label="📥 Descargar Certificación",
                data=out1,
                file_name=f"Certificacion_{nombre}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            st.download_button(
                label="📥 Descargar Anexo",
                data=out2,
                file_name=f"Anexo_{nombre}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        except Exception as e:
            st.error(f"Error: Asegúrate de haber subido los archivos .docx con los nombres correctos. Detalle: {e}")
