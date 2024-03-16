import zipfile
from io import BytesIO

import streamlit as st
from PIL import Image, ImageFilter, ImageOps
from streamlit.runtime.uploaded_file_manager import UploadedFile

from schema.image import SlideImage


class VideoSlideConverter:
    video_size = (2560, 1440)
    slide_position: tuple[int, int] = (60, 72)
    slide_image_magnification: float = 1.43
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
            margin_height = 165
            slide_image = slide_image.crop(
                (
                    0,
                    margin_height,
                    slide_image.width - 2,
                    slide_image.height - margin_height,
                )
            )
            border_color = "#172053"
            border_width = 38
            slide_image = ImageOps.expand(
                slide_image, border=border_width, fill=border_color
            )
            slide_image = self.add_shadow(slide_image)
            self.slide_image_magnification = 0.42
            self.slide_position = (60, 180)

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

    def add_shadow(
        self,
        image: Image.Image,
        shadow_color: str = "#00000040",
        shadow_offset: tuple[int, int] = (20, 20),
        shadow_blur_radius: int = 8,
    ) -> Image.Image:
        # 元の画像のサイズを取得
        width, height = image.size

        # 影のサイズ
        shadow_size = (
            width + abs(shadow_offset[0]) + shadow_blur_radius * 2,
            height + abs(shadow_offset[1]) + shadow_blur_radius * 2,
        )

        # 影用の画像を作成
        shadow_image = Image.new("RGBA", shadow_size, (0, 0, 0, 0))

        # 影の部分を塗りつぶす
        shadow_draw = Image.new("RGBA", (width, height), shadow_color)

        # 影をずらして配置
        shadow_image.paste(
            shadow_draw,
            box=(
                shadow_blur_radius + max(shadow_offset[0], 0),
                shadow_blur_radius + max(shadow_offset[1], 0),
            ),
        )

        # 影にぼかしを適用
        shadow_image = shadow_image.filter(
            ImageFilter.GaussianBlur(radius=shadow_blur_radius)
        )
        # 最終的な画像サイズ（影を加えた後のサイズ）
        final_size = (
            width + abs(shadow_offset[0]) + shadow_blur_radius * 2,
            height + abs(shadow_offset[1]) + shadow_blur_radius * 2,
        )

        # 最終的な画像用のキャンバスを作成
        final_image = Image.new("RGBA", final_size, (0, 0, 0, 0))

        # 影をキャンバスに貼り付け
        final_image.paste(shadow_image, (0, 0))

        # 元の画像を影の上に貼り付け
        final_image.paste(
            image,
            (
                shadow_blur_radius + abs(min(shadow_offset[0], 0)),
                shadow_blur_radius + abs(min(shadow_offset[1], 0)),
            ),
        )

        return final_image

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
        _image = Image.alpha_composite(_image, image)

        # 画像を返す
        return _image

    def sample_images(self) -> list[Image.Image]:
        return [self._sample_image(slide_image) for slide_image in self.slide_images]
