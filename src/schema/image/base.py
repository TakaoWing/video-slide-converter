from functools import cached_property
from io import BytesIO

from PIL import Image
from pydantic import BaseModel, Field


class SlideImage(BaseModel):
    name: str = Field(..., title="スライド名")
    buffer: bytes = Field(..., title="スライド画像のバイナリデータ")

    @cached_property
    def to_pil_image(self) -> Image.Image:
        return Image.open(BytesIO(self.buffer))
