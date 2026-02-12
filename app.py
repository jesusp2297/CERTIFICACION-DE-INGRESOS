import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Certificador PDF Pro", page_icon="⚖️", layout="centered")

# Estilo para mejorar la UI
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

class PDF(FPDF):
    def header(self):
        # Aquí puedes agregar un logo si lo tienes: self.image('logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'CERTIFICACIÓN DE INGRESOS', border=False, ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def generar_pdf(datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Cuerpo del documento
    fecha_hoy = datetime.now().strftime("%d de %B de %Y")
    
    texto_certificacion = f"""
    A QUIEN PUEDA INTERESAR:
    
    Yo, {datos['contador']}, identificado con cédula de ciudadanía No. {datos['id_contador']}, 
    en mi calidad de Contador Público con Tarjeta Profesional No. {datos['tp']}, 
    CERTIFICO QUE:
    
    El(la) Sr(a). {datos['nombre_cliente']}, identificado(a) con {datos['tipo_id']} No. {datos['id_cliente']}, 
    percibe ingresos mensuales por un valor de {datos['monto_letras']} ({datos['monto_numeros']}), 
    provenientes de su actividad como {datos['actividad']}.
    
    La presente certificación se expide a solicitud del interesado en la ciudad de {datos['ciudad']}, 
    el día {fecha_hoy}.
    """
    
    pdf.multi_cell(0, 10, texto_certificacion)
    pdf.ln(20)
    
    # Espacio para firma
    pdf.cell(0, 10, "__________________________", ln=True, align='L')
    pdf.cell(0, 10, f"{datos['contador']}", ln=True, align='L')
    pdf.cell(0, 10, f"T.P. No. {datos['tp']}", ln=True, align='L')
    
    return pdf.output()

# --- INTERFAZ DE USUARIO ---
st.title("🏛️ Generador de Certificaciones Oficiales")
st.write("Complete la información para generar el PDF de inmediato.")

with st.container():
    with st.form("form_pdf"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Datos del Contador")
            contador = st.text_input("Nombre Completo del Contador")
            id_contador = st.text_input("Cédula del Contador")
            tp = st.text_input("Tarjeta Profesional No.")
            ciudad = st.text_input("Ciudad de Expedición")

        with col2:
            st.subheader("Datos del Cliente")
            nombre_cliente = st.text_input("Nombre del Cliente")
            id_cliente = st.text_input("Cédula/ID del Cliente")
            tipo_id = st.selectbox("Tipo de Documento", ["C.C.", "C.E.", "Pasaporte"])
            actividad = st.text_input("Actividad Económica")

        st.subheader("Información Financiera")
        c3, c4 = st.columns([1, 2])
        monto_numeros = c3.text_input("Monto (Números)", placeholder="$ 0.000")
        monto_letras = c4.text_input("Monto (Letras)", placeholder="Ej: Cinco millones de pesos")

        submit = st.form_submit_button("✨ GENERAR PDF PROFESIONAL", use_container_width=True)

if submit:
    if not contador or not nombre_cliente:
        st.error("Por favor, rellene los campos obligatorios.")
    else:
        # Recopilar datos
        datos = {
            "contador": contador, "id_contador": id_contador, "tp": tp,
            "nombre_cliente": nombre_cliente, "id_cliente": id_cliente,
            "tipo_id": tipo_id, "actividad": actividad, "ciudad": ciudad,
            "monto_numeros": monto_numeros, "monto_letras": monto_letras
        }
        
        pdf_bytes = generar_pdf(datos)
        
        st.success("¡Documento generado exitosamente!")
        st.download_button(
            label="📥 DESCARGAR CERTIFICACIÓN (PDF)",
            data=pdf_bytes,
            file_name=f"Certificacion_{nombre_cliente.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
