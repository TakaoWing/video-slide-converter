import zipfile
from io import BytesIO

from streamlit.runtime.uploaded_file_manager import UploadedFile


def download_zip_images(images: list[UploadedFile]) -> BytesIO:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for image in images:
            zip_file.writestr(image.name, image.read())
    zip_buffer.seek(0)
    return zip_buffer
