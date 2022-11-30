#!/usr/bin/python3

import os
import subprocess
import json


class Dismount:
    def main(self) -> None:
        sdevs_info = self.get_sdevs_info()
        mounted_parts = self.get_mounted_parts(sdevs_info)
        if len(mounted_parts) == 0:
            self.error("It seems there are no devices/partitions to dismount")

        target = self.choose_target(mounted_parts)
        self.dismount_target(target)
        self.remove_empty_mnt_dirs()

    def error(self, message: str) -> None:
        subprocess.Popen(["paplay", "rejected.wav"], start_new_session=True)
        print("Error: " + message)
        exit(1)

    def get_sdevs_info(self) -> list[dict[str, str]]:
        cmd = (
            "lsblk --json --include 8 --output NAME,SIZE,TYPE,"
            "FSTYPE,MOUNTPOINT,MODEL".split()
        )
        sdevs_json = subprocess.run(cmd, capture_output=True).stdout.decode(
            "utf-8"
        )
        return json.loads(sdevs_json)["blockdevices"]

    def get_mounted_parts(self, sdevs_info: list[dict]) -> list[dict]:
        mounted_parts = list()
        for sdev in sdevs_info:
            if sdev["type"] == "part" or sdev["mountpoint"] is not None:
                mounted_parts.append(
                    {
                        "model": sdev["model"],
                        "size": sdev["size"],
                        "fstype": sdev["fstype"],
                        "path": f"/dev/{sdev['name']}",
                        "mountpoins": sdev["mountpoint"],
                    }
                )
            try:
                sdev_children = sdev["children"]
            except KeyError:
                continue
            for child in sdev_children:
                if child["mountpoint"] is None:
                    continue
                mounted_parts.append(
                    {
                        "model": sdev["model"],
                        "size": child["size"],
                        "fstype": child["fstype"],
                        "path": f"/dev/{child['name']}",
                        "mountpoint": child["mountpoint"],
                    }
                )

        return mounted_parts

    def choose_target(self, mounted_parts: list[dict]) -> dict[str, str]:
        if len(mounted_parts) == 1:
            return mounted_parts[0]

        print("Found the following mounted partitions:")
        while True:
            [
                print(
                    f"[{n}] {part['model']}: {part['path']} "
                    f"({part['size']} {part['fstype']})"
                )
                for n, part in enumerate(mounted_parts, 1)
            ]
            ans = input("\nChoose the one you want to dismount: ")
            if ans == "q":
                print("Aborting...")
                exit(0)
            try:
                return mounted_parts[int(ans) - 1]
            except (ValueError, IndexError):
                print("Invalid answer...\n")

    def dismount_target(self, target: dict[str, str]) -> None:
        print(
            f"Dismounting {target['model']}: {target['path']} "
            f"({target['size']} {target['fstype']})"
        )

        cmd = f"sudo umount {target['mountpoint']}".split()
        err = subprocess.call(cmd)
        if err != 0:
            self.error("Dismounting device...")

        subprocess.Popen(["paplay", "dismounting.wav"])
        print(f"Dismounted {target['path']} from {target['mountpoint']}")

    def remove_empty_mnt_dirs(self) -> None:
        for folder in os.listdir("/mnt"):
            folder = os.path.join("/mnt", folder)

            # Eliminates all non-mountpoint folders except /mnt/usb
            if folder == "/mnt/usb":
                continue

            cmd = f"mountpoint {folder}".split()
            err = subprocess.call(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            if err != 0:
                cmd = f"sudo rmdir {folder}".split()
                err = subprocess.call(cmd)
                if err != 0:
                    self.error(f"Removing {folder}")
