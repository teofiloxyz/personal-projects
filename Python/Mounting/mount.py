#!/usr/bin/python3

import os
import subprocess
import json


class Mount:
    def main(self) -> None:
        self.check_sdevs()

        sdevs_info = self.get_sdevs_info()
        unmounted_parts = self.get_unmounted_parts(sdevs_info)
        if len(unmounted_parts) == 0:
            self.error("It seems there are no devices/partitions to mount")

        target = self.choose_target(unmounted_parts)
        mount_dir = self.get_mount_dir(target)

        self.mount_target(target, mount_dir)
        self.ranger_to_mount_dir(mount_dir)

    def error(self, message: str) -> None:
        subprocess.Popen(["paplay", "rejected.wav"], start_new_session=True)
        print("Error: " + message)
        exit(1)

    def check_sdevs(self) -> None:
        cmd = "lsblk --include 8".split()
        err = subprocess.call(
            cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
        )
        if err != 0:
            self.error("No special devices found...")

    def get_sdevs_info(self) -> list[dict[str, str]]:
        cmd = (
            "lsblk --json --include 8 --output NAME,SIZE,TYPE,"
            "FSTYPE,MOUNTPOINT,MODEL".split()
        )
        sdevs_json = subprocess.run(cmd, capture_output=True).stdout.decode(
            "utf-8"
        )
        return json.loads(sdevs_json)["blockdevices"]

    def get_unmounted_parts(self, sdevs_info: list[dict]) -> list[dict]:
        unmounted_parts = list()
        for sdev in sdevs_info:
            if sdev["mountpoint"] is not None:
                continue
            elif sdev["type"] == "part":
                unmounted_parts.append(
                    {
                        "model": sdev["model"],
                        "size": sdev["size"],
                        "fstype": sdev["fstype"],
                        "path": f"/dev/{sdev['name']}",
                    }
                )
            try:
                sdev_children = sdev["children"]
            except KeyError:
                continue
            for child in sdev_children:
                if child["mountpoint"] is not None or child["type"] != "part":
                    continue
                unmounted_parts.append(
                    {
                        "model": sdev["model"],
                        "size": child["size"],
                        "fstype": child["fstype"],
                        "path": f"/dev/{child['name']}",
                    }
                )

        return unmounted_parts

    def choose_target(self, unmounted_parts: list[dict]) -> dict[str, str]:
        if len(unmounted_parts) == 1:
            return unmounted_parts[0]

        print("Found the following unmounted partitions:")
        while True:
            [
                print(
                    f"[{n}] {part['model']}: {part['path']} "
                    f"({part['size']} {part['fstype']})"
                )
                for n, part in enumerate(unmounted_parts, 1)
            ]
            ans = input("\nChoose the one you want to mount: ")
            if ans == "q":
                print("Aborting...")
                exit(0)
            try:
                return unmounted_parts[int(ans) - 1]
            except (ValueError, IndexError):
                print("Invalid answer...\n")

    def get_mount_dir(self, target: dict[str, str]) -> str:
        mount_dir = "/mnt/usb/"
        cmd = f"mountpoint {mount_dir}".split()
        err = subprocess.call(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if err == 0:
            mount_dir = f"/mnt/{target['model'].replace(' ', '_')}"
            while os.path.isdir(mount_dir):
                mount_dir += "_"
            cmd = f"sudo mkdir {mount_dir}".split()
            err = subprocess.call(cmd)
            if err != 0:
                self.error("Creating mount folder")
        return mount_dir

    def mount_target(self, target: dict[str, str], mount_dir: str) -> None:
        print(
            f"Mounting {target['model']}: {target['path']} "
            f"({target['size']} {target['fstype']})"
        )

        # Adicionar (-o uid=... -o gid=...) caso necessário
        cmd = f"sudo mount {target['path']} {mount_dir}".split()
        err = subprocess.call(cmd)
        if err != 0:
            self.error("Mounting device...")

        subprocess.Popen(["paplay", "mounting.wav"])
        print(f"Mounted {target['path']} on {mount_dir}\n")

    def ranger_to_mount_dir(self, mount_dir: str) -> None:
        if input(":: Open ranger on the mounting point? [Y/n] ") in (
            "",
            "y",
            "Y",
        ):
            cmd = f"alacritty -e ranger {mount_dir}".split()
            subprocess.Popen(cmd, start_new_session=True)
