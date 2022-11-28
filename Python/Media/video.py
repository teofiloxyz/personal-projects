#!/usr/bin/python3

import os
import subprocess


class Video:
    def __init__(self) -> None:
        self.vid_exts = "mp4", "avi", "m4v", "mov"

    def compress(self) -> None:
        vid_in = self.get_input()
        if len(vid_in) == 0:
            print("Aborted...")
            return

        output_dir = self.create_output_dir(vid_in)
        vid_in_out = self.get_input_output(vid_in, output_dir)

        [
            self.compress_vid(vid_in, vid_out)
            for vid_in, vid_out in vid_in_out.items()
        ]

    def get_input(self) -> list[str]:
        prompt = input("Enter the path of video or folder with videos: ")
        if os.path.isdir(prompt):
            return [
                os.path.join(prompt, video)
                for video in os.listdir(prompt)
                if video.endswith(self.vid_exts)
            ]
        elif os.path.isfile(prompt):
            if prompt.endswith(self.vid_exts):
                return [prompt]
            else:
                print(f"Accepted formats are: {'; '.join(self.vid_exts)}")
        return []

    def create_output_dir(self, vid_in: list[str]) -> str:
        vid_in_dir = os.path.dirname(vid_in[0])
        output_dir = os.path.join(vid_in_dir, "Compressed")
        while os.path.isdir(output_dir):
            output_dir += "_"
        os.mkdir(output_dir)
        return output_dir

    def get_input_output(
        self, vid_in: list[str], output_dir: str
    ) -> dict[str, str]:
        vid_in_out = dict()
        for vid in vid_in:
            vid_in_basename = os.path.basename(vid)
            vid_in_bn_no_ext = os.path.splitext(vid_in_basename)[0]
            vid_out_basename = vid_in_bn_no_ext + ".mp4"
            vid_out = os.path.join(output_dir, vid_out_basename)
            vid_in_out[vid] = vid_out
        return vid_in_out

    def compress_vid(self, vid_in: str, vid_out: str) -> None:
        """Comprime imagem, e mantém o som;
        quanto maior o -crf, maior a compressão"""

        cmd = (
            f'ffmpeg -i "{vid_in}" -vcodec libx265 -crf 28 -acodec '
            f'copy "{vid_out}"'
        )

        err = subprocess.call(cmd, shell=True)
        if err != 0:
            print(f"Error compressing {vid_in}")
