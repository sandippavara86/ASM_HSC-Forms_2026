import streamlit as st
import pandas as pd
import PyPDF2
import fitz  # PyMuPDF (PDF चे फोटो करण्यासाठी)
import io
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
            st.success(f"✅ स्वागत आहे, **{student_name}**! तुमचा फॉर्म खाली पाहण्यासाठी उपलब्ध आहे.")
            
            try:
                pdf_path = "12th_Final_Smart_Merged_Document.pdf" 
                student_index = int(form_no_input) - 1
                page_start = student_index * 2
                page_end = page_start + 1
                
                # --- PDF चे थेट स्क्रीनवर फोटो (Preview) दाखवणे ---
                doc = fitz.open(pdf_path)
                
                st.markdown("### 📱 तुमचा फॉर्म खाली पहा:")
                
                for i, p_num in enumerate([page_start, page_end]):
                    if p_num < len(doc):
                        page = doc[p_num]
                        pix = page.get_pixmap(dpi=150)  # उच्च दर्जाची क्लिarity
                        img_bytes = pix.tobytes("png")
                        st.image(img_bytes, caption=f"फॉर्म पान क्र. {i+1}", use_container_width=True)
                
                # --- डाउनलोडसाठी PDF तयार करणे ---
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
                
                st.write("---")
                # डाउनलोड बटण
                st.download_button(
                    label="📥 मला हा फॉर्म डाऊनलोड करायचा आहे",
                    data=pdf_bytes,
                    file_name=f"Board_Form_{form_no_input}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error("फॉर्म लोड करताना अडचण आली.")
        else:
            st.error("❌ चुकीचा फॉर्म नंबर किंवा पासवर्ड. कृपया पुन्हा तपासा.")
    else:
        st.warning("⚠️ कृपया फॉर्म नंबर आणि पासवर्ड दोन्ही रकाने भरा.")

# --- 3. चुका नोंदवण्यासाठी फीडबॅक फॉर्म (Google Form) ---
st.write("---")
st.subheader("📝 फॉर्ममध्ये काही चूक आहे का?")
st.info("जर तुमच्या नावात, विषयात, जन्मतारखेत किंवा इतर माहितीत काही चूक असेल, तर खालील लिंकवर क्लिक करून माहिती सबमिट करा. ही माहिती थेट सरांना मिळेल.")

google_form_link = "https://forms.gle/hXDkhdJfPZjNCcwA7"

st.markdown(f"[👉 येथे क्लिक करून तुमची चूक नोंदवा]({google_form_link})", unsafe_allow_html=True)
