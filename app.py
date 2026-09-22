import streamlit as st
import pandas as pd
import PyPDF2
import io
import base64
import os

# पेज सेटिंग्ज
st.set_page_config(page_title="12th Board Form Verification", page_icon="📄", layout="centered")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Students_Password_Data.xlsx")
        df['Form_Number'] = df['Form_Number'].astype(str).str.zfill(4)
        df['Password'] = df['Password'].astype(str)
        return df
    except Exception as e:
        st.error("Excel फाईल सापडली नाही. कृपया आधी create_excel.py रन करा.")
        return pd.DataFrame()

df = load_data()

st.title("📄 इ. १२ वी बोर्ड फॉर्म पडताळणी")
st.info("विद्यार्थ्यांनी आपला फॉर्म नंबर (उदा. 0001) आणि सरांनी दिलेला ४-अंकी पासवर्ड टाकावा.")

col1, col2 = st.columns(2)
with col1:
    form_no_input = st.text_input("फॉर्म नंबर (Form Number)")
with col2:
    password_input = st.text_input("पासवर्ड (Password)", type="password")

if st.button("फॉर्म पहा", type="primary"):
    if form_no_input and password_input:
        student = df[(df['Form_Number'] == form_no_input.strip()) & (df['Password'] == password_input.strip())]
        
        if not student.empty:
            student_name = student.iloc[0]['Student_Name']
            st.success(f"✅ स्वागत आहे, **{student_name}**! तुमचा फॉर्म खाली उपलब्ध आहे.")
            
            try:
                pdf_path = "12th_Final_Smart_Merged_Document.pdf" 
                student_index = int(form_no_input) - 1
                page_start = student_index * 2
                page_end = page_start + 1
                
                with open(pdf_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    writer = PyPDF2.PdfWriter()
                    
                    if page_start < len(reader.pages):
                        writer.add_page(reader.pages[page_start])
                    if page_end < len(reader.pages):
                        writer.add_page(reader.pages[page_end])
                    
                    pdf_bytes = io.BytesIO()
                    writer.write(pdf_bytes)
                    pdf_bytes.seek(0)
                    
                    # --- 1. फॉर्म Preview दाखवणे ---
                    st.markdown("### तुमचा फॉर्म खाली पहा:")
                    base64_pdf = base64.b64encode(pdf_bytes.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                    
                    st.info("💡 सूचना: काही मोबाईलमध्ये वरील फॉर्म डायरेक्ट दिसत नाही. तसे झाल्यास खालील 'डाउनलोड करा' बटणाचा वापर करा.")
                    
                    # डाउनलोड करण्यासाठी फाईल पुन्हा सेट करणे
                    pdf_bytes.seek(0)
                    
                    # --- 2. डाउनलोड बटण ---
                    st.download_button(
                        label="📥 माझा फॉर्म डाउनलोड करा",
                        data=pdf_bytes,
                        file_name=f"Board_Form_{form_no_input}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error("PDF फाईल लोड करताना अडचण आली.")
        else:
            st.error("❌ चुकीचा फॉर्म नंबर किंवा पासवर्ड. कृपया पुन्हा तपासा.")
    else:
        st.warning("⚠️ कृपया फॉर्म नंबर आणि पासवर्ड दोन्ही रकाने भरा.")

# --- 3. चुका नोंदवण्यासाठी फीडबॅक फॉर्म (Google Form) ---
st.write("---")
st.subheader("📝 फॉर्ममध्ये काही चूक आहे का?")
st.info("जर तुमच्या नावात, विषयात, जन्मतारखेत किंवा इतर माहितीत काही चूक असेल, तर खालील लिंकवर क्लिक करून माहिती सबमिट करा. ही माहिती थेट सरांना मिळेल.")

# येथे तुमच्या Google Form ची लिंक टाका
https://forms.gle/hXDkhdJfPZjNCcwA7तुमची_गुगल_फॉर्म_लिंक_इथे_टाका"

st.markdown(f"[👉 येथे क्लिक करून तुमची चूक नोंदवा]({google_form_link})", unsafe_allow_html=True)