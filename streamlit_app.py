import streamlit as st
import cv2

files = st.file_uploader("input images", accept_multiple_files=True)

col1, col2, col3, col4, col5 = st.columns(5)

columns = [col1, col2, col3, col4, col5]

if files:
    for i, image in enumerate(files):
        with columns[i % 5]:
            st.image(image, width=100)
            st.write(image.name)

st.markdown("---")
if st.button("Continuar"):

    if files:
        for i, image in enumerate(files):
            with open(f"uploaded_images/{image.name}", "wb") as f:
                f.write(image.read())
        st.switch_page("./pages/detection.py")
    else:
        st.subheader("No Images Uploaded!")

