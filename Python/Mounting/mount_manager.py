import os
import subprocess
import json
from dataclasses import dataclass

# need better naming for classes, methods and vars


@dataclass
class UnmountedSDev:
    model: str
    size: str
    file_sys_type: str
    dev_path: str


@dataclass
class MountedSDev(UnmountedSDev):
    mount_point_path: str


class MountManager:
    def __init__(self) -> None:
        self.sdevs = SDevices()

    def mount(self) -> None:
        err = self.sdevs.check_sdevs()
        if err != 0:
            self._error("No devices found...")

        unmounted_parts = self.sdevs.get_unmounted_parts()
        if len(unmounted_parts) == 0:
            self._error("It seems there are no devices/partitions to mount")
        target = self._choose_target(unmounted_parts, is_mount=True)
        mount_dir = self._get_mount_dir(target)

        self._mount_target(target, mount_dir)
        self._open_ranger_on_mount_dir(mount_dir)

    def dismount(self) -> None:
        mounted_parts = self.sdevs.get_mounted_parts()
        if len(mounted_parts) == 0:
            self._error("It seems there are no devices/partitions to dismount")

        target = self._choose_target(mounted_parts, is_mount=False)
        self._dismount_target(target)
        self._remove_empty_mnt_dirs()

    def _choose_target(
        self, parts: list[UnmountedSDev] | list[MountedSDev], is_mount: bool
    ) -> UnmountedSDev | MountedSDev:
        if len(parts) == 1:
            return parts[0]

        if is_mount:
            print("Found the following unmounted partitions:")
        else:
            print("Found the following mounted partitions:")

        while True:
            [
                print(
                    f"[{n}] {part.model}: {part.dev_path} "
                    f"({part.size} {part.file_sys_type})"
                )
                for n, part in enumerate(parts, 1)
            ]
            prompt = input("\nChoose the one you want to mount/dismount: ")
            if prompt == "q":
                print("Aborting...")
                exit(0)
            try:
                return parts[int(prompt) - 1]
            except (ValueError, IndexError):
                print("Invalid answer...\n")

    def _get_mount_dir(self, target: UnmountedSDev) -> str:
        mount_dir = "/mnt/usb/"
        cmd = f"mountpoint {mount_dir}".split()
        err = subprocess.call(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if err == 0:
            mount_dir = f"/mnt/{target.model.replace(' ', '_')}"
            while os.path.isdir(mount_dir):
                mount_dir += "_"
            cmd = f"sudo mkdir {mount_dir}".split()
            err = subprocess.call(cmd)
            if err != 0:
                self._error("Creating mount folder")
        return mount_dir

    def _mount_target(self, target: UnmountedSDev, mount_dir: str) -> None:
        print(
            f"Mounting {target.model}: {target.dev_path} "
            f"({target.size} {target.file_sys_type})"
        )

        # Adicionar (-o uid=... -o gid=...) caso necessário
        cmd = f"sudo mount {target.dev_path} {mount_dir}"
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            self._error("Mounting device...")
        print(f"Mounted {target.dev_path} on {mount_dir}\n")

    def _dismount_target(self, target: MountedSDev) -> None:
        print(
            f"Dismounting {target.model}: {target.dev_path} "
            f"({target.size} {target.file_sys_type})"
        )

        cmd = f"sudo umount {target.mount_point_path}"
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            self._error("Dismounting device...")
        print(f"Dismounted {target.dev_path} from {target.mount_point_path}")

    def _open_ranger_on_mount_dir(self, mount_dir: str) -> None:
        prompt = input(":: Open ranger on the mounting point? [Y/n] ")
        if prompt.lower() in ("", "y"):
            cmd = f"alacritty -e ranger {mount_dir}"
            subprocess.Popen(cmd, shell=True, start_new_session=True)

    def _remove_empty_mnt_dirs(self) -> None:
        """Eliminates all non-mountpoint folders except /mnt/usb"""

        for folder in os.listdir("/mnt"):
            folder = os.path.join("/mnt", folder)
            if folder == "/mnt/usb":
                continue

            cmd = f"mountpoint {folder}".split()
            err = subprocess.call(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            if err != 0:
                os.rmdir(folder)

    def _error(self, message: str) -> None:
        subprocess.Popen(["paplay", "rejected.wav"], start_new_session=True)
        print(f"Error: {message}")
        exit(1)


class SDevices:  # is it storage or special devs (e.g.: /dev/sda)?
    def check_sdevs(self) -> int:
        cmd = "lsblk --include 8".split()
        return subprocess.call(
            cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
        )

    def get_unmounted_parts(self) -> list[UnmountedSDev]:
        unmounted_parts = []
        sdevs_info = self._get_info()
        for sdev in sdevs_info:
            if sdev["mountpoint"]:
                continue
            elif sdev["type"] == "part":
                unmounted_parts.append(self._create_unmounted_sdev(sdev))
            try:
                sdev_children = sdev["children"]
            except KeyError:
                continue
            for child in sdev_children:
                if child["mountpoint"] is not None or child["type"] != "part":
                    continue
                unmounted_parts.append(self._create_unmounted_sdev(child))
        return unmounted_parts

    def get_mounted_parts(self) -> list[MountedSDev]:
        mounted_parts = []
        sdevs_info = self._get_info()
        for sdev in sdevs_info:
            if sdev["type"] == "part" or sdev["mountpoint"]:
                mounted_parts.append(self._create_mounted_sdev(sdev))
            try:
                sdev_children: dict = sdev["children"]
            except KeyError:
                continue
            for child in sdev_children:
                if not child["mountpoint"]:
                    continue
                mounted_parts.append(self._create_mounted_sdev(child))
        return mounted_parts

    def _get_info(self) -> list[dict]:
        cmd = (
            "lsblk --json --include 8 --output NAME,SIZE,TYPE,"
            "FSTYPE,MOUNTPOINT,MODEL".split()
        )
        sdevs_json = subprocess.run(cmd, capture_output=True).stdout.decode(
            "utf-8"
        )
        return json.loads(sdevs_json)["blockdevices"]

    def _create_unmounted_sdev(self, part: dict) -> UnmountedSDev:
        return UnmountedSDev(
            model=part["model"],
            size=part["size"],
            file_sys_type=part["fstype"],
            dev_path=f"/dev/{part['name']}",
        )

    def _create_mounted_sdev(self, part: dict) -> MountedSDev:
        return MountedSDev(
            model=part["model"],
            size=part["size"],
            file_sys_type=part["fstype"],
            dev_path=f"/dev/{part['name']}",
            mount_point_path=part["mountpoint"],
        )
