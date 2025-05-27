import sys
import os

# Adicionar o diretório atual
print("PATH:: " + os.getcwd()+"/pages")
sys.path.append(os.getcwd()+"/pages")

import streamlit as st
from glob import glob
from streamlit_image_annotation2 import detection
import cv2
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout='wide', initial_sidebar_state="collapsed")

st.header("Classificador de Células em Mitose")
st.write("Dicas:")
st.write(" Use o scrol do mouse para dar zoom na imagem ")
st.write("Selecione a classe desejada e classifique as células em mitose  no modo Classificar")
st.write("Clique em Calcular para obter o indice mitotico da imagem")
#########
def get_bounds(img_path):
    img = cv2.imread(img_path)

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    output_image = img

    min_area = 2500   
    max_area = 20000   

    def find_best_threshold(gray_img):

        threshold_range = range(75,200, 5)
        best_threshold = 0
        max_detected_boxes = 0

        for threshold in threshold_range:

            _, binary_img = cv2.threshold(gray_img, threshold, 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            count_boxes = 0

            for cnt in contours:
                
                area = cv2.contourArea(cnt)
                
                if area < min_area or area > max_area:
                    continue  

                count_boxes += 1

            if count_boxes > max_detected_boxes:
                max_detected_boxes = count_boxes
                best_threshold = threshold
        
        return best_threshold

    threshold = find_best_threshold(gray_img)

    _, binary_img = cv2.threshold(gray_img, threshold, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    result = {
        "bboxes" : [],
        "labels" : []
    }

    for cnt in contours:
        
        area = cv2.contourArea(cnt)
        
        if area < min_area or area > max_area:
            continue  

        x, y, w, h = cv2.boundingRect(cnt)

        result['bboxes'].append([x, y, w, h])
        result['labels'].append(0)
    
    return result
#########



label_list = ['interfase',  'profase', 'metafase', 'anafase' ,'telofase']

if st.session_state['example_images']:
    images_path = "./uploaded_images"
else:
    images_path = st.session_state['images_path']

image_path_list = glob(f"{images_path}/*.jpg")
if 'result_dict' not in st.session_state:
    result_dict = {}
    for img in image_path_list:
        result_dict[img] = get_bounds(img)
    st.session_state['result_dict'] = result_dict.copy()

num_page = st.slider('imagem', 0, len(image_path_list), 0, key='slider')

col1, col2 = st.columns(2)

with col1:
    target_image_path = image_path_list[num_page]

    new_labels = detection(image_path=target_image_path, 
                        bboxes=st.session_state['result_dict'][target_image_path]['bboxes'], 
                        labels=st.session_state['result_dict'][target_image_path]['labels'],
                        line_width=2,
                        label_list=label_list, use_space=False, key=target_image_path, height=512, width=512)
    if new_labels is not None:
        st.session_state['result_dict'][target_image_path]['bboxes'] = [v['bbox'] for v in new_labels]
        st.session_state['result_dict'][target_image_path]['labels'] = [v['label_id'] for v in new_labels]

with col2:
    st.markdown("<h2 style='text-align: center;'>Indíce Mitótico</h2>", unsafe_allow_html=True)
    total_cells = st.session_state['result_dict'][target_image_path]['labels']
    mitotic_cells = sum([1 for x in st.session_state['result_dict'][target_image_path]['labels'] if x != 0])

    indice_mitotico = (mitotic_cells / len(total_cells)) * 100 if total_cells else 0

    st.latex(r'\frac{' + str(mitotic_cells) + r'}{' + str(len(total_cells)) + r'} = ' + f'{indice_mitotico:.2f}\\%')

    st.markdown("---")

    # Título centralizado
    st.markdown("<h2 style='text-align: center;'>Contagem de Células</h2>", unsafe_allow_html=True)

    # Cálculo das fases
    labels = st.session_state['result_dict'][target_image_path]['labels']
    fase_in = sum(1 for x in labels if x == 0)
    fase_pr = sum(1 for x in labels if x == 1)
    fase_me = sum(1 for x in labels if x == 2)
    fase_an = sum(1 for x in labels if x == 3)
    fase_te = sum(1 for x in labels if x == 4)
    total = len(total_cells)

    # Soma em formato vertical
    st.markdown(f"""
    <div style="font-size: 20px; line-height: 2;">
        Interfase: {fase_in} <br>
        Prófase: {fase_pr} <br>
        Metáfase: {fase_me} <br>
        Anáfase: {fase_an} <br>
        Telófase: {fase_te} <br>
        <hr style="border:1px solid #aaa;">
        <strong>Total de Células: {total}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    
    
#st.json(st.session_state['result_dict'])
