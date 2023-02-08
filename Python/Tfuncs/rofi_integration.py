# Integração com os menus do rofi

import subprocess
import tempfile


class Rofi:
    cmd_config = (
        '-theme-str \'entry { placeholder: ""; } inputbar '
        "{ children: [prompt, textbox-prompt-colon, entry]; }"
    )

    def simple_prompt(
        self, prompt: str, hide_input: bool = False, message: str = ""
    ) -> str:
        prompt = self._clean_prompt(prompt)
        message = self._get_prompt_msg(message)
        hide_flag = "-password" if hide_input else ""
        cmd = (
            f"rofi -dmenu {hide_flag} -p '{prompt}' -l 0 {self.cmd_config} "
            f"listview {{ border: 0; }}' {message}"
        )
        return self._run_rofi(cmd)

    def custom_dmenu(self, prompt: str, dmenu: list, message: str = "") -> str:
        prompt = self._clean_prompt(prompt)
        message = self._get_prompt_msg(message)
        tmp_file = self._get_tmp_file(dmenu)
        dmenu_lines = str(len(dmenu)) if len(dmenu) < 15 else "15"
        cmd = (
            f"rofi -dmenu -i -input {tmp_file} -p '{prompt}' "
            f"-l {dmenu_lines} {self.cmd_config}' {message}"
        )

        return self._run_rofi(cmd)

    def message_box(self, content: str) -> None:
        cmd = f'rofi -e "{content}"'
        self._run_rofi(cmd)

    def _clean_prompt(self, prompt: str) -> str:
        prompt = prompt.rstrip()
        if prompt.endswith(":"):
            prompt = prompt[:-1]
        return prompt

    def _get_prompt_msg(self, message: str) -> str:
        if message != "":
            message = f' -mesg "{message}"'
        return message

    def _get_tmp_file(self, lines: list) -> str:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.writelines("\n".join(lines))
            return tmp.name

    def _run_rofi(self, cmd: str) -> str:
        return (
            subprocess.run(cmd, shell=True, capture_output=True)
            .stdout.decode("utf-8")
            .strip()
        )
