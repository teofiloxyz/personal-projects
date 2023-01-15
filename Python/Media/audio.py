from utils import Utils


class Audio:
    utils = Utils()
    audio_exts = "mp3", "m4b", "opus", "wav"
    output_ext = "opus"

    def compress(self) -> None:
        audios = self.utils.get_input(self.audio_exts)
        if len(audios) == 0:
            print("Aborted...")
            return
        output_dir = self.utils.create_output_dir(audios)
        audios = self.utils.get_output(audios, output_dir, self.output_ext)

        if len(audios) == 1:
            if self.utils.concatenate():
                audio = self.utils.get_concatenation(audios)
                self._compress_audio(audio, concatenate=True)
                return

        [self._compress_audio(audio, concatenate=False) for audio in audios]

    def _compress_audio(self, audio: dict, concatenate: bool) -> None:
        if concatenate:
            cmd = f'ffmpeg -f concat -safe 0 -i "{audio["input"]}"'
        else:
            cmd = f'ffmpeg -i "{audio["input"]}"'
        cmd += (
            # 32Kb of bitrate is poor quality
            " -c:a libopus -b:a 32k -vbr on -compression_level 10 "
            f'-frame_duration 60 -application voip "{audio["output"]}"'
        )
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print(f"Error compressing {audio['input']}")
