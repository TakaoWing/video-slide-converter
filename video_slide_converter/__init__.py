from .base import VideoSlideConverter


class VideoSlideConverterSingleton:
    _instance = None

    @classmethod
    def get_instance(cls) -> VideoSlideConverter:
        if cls._instance is None:
            cls._instance = VideoSlideConverter()
        return cls._instance


video_slide_converter = VideoSlideConverterSingleton.get_instance()

__all__ = [
    "video_slide_converter",
]
