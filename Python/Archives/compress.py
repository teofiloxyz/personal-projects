from dataclasses import dataclass
from enum import Enum
from typing import Optional

from utils import Utils


class CompressionType(Enum):
    XZ = "XZ (on max compression)"
    TAR = "Tar"
    ZIP = "Zip"
    SEVENZIP = "7zip"


@dataclass
class CompressionProperties:
    type: CompressionType
    cmd: str
    output_ext: str


class CompressionOptions:
    XZ = CompressionProperties(
        type=CompressionType.XZ,
        cmd="tar cvf {output} --use-compress-program='xz -9T0' {input}",
        output_ext=".tar.xz",
    )
    TAR = CompressionProperties(
        type=CompressionType.TAR,
        cmd="tar cvf {output} {input}",
        output_ext=".tar",
    )
    ZIP = CompressionProperties(
        type=CompressionType.ZIP,
        cmd="zip {output} {input}",
        output_ext=".zip",
    )
    SEVENZIP = CompressionProperties(
        type=CompressionType.SEVENZIP,
        cmd="7z a {output} {input}",
        output_ext=".7z",
    )

    @classmethod
    def multiple_files_input(cls) -> tuple:
        return cls.XZ, cls.TAR, cls.ZIP, cls.SEVENZIP

    @classmethod
    def single_file_input(cls) -> tuple:
        cls.XZ.cmd, cls.XZ.output_ext = (
            "xz -9kT0 {input} --stdout > {output}",
            ".xz",
        )
        cls.ZIP.cmd = "zip --junk-paths {output} {input}"
        return cls.XZ, cls.ZIP, cls.SEVENZIP

    @classmethod
    def get_command(
        cls, option: CompressionProperties, input: str, output: str
    ) -> str:
        return option.cmd.format(input=input, output=output)


class Compress:
    def __init__(self, input_files: list[str]) -> None:
        self.utils = Utils()
        self.input_files = input_files

    def main(self) -> None:
        self._handle_input()

        compression_options = self._get_compression_options()
        compression_properties = self._choose_compression_properties(
            compression_options
        )
        if not compression_properties:
            print("Aborted...")
            return
        elif compression_properties.type == CompressionType.SEVENZIP:
            compression_properties = self._choose_if_7zip_encrypts_output(
                compression_properties
            )

        output_name = self._generate_output_file_name(compression_properties)
        self._run_compression(compression_properties, output_name)

    def _handle_input(self) -> None:
        if len(self.input_files) > 1:
            return
        if self.utils.check_if_is_dir(self.input_files[0]):
            self.input_files = self.utils.get_dir_contents(self.input_files[0])

    def _get_compression_options(self) -> tuple[CompressionProperties]:
        if len(self.input_files) > 1:
            return CompressionOptions.multiple_files_input()
        return CompressionOptions.single_file_input()

    def _choose_compression_properties(
        self, compression_options: tuple[CompressionProperties]
    ) -> Optional[CompressionProperties]:
        for n, option in enumerate(compression_options, 1):
            print(f"[{n}] {option.type.value}")
        prompt = input("\nChoose compression option or leave empty for first: ")
        if prompt == "":
            return compression_options[0]
        elif prompt.isdigit() and 1 <= int(prompt) <= len(compression_options):
            return compression_options[int(prompt) - 1]
        return None

    def _choose_if_7zip_encrypts_output(
        self, compression_properties: CompressionProperties
    ) -> CompressionProperties:
        if input(":: Want an encrypted 7zip output? [y/N] ").lower() == "y":
            compression_properties.cmd = "7z a {output} -mhe=on {input} -p"
        return compression_properties

    def _generate_output_file_name(
        self,
        compression_properties: CompressionProperties,
    ) -> str:
        extension = compression_properties.output_ext
        output_name = (
            self.utils.get_output_name_in_cwd(self.input_files) + extension
        )
        return self.utils.process_output_file_name(output_name)

    def _run_compression(
        self, compression_properties: CompressionProperties, output_name: str
    ) -> None:
        cmd = CompressionOptions.get_command(
            compression_properties,
            input=" ".join(self.input_files),
            output=output_name,
        )
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print("Error compressing input")
