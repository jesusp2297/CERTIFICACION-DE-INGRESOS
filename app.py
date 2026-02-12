import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Certificador PDF Pro", page_icon="⚖️", layout="centered")

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'CERTIFICACION DE INGRESOS', border=False, ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def generar_pdf(datos):
    # Usamos 'latin-1' para compatibilidad básica con tildes y ñ
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    fecha_hoy = datetime.now().strftime("%d de %B de %Y")
    
    # Texto formateado (sin usar f-strings complejos para evitar errores de codificación)
    cuerpo = (
        f"A QUIEN PUEDA INTERESAR:\n\n"
        f"Yo, {datos['contador']}, identificado con cedula de ciudadania No. {datos['id_contador']}, "
        f"en mi calidad de Contador Publico con Tarjeta Profesional No. {datos['tp']}, "
        f"CERTIFICO QUE:\n\n"
        f"El(la) Sr(a). {datos['nombre_cliente']}, identificado(a) con {datos['tipo_id']} No. {datos['id_cliente']}, "
        f"percibe ingresos mensuales por un valor de {datos['monto_letras']} ({datos['monto_numeros']}), "
        f"provenientes de su actividad como {datos['actividad']}.\n\n"
        f"La presente certificacion se expide a solicitud del interesado en la ciudad de {datos['ciudad']}, "
        f"el dia {fecha_hoy}."
    )
    
    pdf.multi_cell(0, 10, cuerpo.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(20)
    
    # Espacio para firma
    pdf.cell(0, 10, "__________________________", ln=True)
    pdf.cell(0, 10, datos['contador'], ln=True)
    pdf.cell(0, 10, f"T.P. No. {datos['tp']}", ln=True)
    
    return pdf.output()

# --- INTERFAZ ---
st.title("🏛️ Generador de Certificaciones")

with st.form("form_pdf"):
    col1, col2 = st.columns(2)
    with col1:
        contador = st.text_input("Nombre del Contador")
        id_contador = st.text_input("Cédula Contador")
        tp = st.text_input("Tarjeta Profesional")
    with col2:
        nombre_cliente = st.text_input("Nombre del Cliente")
        id_cliente = st.text_input("ID Cliente")
        tipo_id = st.selectbox("Tipo ID", ["C.C.", "C.E.", "NIT"])
    
    actividad = st.text_input("Actividad Económica")
    ciudad = st.text_input("Ciudad")
    
    c3, c4 = st.columns(2)
    monto_numeros = c3.text_input("Monto ($)")
    monto_letras = c4.text_input("Monto (Letras)")
    
    enviar = st.form_submit_button("GENERAR PDF", use_container_width=True)

if enviar:
    if not contador or not nombre_cliente:
        st.warning("Por favor rellena los campos principales.")
    else:
        info = {
            "contador": contador, "id_contador": id_contador, "tp": tp,
            "nombre_cliente": nombre_cliente, "id_cliente": id_cliente,
            "tipo_id": tipo_id, "actividad": actividad, "ciudad": ciudad,
            "monto_numeros": monto_numeros, "monto_letras": monto_letras
        }
        pdf_res = generar_pdf(info)
        st.success("✅ PDF generado.")
        st.download_button(
            label="📥 Descargar PDF",
            data=pdf_res,
            file_name="Certificacion.pdf",
            mime="application/pdf"
        )
