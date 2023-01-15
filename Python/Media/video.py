from utils import Utils


class Video:
    utils = Utils()
    video_exts = "mp4", "avi", "m4v", "mov"
    output_ext = "mp4"

    def compress(self) -> None:
        videos = self.utils.get_input(self.video_exts)
        if len(videos) == 0:
            print("Aborted...")
            return
        output_dir = self.utils.create_output_dir(videos)
        videos = self.utils.get_output(videos, output_dir, self.output_ext)
        [self._compress_video(video) for video in videos]

    def _compress_video(self, video: dict) -> None:
        """Comprime imagem, e mantém o som;
        quanto maior o -crf, maior a compressão"""
        # -filter:a "volume=15dB" max 20dB

        cmd = (
            f'ffmpeg -i "{video["input"]}" -vcodec libx265 -crf 28 '
            f'-acodec copy "{video["output"]}"'
        )
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print(f"Error compressing {video['input']}")
