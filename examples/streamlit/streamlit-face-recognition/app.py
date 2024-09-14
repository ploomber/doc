import streamlit as st
import face_recognition
from PIL import Image, ImageDraw
import numpy as np


def detect_faces(image):
    # Convert the image to RGB (face_recognition requires RGB)
    rgb_image = image.convert("RGB")

    # Convert PIL Image to numpy array
    np_image = np.array(rgb_image)

    # Find all face locations and face encodings in the image
    face_locations = face_recognition.face_locations(np_image)

    # Create a copy of the image to draw on
    image_with_faces = image.copy()
    draw = ImageDraw.Draw(image_with_faces)

    # Draw rectangles around detected faces
    for face_location in face_locations:
        top, right, bottom, left = face_location
        draw.rectangle(((left, top), (right, bottom)), outline="red", width=2)

    return image_with_faces, len(face_locations)


st.title("Face Detection App")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the image file
    image = Image.open(uploaded_file)

    # Display the original image
    st.image(image, caption="Original Image", use_column_width=True)

    try:
        # Detect faces
        image_with_faces, face_count = detect_faces(image)

        # Display the result
        st.image(
            image_with_faces,
            caption=f"Detected Faces: {face_count}",
            use_column_width=True,
        )

        if face_count == 0:
            st.write("No faces detected in the image.")
        elif face_count == 1:
            st.write("1 face detected in the image.")
        else:
            st.write(f"{face_count} faces detected in the image.")
    except Exception as e:
        st.error(f"An error occurred during face detection: {str(e)}")
        st.write(
            "Please try uploading a different image or check if the face_recognition models are properly installed."
        )
