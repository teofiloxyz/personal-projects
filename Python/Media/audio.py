#!/usr/bin/python3

import os
import subprocess


class Audio:
    def __init__(self) -> None:
        self.aud_exts = "mp3", "m4b", "opus", "wav"

    def compress_aud(self) -> None:
        def compress_aud(
            aud_in: str, aud_out: str, concatenate: bool = False
        ) -> None:
            # 32Kb de bitrate não é bom para música
            if concatenate:
                cmd = (
                    f'ffmpeg -f concat -safe 0 -i "{aud_in}" '
                    "-c:a libopus -b:a 32k -vbr on -compression_level 10 "
                    f'-frame_duration 60 -application voip "{aud_out}"'
                )
            else:
                cmd = (
                    f'ffmpeg -i "{aud_in}" -c:a libopus -b:a 32k '
                    "-vbr on -compression_level 10 -frame_duration 60 "
                    f'-application voip "{aud_out}"'
                )
            err = subprocess.call(cmd, shell=True)
            if err != 0:
                print(f"Error compressing {aud_in}")

        aud_in = input("Enter the input audio or folder: ")
        if os.path.isdir(aud_in):
            aud_in_dir = aud_in
            aud_in = [
                os.path.join(aud_in, aud)
                for aud in os.listdir(aud_in)
                if aud.endswith(self.aud_exts)
            ]
        elif os.path.isfile(aud_in):
            aud_in = inpt.files(
                question="Enter de audio input full path: ",
                extensions=self.aud_exts,
                file_input=aud_in,
            )
            if aud_in == "q":
                print("Aborted...")
                return
        else:
            print("Aborted...")
            return

        if type(aud_in) is not list:
            aud_out = oupt.files(
                question="Enter the audio output full path, "
                "or just the name for same input dir, "
                "or leave empty for <input>_output.opus: ",
                extension="opus",
                file_input=aud_in,
            )
            if aud_out == "q":
                print("Aborted...")
                return

            compress_aud(aud_in, aud_out)
        else:
            if (
                input(
                    ":: Do you want to concatenate the audio files? [y/N] "
                ).lower()
                == "y"
            ):

                output_dir = os.path.join(aud_in_dir, "Compressed_and_concat")
                if os.path.isdir(output_dir):
                    print("Output folder already exists\nAborting...")
                    return
                os.mkdir(output_dir)
                aud_out = os.path.join(output_dir, "output.opus")

                aud_in_txt = os.path.join(aud_in_dir, "input_files.txt")
                aud_in = sorted(aud_in)
                with open(aud_in_txt, "w") as txt:
                    for aud in aud_in:
                        entry = f"file '{aud}'"
                        print(entry)
                        txt.write(entry + "\n")

                if (
                    input(
                        ":: Do you want to edit the list of audio files to "
                        "be concatenated? [y/N] "
                    ).lower()
                    == "y"
                ):
                    cmd = f'nvim "{aud_in_txt}"'
                    subprocess.run(cmd, shell=True)

                compress_aud(aud_in_txt, aud_out, concatenate=True)
            else:
                output_dir = os.path.join(aud_in_dir, "Compressed")
                if os.path.isdir(output_dir):
                    print("Output folder already exists\nAborting...")
                    return
                os.mkdir(output_dir)

                for aud in aud_in:
                    aud_basename = os.path.basename(aud)
                    aud_out = os.path.join(output_dir, aud_basename)
                    compress_aud(aud, aud_out)
