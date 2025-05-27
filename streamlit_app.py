import streamlit as st
import cv2
import uuid
import os

st.set_page_config(initial_sidebar_state="collapsed")

st.header("Classificador de Células em Mitose")
st.subheader("Faça o upload de imagens (Formato JPG) de células ou use as imagens de exemplo clicando no botão abaixo")

if st.button("Usar Imagens exemplo"):
    st.session_state['example_images'] = True
    st.switch_page("./pages/detection.py")


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
        images_path = f"./uploaded_images/{str(uuid.uuid4())}"
        os.makedirs(images_path, exist_ok=True)
        for i, image in enumerate(files):
            with open(f"{images_path}/{image.name}", "wb") as f:
                f.write(image.read())
        st.session_state['example_images'] = False
        st.session_state['images_path'] = images_path
        st.switch_page("./pages/detection.py")
    else:
        st.subheader("No Images Uploaded!")

