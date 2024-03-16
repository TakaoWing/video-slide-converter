import zipfile
from io import BytesIO

import streamlit as st
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

from schema.image import SlideImage


class VideoSlideConverter:
    video_size = (1280, 720)
    slide_position: tuple[int, int] = (30, 36)
    slide_image_magnification: float = 0.715
    base_image = Image.open("src/resource/base_image.png")

    def __init__(self, position: tuple[int, int] | None = None) -> None:
        # load sample image
        if position is not None:
            self.slide_position = position

    def _convert_slide_image(self, image: UploadedFile) -> SlideImage:
        # 1920x1080の透明背景画像を作成
        base_image = Image.new("RGBA", self.video_size, (255, 0, 0, 0))

        # 配置する小さい画像を開く
        slide_image = Image.open(image).convert("RGBA")

        if slide_image.height > 1090:
            self.slide_image_magnification = 0.23
            self.slide_position = (25, 90)

        # スライド画像のサイズをn倍に拡大
        enlarged_size = (
            int(slide_image.width * self.slide_image_magnification),
            int(slide_image.height * self.slide_image_magnification),
        )
        slide_image = slide_image.resize(enlarged_size, Image.LANCZOS)

        base_image.paste(slide_image, self.slide_position)

        # 結果を保存
        buffer = BytesIO()
        base_image.save(buffer, format="PNG")
        return SlideImage(
            name=image.name,
            buffer=buffer.getvalue(),
        )

    def convert_slide_images(self):
        images = st.session_state.get("images", [])
        self.slide_images = [self._convert_slide_image(image) for image in images]

    def images_to_zip_buffer(self) -> bytes:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for image in self.slide_images:
                zip_file.writestr(image.name, image.buffer)
        return zip_buffer.getvalue()

    def _sample_image(self, slide_image: SlideImage) -> Image.Image:
        # スキーマから画像へ変換
        image = slide_image.to_pil_image

        # ベースを複製
        _image = self.base_image.copy()

        # 画像を貼り付け
        _image.paste(
            im=image,
            box=(0, 0),
            mask=image,
        )

        # 画像を返す
        return _image

    def sample_images(self) -> list[Image.Image]:
        return [self._sample_image(slide_image) for slide_image in self.slide_images]
