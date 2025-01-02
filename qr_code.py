import streamlit as st
import qrcode
from PIL import Image
from io import BytesIO
import base64
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables (only for local development)
load_dotenv()

# Configure Cloudinary with environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# Function to encode image as base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

# Encode the background image
background_image = get_base64_image("gradient-blur.png")

# Custom CSS for background image
st.markdown(
    f"""
    <style>
    body {{
        background-image: url("data:image/jpeg;base64,{background_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp {{
        background-color: rgba(255, 255, 255, 0.8); /* Add transparency for better readability */
        padding: 20px;
        border-radius: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit App Configuration
st.title("QR Code Generator")
st.write("Generate a custom QR code by providing a URL and selecting colors.")

# Initialize session state for the QR code
if "qr_buffer" not in st.session_state:
    st.session_state.qr_buffer = None
if "hosted_qr_url" not in st.session_state:
    st.session_state.hosted_qr_url = None

# User Inputs
url = st.text_input("Enter the URL for the QR code", "https://github.com/arham2003")
fill_color = st.color_picker("Choose the QR code fill color", "#000000")  # Default: Black
back_color = st.color_picker("Choose the QR code background color", "#FFFFFF")  # Default: White

# QR Code Generation and Hosting
if st.button("Generate QR Code"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=5,  # Smaller size for the QR code
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Save the image in a byte stream
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)

    # Store the byte stream in session state
    st.session_state.qr_buffer = buffered

    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(buffered, resource_type="image")
    st.session_state.hosted_qr_url = upload_result["secure_url"]

    st.success("QR Code generated and hosted successfully!")

# Center QR Code and Buttons (using columns)
if st.session_state.qr_buffer:
    # Center QR code
    col1, col2, col3 = st.columns([1, 2, 1])  # 2 is the largest column to center the content
    with col2:
        st.image(st.session_state.qr_buffer, caption="Generated QR Code", use_container_width=False, width=200)

    # Custom-styled Download Button
    col1, col2 = st.columns([1, 1])  # Equal width for buttons
    with col1:
        download_button_html = f"""
        <style>
            .download-button {{
                display: inline-block;
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: lightgreen;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                border: none;
                border-radius: 8px;
            }}
            .download-button:hover {{
                background-color: #90ee90; /* Slightly darker green on hover */
            }}
        </style>
        <a download="custom_qr_code.png" href="data:image/png;base64,{base64.b64encode(st.session_state.qr_buffer.getvalue()).decode("utf-8")}" class="download-button">
            Download QR Code
        </a>
        """
        st.markdown(download_button_html, unsafe_allow_html=True)

    # Clear Button
    with col2:
        if st.button("Clear QR Code"):
            st.session_state.qr_buffer = None
            st.session_state.hosted_qr_url = None
            st.rerun()  # Trigger rerun to update the UI immediately

    # Title for Share Section
    st.subheader("Share Now")

    # Share button (only show if hosted_qr_url exists)
    if st.session_state.hosted_qr_url:
        hosted_link = st.session_state.hosted_qr_url

        # HTML for share button and icons
        share_html = f"""
        <div style="display: flex; gap: 15px;">
            <a href="https://wa.me/?text={hosted_link}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="40" height="40" alt="WhatsApp"/>
            </a>
            <a href="https://www.instagram.com/share?url={hosted_link}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="40" height="40" alt="Instagram"/>
            </a>
            <a href="https://drive.google.com/uc?export=download&url={hosted_link}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Google_Drive_icon_%282020%29.svg/150px-Google_Drive_icon_%282020%29.svg.png" width="40" height="40" alt="Google Drive"/>
            </a>
            <a href="https://www.facebook.com/sharer/sharer.php?u={hosted_link}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" width="40" height="40" alt="Facebook"/>
            </a>
        </div>
        """
        # Display Share options
        st.markdown(share_html, unsafe_allow_html=True)
