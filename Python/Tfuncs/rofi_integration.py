#!/usr/bin/python3
# Integração com os menus do rofi

import subprocess


class Rofi:
    @staticmethod
    def simple_prompt(prompt: str, message: str = "") -> str:
        prompt = fix_prompt(prompt)
        message = get_prompt_msg(message)
        cmd = (
            f"rofi -dmenu -p '{prompt}' -l 0 -theme-str 'entry "
            '{ placeholder: ""; } inputbar { children: [prompt, '
            "textbox-prompt-colon, entry]; } listview { border: 0; }'"
            f"{message}"
        )
        return run_and_get_input(cmd)

    @staticmethod
    def custom_dmenu(prompt: str, dmenu: list, message: str = "") -> str:
        prompt = fix_prompt(prompt)
        message = get_prompt_msg(message)
        input_file = create_input_file(dmenu)
        dmenu_lines = fix_dmenu_lines_num(len(dmenu))
        cmd = (
            f"rofi -dmenu -i -input {input_file} -p '{prompt}'"
            f' -l {dmenu_lines} -theme-str \'entry {{ placeholder: ""; }} '
            "inputbar { children: [prompt, textbox-prompt-colon, entry]; }'"
            f"{message}; rm {input_file}"
        )
        return run_and_get_input(cmd)

    @staticmethod
    def message(message: str) -> None:
        cmd = f'rofi -e "{message}"'
        subprocess.run(cmd, shell=True)


def fix_prompt(prompt: str) -> str:
    if prompt.endswith(":"):
        prompt = prompt[:-1]
    return prompt


def get_prompt_msg(message: str) -> str:
    if message != "":
        message = f' -mesg "{message}"'
    return message


def create_input_file(dmenu: list) -> str:
    lines = "\n".join(dmenu)
    input_file = "/tmp/python_rofi_integration.dmenulist"
    with open(input_file, "w") as rif:
        rif.writelines(lines)
    return input_file


def fix_dmenu_lines_num(dmenu_length: int) -> str:
    return str(dmenu_length) if dmenu_length < 15 else "15"


def run_and_get_input(cmd: str) -> str:
    user_input = subprocess.run(
        cmd, shell=True, capture_output=True
    ).stdout.decode("utf-8")
    return user_input.strip("\n")
