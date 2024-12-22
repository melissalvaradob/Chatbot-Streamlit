import streamlit as st
from langchain.chat_models import ChatOpenAI
from PIL import Image
import os
from PyPDF2 import PdfReader 
from langchain.prompts.chat import ChatPromptTemplate

st.set_page_config(page_title = "Chatbot usando Langchain, OpenAI y Streamlit", page_icon = "https://python.langchain.com/img/favicon.ico")
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, 'logos.png')

with st.sidebar:
    # Prompt Template
    template = """
        Eres un asistente experto en temas relacionados a contabilidad, usando información reciente y vigente hasta la fecha de hoy en Perú, 
        basándote en las normativas y aspectos legales de la constitución peruana.
        Tu tarea es ayudar a los usuarios con preguntas relacionadas a estos temas.
    """
    human_template = "{text}"

    # Plantilla
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_template)
    ])


    st.title("Examen Final DMC: Chatbot Personalizado")

    model = st.selectbox('Eliga el modelo',
        (
            'gpt-3.5-turbo', 
            'gpt-3.5-turbo-16k', 
            'gpt-4'
        ), 
        key = "model"
    )

   # Cargar y mostrar la imagen
    try:
        image = Image.open(image_path)
        st.image(image, caption='OpenAI, Langchain y Streamlit')
    except FileNotFoundError:
        st.error("El archivo 'logos.png' no se encontró. Asegúrate de que está en el directorio correcto.")

    st.markdown(
        """
        Integrando OpenAI con Streamlit y Langchain.
    """
    )

def clear_chat_history():
    st.session_state.messages = [{"role" : "assistant", "content": msg_chatbot}]

openai_api_key = st.sidebar.text_input("Ingrese tu API Key de OpenAI y dale Enter para habilitar el chatbot", key = "chatbot_api_key", type = "password")
st.sidebar.button('Limpiar historial de chat', on_click = clear_chat_history)

msg_chatbot = """
        Hola, soy tu asistente personal conectado a la API de ChatGPT 
        ¿Cómo puedo ayudarte? Aquí te dejo algunas opciones para empezar.
        

        ¿Cómo funcionas?
        Hazme un análisis de la variación del TC Dólar.
        Elabora un gráfico comparativo de los sectores más impactantes en el mercado.
"""

# Se envía el prompt de usuario al modelo de GPT-3.5-Turbo para que devuelva una respuesta
def get_response_openai(prompt, model):
    
    llm = ChatOpenAI(
        openai_api_key = openai_api_key,
        model_name = model,
        temperature = 0
    )

    return llm.predict(prompt)

# Función para procesar el archivo PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

#Si no existe la variable messages, se crea la variable y se muestra por defecto el mensaje de bienvenida al chatbot.
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content" : msg_chatbot}]

# Muestra todos los mensajes de la conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if openai_api_key:
    with st.sidebar:
        # Subir archivo PDF solo si se ha ingresado la API Key
        uploaded_file = st.file_uploader("Sube un archivo PDF", type=["pdf"])  # En el sidebar

    # Barra de texto de entrada fuera del sidebar, visible siempre
    prompt = st.chat_input("Ingresa tu pregunta o sube un archivo PDF:")

    if uploaded_file:
        with st.chat_message("user"):
            st.write("He subido un archivo PDF para que lo analices.")
        try:
            with st.spinner("Procesando el archivo PDF..."):
                pdf_text = extract_text_from_pdf(uploaded_file)

            st.session_state.messages.append({"role": "user", "content": "He subido un archivo PDF para que lo analices."})
            
            # Generar respuesta basada en el contenido del PDF
            if openai_api_key:
                prompt = f"El siguiente es el contenido del archivo PDF:\n{pdf_text}\n\nPor favor, analízalo y dame un resumen breve y conciso o responde preguntas basadas en el contenido."
                with st.chat_message("assistant"):
                    response = get_response_openai(prompt, model)
                    st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Hubo un error procesando el archivo: {e}")

    elif prompt:
        # Procesar entrada del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Generar respuesta si el último mensaje no es de un "assistant"
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Esperando respuesta, dame unos segundos..."):
                    response = get_response_openai(prompt, model)
                    st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})