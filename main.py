import streamlit as st
from PIL import Image
from util import classify_image
from datetime import datetime
import base64
from fpdf import FPDF

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = "Home"

def main():
    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = ["Home", "Upload Image", "About", "Contact"]
    choice = st.sidebar.selectbox("Select Page", pages, index=pages.index(st.session_state.page))

    if choice:
        st.session_state.page = choice

    # Navigate based on session state
    if st.session_state.page == "Home":
        show_home_page()
    elif st.session_state.page == "Upload Image":
        show_upload_page()
    elif st.session_state.page == "About":
        show_about_page()
    elif st.session_state.page == "Contact":
        show_contact_page()

def show_home_page():
    st.title("Welcome to Pneumonia Detection Using Chest X-Ray Images")
    st.write("""
    This website uses a machine learning model to predict pneumonia from chest X-ray images. 
    Please navigate to the "Upload Image" section to get started.
    """)
    if st.button("Go to Upload Page"):
        st.session_state.page = "Upload Image"
        st.experimental_rerun()

def show_upload_page():
    st.title("Pneumonia Detection Using Chest X-Ray Images")
    st.header("Provide Patient Information and Upload a Chest X-ray Image")

    # Use columns for horizontal layout
    col1, col2 = st.columns(2)

    # Add input fields for patient information in the first column
    with col1:
        patient_name = st.text_input("Patient Name")
        age = st.text_input("Age")  # Age input with default blank state
        sex = st.radio("Sex", options=["Male", "Female", "Other"])

    # Add input fields for patient information in the second column
    with col2:
        address = st.text_area("Address")
        diagnosis_date = st.date_input("Diagnosis Date", value=datetime.today())

    # Upload image
    uploaded_file = st.file_uploader("Choose a chest X-ray image ...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.write("")
        st.write("Classifying...")
        class_label, confidence = classify_image(image)
        
        if class_label == "PNEUMONIA":
            st.markdown(f"<h2 style='color: red;'>Prediction: {class_label}</h2>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='color: green;'>Prediction: {class_label}</h2>", unsafe_allow_html=True)
        
        st.markdown(f"<h3>Confidence: {confidence * 100:.2f}%</h3>", unsafe_allow_html=True)
        st.write("")
        show_result_explanation(class_label)
        
        # Generate and download the classification report automatically
        classification_report = generate_classification_report(patient_name, age, sex, address, diagnosis_date, class_label, confidence)
        filename = f"{patient_name}_classification_report.pdf"  # Set filename with patient's name for PDF
        
        # Display download link for PDF report
        st.markdown(download_pdf_button(classification_report, filename), unsafe_allow_html=True)

        # Display classification report in text format
        st.code(classification_report, language='txt')

    else:
        st.write("Please upload an image file.")

def show_result_explanation(class_label):
    if class_label == "PNEUMONIA":
        st.write("This X-ray image is classified as Pneumonia.")
        st.write("Please consult a healthcare professional for further evaluation and treatment.")
        st.write("Based on the diagnosis, here are some initial steps the patient may take:")
        st.write("- Seek medical attention immediately")
        st.write("- Follow the prescribed treatment plan")
        st.write("- Get plenty of rest")
        st.write("- Stay hydrated")
        st.write("- Avoid close contact with others to prevent spreading the infection")
    else:
        st.write("This X-ray image is classified as Normal.")

def generate_classification_report(patient_name, age, sex, address, diagnosis_date, class_label, confidence):
    # Create PDF document
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Patient Information Section
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, txt="Patient Information", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Name: {patient_name}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Age: {age}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Sex: {sex}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Address: {address}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Diagnosis Date: {diagnosis_date.strftime('%Y-%m-%d')}", ln=True, align='L')
    pdf.ln()

    # Classification Result Section
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, txt="Classification Result", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Prediction: {class_label}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Confidence: {confidence * 100:.2f}%", ln=True, align='L')
    pdf.ln()

    # Recommendations Section based on classification
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, txt="Recommendations", ln=True, align='L')
    pdf.set_font("Arial", size=12)

    if class_label == "PNEUMONIA":
        pdf.multi_cell(200, 10, txt="This X-ray image is classified as Pneumonia. Please consult a healthcare professional for further evaluation and treatment.")
        pdf.multi_cell(200, 10, txt="Based on the diagnosis, here are some initial steps the patient may take:")
        pdf.multi_cell(200, 10, txt="- Seek medical attention immediately")
        pdf.multi_cell(200, 10, txt="- Follow the prescribed treatment plan")
        pdf.multi_cell(200, 10, txt="- Get plenty of rest and stay hydrated")
        pdf.multi_cell(200, 10, txt="- Avoid close contact with others to prevent spreading the infection")
    else:
        pdf.multi_cell(200, 10, txt="This X-ray image is classified as Normal.")

    pdf.ln()

    # Closing message
    pdf.multi_cell(200, 10, txt="Please consult a healthcare professional for further evaluation and treatment if necessary.")

    # Save PDF to a temporary file
    temp_file = f"./{patient_name}_classification_report.pdf"
    pdf.output(temp_file)

    # Read PDF content to return
    with open(temp_file, "rb") as file:
        pdf_content = file.read()

    return pdf_content

def download_pdf_button(pdf_content, filename="classification_report.pdf"):
    # Function to generate a download link for the PDF classification report
    b64 = base64.b64encode(pdf_content).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Click here to download the classification report as PDF</a>'
    return href

if __name__ == "__main__":
    main()
