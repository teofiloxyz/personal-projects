#!/usr/bin/python3
# Integração com os menus do rofi

import subprocess


class Rofi:
    @staticmethod
    def simple_prompt(prompt: str, message=""):
        if message != "":
            message = f" -mesg \"{message}\""

        cmd = f"rofi -dmenu -p '{prompt}' -l 0 -theme-str 'entry " \
              "{ placeholder: \"\"; } inputbar { children: [prompt, " \
              "textbox-prompt-colon, entry]; } listview { border: 0; }'" \
              f"{message}"
        user_input = subprocess.run(cmd, shell=True, capture_output=True) \
            .stdout.decode('utf-8')
        return user_input.strip("\n")

    @staticmethod
    def custom_dmenu(prompt: str, dmenu: list, message=""):
        if message != "":
            message = f" -mesg \"{message}\""

        lines = "\n".join(dmenu)
        input_file = "/tmp/python_rofi_integration.dmenulist"
        with open(input_file, "w") as rif:
            rif.writelines(lines)

        if len(dmenu) < 15:
            dmenu_lines = str(len(dmenu))
        else:
            dmenu_lines = "15"

        cmd = f"rofi -dmenu -i -input {input_file} -p '{prompt}'" \
              f" -l {dmenu_lines} -theme-str 'entry {{ placeholder: \"\"; }} "\
              "inputbar { children: [prompt, textbox-prompt-colon, entry]; }'"\
              f"{message}; rm {input_file}"
        user_input = subprocess.run(cmd, shell=True, capture_output=True) \
            .stdout.decode('utf-8')
        return user_input.strip("\n")

    @staticmethod
    def message(message: str):
        cmd = f"rofi -e \"{message}\""
        subprocess.run(cmd, shell=True)
