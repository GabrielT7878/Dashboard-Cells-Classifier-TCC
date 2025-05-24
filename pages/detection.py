import streamlit as st
from glob import glob
from streamlit_image_annotation2 import detection
import cv2
import numpy as np
import matplotlib.pyplot as plt
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
image_path_list = glob('../uploaded_images/*.jpg')
if 'result_dict' not in st.session_state:
    result_dict = {}
    for img in image_path_list:
        result_dict[img] = get_bounds(img)
    st.session_state['result_dict'] = result_dict.copy()

num_page = st.slider('page', 0, len(image_path_list)-1, 0, key='slider')

target_image_path = image_path_list[num_page]

image_size = st.slider('image size', 1, 10, 1, key='image_size_slider')

new_labels = detection(image_path=target_image_path, 
                    bboxes=st.session_state['result_dict'][target_image_path]['bboxes'], 
                    labels=st.session_state['result_dict'][target_image_path]['labels'],
                    line_width=2,
                    label_list=label_list, use_space=False, key=target_image_path, height=512 * (1 + image_size * 0.1), width=512 * (1 + image_size * 0.1))
if new_labels is not None:
    st.session_state['result_dict'][target_image_path]['bboxes'] = [v['bbox'] for v in new_labels]
    st.session_state['result_dict'][target_image_path]['labels'] = [v['label_id'] for v in new_labels]
    
st.json(st.session_state['result_dict'])