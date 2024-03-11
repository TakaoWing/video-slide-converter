import streamlit as st

from video_slide_converter import video_slide_converter


def main():
    st.title("動画内スライド画像変換ツール")

    # スライドの画像をアップロード（複数選択可）
    st.file_uploader(
        "スライド画像をアップロードしてください",
        type=[
            "png",
            "jpg",
        ],
        accept_multiple_files=True,
        key="images",
    )

    # 画像がアップロードされていない場合はここで終了
    if not st.session_state.get("images"):
        st.stop()

    # スライド画像を変換
    video_slide_converter.convert_slide_images()

    # 画像をダウンロードするボタン
    st.download_button(
        label="ダウンロード",
        data=video_slide_converter.images_to_zip_buffer(),
        file_name="images.zip",
        mime="application/zip",
    )

    # スライドの確認証
    for image in video_slide_converter.sample_images():
        st.image(
            image,
            use_column_width=True,
        )


if __name__ == "__main__":
    main()
