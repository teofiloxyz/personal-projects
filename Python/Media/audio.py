#!/usr/bin/python3

import os
import subprocess


class Audio:
    def __init__(self) -> None:
        self.aud_exts = "mp3", "m4b", "opus", "wav"

    def compress(self) -> None:
        aud_in = self.get_input()
        if len(aud_in) == 0:
            print("Aborted...")
            return

        output_dir = self.create_output_dir(aud_in)
        aud_in_out = self.get_input_output(aud_in, output_dir)

        if len(aud_in) > 1:
            if self.concatenate():
                aud_in = self.get_concatenation(aud_in)
                # precisa de ajuste o título do output
                aud_out = [aud_out for aud_out in aud_in_out.values()][0]
                self.compress_aud(aud_in, aud_out, concatenate=True)
                return

        [
            self.compress_aud(aud_in, aud_out, concatenate=False)
            for aud_in, aud_out in aud_in_out.items()
        ]

    def get_input(self) -> list[str]:
        prompt = input("Enter the path of audio or folder with audios: ")
        if os.path.isdir(prompt):
            return [
                os.path.join(prompt, audio)
                for audio in os.listdir(prompt)
                if audio.endswith(self.aud_exts)
            ]
        elif os.path.isfile(prompt):
            if prompt.endswith(self.aud_exts):
                return [prompt]
            else:
                print(f"Accepted formats are: {'; '.join(self.aud_exts)}")
        return []

    def create_output_dir(self, aud_in: list[str]) -> str:
        aud_in_dir = os.path.dirname(aud_in[0])
        output_dir = os.path.join(aud_in_dir, "Compressed")
        while os.path.isdir(output_dir):
            output_dir += "_"
        os.mkdir(output_dir)
        return output_dir

    def get_input_output(
        self, aud_in: list[str], output_dir: str
    ) -> dict[str, str]:
        aud_in_out = dict()
        for aud in aud_in:
            aud_in_basename = os.path.basename(aud)
            aud_in_bn_no_ext = os.path.splitext(aud_in_basename)[0]
            aud_out_basename = aud_in_bn_no_ext + ".opus"
            aud_out = os.path.join(output_dir, aud_out_basename)
            aud_in_out[aud] = aud_out
        return aud_in_out

    def concatenate(self) -> bool:
        return (
            True
            if (
                input(
                    ":: Do you want to concatenate the audio files? [y/N] "
                ).lower()
                == "y"
            )
            else False
        )

    def get_concatenation(self, aud_in: list[str]) -> str:
        aud_in_dir = os.path.dirname(aud_in[0])
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
        return aud_in_txt

    def compress_aud(
        self, aud_in: str, aud_out: str, concatenate: bool
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
