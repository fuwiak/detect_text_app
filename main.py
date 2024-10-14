import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import time
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import speech_recognition as sr
from pydub import AudioSegment
import io
import tempfile

# Load OCR model only once
if 'ocr_model' not in st.session_state:
    st.session_state['ocr_model'] = easyocr.Reader(['ru', 'en'])  # Russian and English OCR

# Session state variables for handling image and rotation
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None
if 'image' not in st.session_state:
    st.session_state['image'] = None
if 'rotated_image' not in st.session_state:
    st.session_state['rotated_image'] = None
if 'rotation_angle' not in st.session_state:
    st.session_state['rotation_angle'] = 0
if 'extracted_text' not in st.session_state:
    st.session_state['extracted_text'] = ""
if 'detected_lang' not in st.session_state:
    st.session_state['detected_lang'] = None
if 'inference_time' not in st.session_state:
    st.session_state['inference_time'] = 0.0

# Title and sidebar
st.title('Приложение для распознавания текста и аудио')

# Sidebar components
with st.sidebar:
    st.header("Загрузите изображение и настройки")

    # Upload image
    uploaded_file = st.file_uploader("Загрузите изображение", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file
        st.session_state['image'] = Image.open(st.session_state['uploaded_file'])
        st.session_state['rotated_image'] = st.session_state['image']
        st.session_state['rotation_angle'] = 0  # Сброс угла поворота

    # Buttons for rotating the image
    rotate_left = st.button('Повернуть влево на 90°')
    rotate_right = st.button('Повернуть вправо на 90°')

    # Slider for custom rotation
    rotate_custom = st.slider('Повернуть изображение на угол', -180, 180, value=st.session_state['rotation_angle'],
                              key='rotate_slider')

    # Clear uploaded image
    clear_file = st.button('Очистить загруженное изображение')

# Handle image rotation
if st.session_state['image'] is not None:
    if rotate_left:
        st.session_state['rotation_angle'] += 90
    if rotate_right:
        st.session_state['rotation_angle'] -= 90

    # Custom rotation using the slider
    if rotate_custom != st.session_state['rotation_angle']:
        st.session_state['rotation_angle'] = rotate_custom

    # Apply rotation and update the image
    st.session_state['rotated_image'] = st.session_state['image'].rotate(st.session_state['rotation_angle'], expand=True)

# Clear file logic
if clear_file:
    st.session_state['uploaded_file'] = None
    st.session_state['image'] = None
    st.session_state['rotated_image'] = None
    st.session_state['rotation_angle'] = 0
    st.write("Файл очищен. Пожалуйста, загрузите новое изображение.")

# Display the rotated image
if st.session_state['rotated_image'] is not None:
    st.image(st.session_state['rotated_image'], caption='Загруженное изображение', use_column_width=True)

    # Button to process the image and measure inference time
    if st.button('Распознать текст'):
        # Start timing inference
        start_time = time.time()

        # Perform OCR
        reader = st.session_state['ocr_model']
        result = reader.readtext(np.array(st.session_state['rotated_image']))
        st.session_state['extracted_text'] = ' '.join([res[1] for res in result])

        # End timing
        end_time = time.time()
        inference_time = end_time - start_time
        st.session_state['inference_time'] = inference_time

        # Display extracted text
        if st.session_state['extracted_text']:
            st.write('### Распознанный текст:')
            st.write(st.session_state['extracted_text'])

            # Language detection
            try:
                detected_lang = detect(st.session_state['extracted_text'])
                if detected_lang in ['ru', 'en']:
                    st.session_state['detected_lang'] = detected_lang
                    lang_display = 'Русский' if detected_lang == 'ru' else 'Английский'
                    st.write(f"### Определённый язык: **{lang_display}**")
                else:
                    st.write("Поддерживаются только русский и английский языки.")
            except LangDetectException:
                st.write("Не удалось определить язык. Пожалуйста, попробуйте снова.")




else:
    st.write("Пожалуйста, загрузите изображение для начала.")

