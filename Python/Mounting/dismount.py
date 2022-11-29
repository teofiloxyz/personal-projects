#!/usr/bin/python3

import os
import subprocess
import json


class Dismount:
    def check_mounted():
        cmd = (
            "lsblk --json --include 8 --output NAME,SIZE,TYPE,"
            "FSTYPE,MOUNTPOINT,MODEL".split()
        )
        sdevs_json = subprocess.run(cmd, capture_output=True).stdout.decode(
            "utf-8"
        )
        sdevs_info = json.loads(sdevs_json)["blockdevices"]

        mounted_devs = list()
        for sdev in sdevs_info:
            if sdev["type"] == "part" or sdev["mountpoint"] is not None:
                mounted_devs.append(
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
                mounted_devs.append(
                    {
                        "model": sdev["model"],
                        "size": child["size"],
                        "fstype": child["fstype"],
                        "path": f"/dev/{child['name']}",
                        "mountpoint": child["mountpoint"],
                    }
                )

        if len(mounted_devs) == 0:
            self.error(
                "It seems there are no devices/partitions " "to dismount"
            )
        return mounted_devs

    def choose_target():
        if len(mounted_devs) == 1:
            return mounted_devs[0]
        print("Found the following mounted devices/partitions:")

        while True:
            [
                print(
                    f"[{n}] {part['model']}: {part['path']} "
                    f"({part['size']} {part['fstype']})"
                )
                for n, part in enumerate(mounted_devs, 1)
            ]
            ans = input("\nChoose the one you want to dismount: ")
            if ans == "q":
                print("Aborting...")
                exit(0)
            try:
                return mounted_devs[int(ans) - 1]
            except (ValueError, IndexError):
                print("Invalid answer...\n")

    def dismount_target():
        print(
            f"Dismounting {target['model']}: {target['path']} "
            f"({target['size']} {target['fstype']})"
        )

        cmd = f"sudo umount {target['mountpoint']}".split()
        err = subprocess.call(cmd)
        if err != 0:
            self.error("Dismounting device")

        subprocess.Popen(["paplay", self.d_sound])
        print(f"Dismounted {target['path']} from {target['mountpoint']}")

    def remove_empty_dirs():
        for folder in os.listdir("/mnt"):
            folder = os.path.join("/mnt", folder)
            # Eliminates all non-mountpoint folders except /mnt/usb
            if folder + "/" != self.usb_mnt:
                cmd = f"mountpoint {folder}".split()
                err = subprocess.call(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                if err != 0:
                    cmd = f"sudo rmdir {folder}".split()
                    err = subprocess.call(cmd)
                    if err != 0:
                        self.error(
                            "Removing the following " f"folder: {folder}"
                        )

    mounted_devs = check_mounted()
    target = choose_target()
    dismount_target()
    remove_empty_dirs()
