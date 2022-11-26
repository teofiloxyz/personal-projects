#!/usr/bin/python3

import os
import subprocess


class Video:
    def __init__(self) -> None:
        self.vid_exts = "mp4", "avi", "m4v", "mov"

    def compress(self) -> None:
        def compress_vid(vid_in: str, vid_out: str) -> None:
            """Comprime apenas vid, e mantém o som;
            qt maior -crf, maior compress"""

            cmd = (
                f'ffmpeg -i "{vid_in}" -vcodec libx265 -crf 28 -acodec '
                f'copy "{vid_out}"'
            )
            err = subprocess.call(cmd, shell=True)
            if err != 0:
                print(f"Error compressing {vid_in}")

        vid_in = input("Enter the input video or folder: ")
        if os.path.isdir(vid_in):
            vid_in_dir = vid_in
            vid_in = [
                os.path.join(vid_in, vid)
                for vid in os.listdir(vid_in)
                if vid.endswith(self.vid_exts)
            ]
        elif os.path.isfile(vid_in):
            vid_in = inpt.files(
                question="Enter de video input full path: ",
                extensions=self.vid_exts,
                file_input=vid_in,
            )
            if vid_in == "q":
                print("Aborted...")
                return
        else:
            print("Aborted...")
            return

        if type(vid_in) is not list:
            vid_out = oupt.files(
                question="Enter the video output full path, "
                "or just the name for same input dir, "
                "or leave empty for <input>_output.mp4: ",
                extension="mp4",
                file_input=vid_in,
            )
            if vid_out == "q":
                print("Aborted...")
                return

            compress_vid(vid_in, vid_out)
        else:
            output_dir = os.path.join(vid_in_dir, "Compressed")
            if os.path.isdir(output_dir):
                print("Output folder already exists\nAborting...")
                return
            os.mkdir(output_dir)
            for vid in vid_in:
                vid_basename = os.path.basename(vid)
                vid_basename_out = os.path.splitext(vid_basename)[0] + ".mp4"
                vid_out = os.path.join(output_dir, vid_basename_out)
                compress_vid(vid, vid_out)
