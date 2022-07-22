#!/usr/bin/python3
# Mounting tool for sdevs

import os
import sys
import subprocess
import json


class Mounting:
    def __init__(self):
        self.usb_mnt = '/mnt/usb/'
        self.m_sound = 'mount.wav'
        self.d_sound = 'dismount.wav'

    def main(self):
        self.check_option()
        self.process()

    def error(self, msg):
        rej_sound = 'rejected.wav'
        subprocess.Popen(['paplay', rej_sound], start_new_session=True)
        print('Error: ' + msg)
        exit(1)

    def check_option(self):
        self.opst_dict = {'mount': self.mount,
                          'dismount': self.dismount}

        try:
            self.option = sys.argv[1]
        except IndexError:
            self.error('Command needs an argument: mount or dismount')

        if self.option in self.opst_dict.keys():
            self.process = self.opst_dict[self.option]
        else:
            self.error("Argument needs to be 'mount' or 'dismount'")

    def mount(self):
        # needs refactoring
        def check_unmounted():
            cmd = 'lsblk --include 8'.split()
            err = subprocess.call(cmd, stderr=subprocess.DEVNULL,
                                  stdout=subprocess.DEVNULL)
            if err != 0:
                self.error('No devices found to mount')

            cmd = 'lsblk --json --include 8 --output NAME,SIZE,TYPE,' \
                'FSTYPE,MOUNTPOINT,MODEL'.split()
            sdevs_json = subprocess.run(cmd, capture_output=True) \
                .stdout.decode('utf-8')
            sdevs_info = json.loads(sdevs_json)['blockdevices']

            unmounted_devs = list()
            for sdev in sdevs_info:
                if sdev['mountpoint'] is not None:
                    continue
                elif sdev['type'] == 'part':
                    unmounted_devs.append({'model': sdev['model'],
                                           'size': sdev['size'],
                                           'fstype': sdev['fstype'],
                                           'path': f"/dev/{sdev['name']}"})
                try:
                    sdev_children = sdev['children']
                except KeyError:
                    continue
                for child in sdev_children:
                    if child['mountpoint'] is not None \
                            or child['type'] != 'part':
                        continue
                    unmounted_devs.append({'model': sdev['model'],
                                           'size': child['size'],
                                           'fstype': child['fstype'],
                                           'path': f"/dev/{child['name']}"})

            if len(unmounted_devs) == 0:
                self.error("It seems there are no devices/partitions to mount")
            return unmounted_devs

        def choose_target():
            if len(unmounted_devs) == 1:
                return unmounted_devs[0]

            print('Found the following unmounted devices/partitions:')
            while True:
                [print(f"[{n}] {part['model']}: {part['path']} "
                       f"({part['size']} {part['fstype']})")
                 for n, part in enumerate(unmounted_devs, 1)]
                ans = input('\nChoose the one you want to mount: ')
                if ans == 'q':
                    print('Aborting...')
                    exit(0)
                try:
                    return unmounted_devs[int(ans) - 1]
                except (ValueError, IndexError):
                    print("Invalid answer...\n")

        def get_mount_dir():
            mount_dir = self.usb_mnt
            cmd = f'mountpoint {mount_dir}'.split()
            err = subprocess.call(cmd, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
            if err == 0:
                mount_dir = f"/mnt/{target['model'].replace(' ', '_')}"
                # mount dir needs to be unique
                while os.path.isdir(mount_dir):
                    mount_dir += '_'
                cmd = f"sudo mkdir {mount_dir}".split()
                err = subprocess.call(cmd)
                if err != 0:
                    self.error('Creating mount folder')
            return mount_dir

        def mount_target():
            print(f"Mounting {target['model']}: {target['path']} "
                  f"({target['size']} {target['fstype']})")

            # adicionar (-o uid=... -o gid=...) caso necessário
            cmd = f"sudo mount {target['path']} {mount_dir}".split()
            err = subprocess.call(cmd)
            if err != 0:
                self.error("Mounting device")

            subprocess.Popen(['paplay', self.m_sound])
            print(f"Mounted {target['path']} on {mount_dir}\n")

        def ranger_to_mount_dir():
            if input(":: Do you want to open ranger on the mounting point? "
                     "[Y/n] ") in ('', 'y', 'Y'):
                cmd = f'alacritty -e ranger {mount_dir}'.split()
                subprocess.Popen(cmd, start_new_session=True)

        unmounted_devs = check_unmounted()
        target = choose_target()
        mount_dir = get_mount_dir()
        mount_target()
        ranger_to_mount_dir()

    def dismount(self):
        def check_mounted():
            cmd = 'lsblk --json --include 8 --output NAME,SIZE,TYPE,' \
                'FSTYPE,MOUNTPOINT,MODEL'.split()
            sdevs_json = subprocess.run(cmd, capture_output=True) \
                .stdout.decode('utf-8')
            sdevs_info = json.loads(sdevs_json)['blockdevices']

            mounted_devs = list()
            for sdev in sdevs_info:
                if sdev['type'] == 'part' \
                        or sdev['mountpoint'] is not None:
                    mounted_devs.append({'model': sdev['model'],
                                         'size': sdev['size'],
                                         'fstype': sdev['fstype'],
                                         'path': f"/dev/{sdev['name']}",
                                         'mountpoins': sdev['mountpoint']})
                try:
                    sdev_children = sdev['children']
                except KeyError:
                    continue
                for child in sdev_children:
                    if child['mountpoint'] is None:
                        continue
                    mounted_devs.append({'model': sdev['model'],
                                         'size': child['size'],
                                         'fstype': child['fstype'],
                                         'path': f"/dev/{child['name']}",
                                         'mountpoint': child['mountpoint']})

            if len(mounted_devs) == 0:
                self.error("It seems there are no devices/partitions "
                           "to dismount")
            return mounted_devs

        def choose_target():
            if len(mounted_devs) == 1:
                return mounted_devs[0]
            print('Found the following mounted devices/partitions:')

            while True:
                [print(f"[{n}] {part['model']}: {part['path']} "
                       f"({part['size']} {part['fstype']})")
                 for n, part in enumerate(mounted_devs, 1)]
                ans = input('\nChoose the one you want to dismount: ')
                if ans == 'q':
                    print('Aborting...')
                    exit(0)
                try:
                    return mounted_devs[int(ans) - 1]
                except (ValueError, IndexError):
                    print("Invalid answer...\n")

        def dismount_target():
            print(f"Dismounting {target['model']}: {target['path']} "
                  f"({target['size']} {target['fstype']})")

            cmd = f"sudo umount {target['mountpoint']}".split()
            err = subprocess.call(cmd)
            if err != 0:
                self.error("Dismounting device")

            subprocess.Popen(['paplay', self.d_sound])
            print(f"Dismounted {target['path']} from {target['mountpoint']}")

        def remove_empty_dirs():
            for folder in os.listdir('/mnt'):
                folder = os.path.join('/mnt', folder)
                # Eliminates all non-mountpoint folders except /mnt/usb
                if folder + '/' != self.usb_mnt:
                    cmd = f'mountpoint {folder}'.split()
                    err = subprocess.call(cmd, stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
                    if err != 0:
                        cmd = f'sudo rmdir {folder}'.split()
                        err = subprocess.call(cmd)
                        if err != 0:
                            self.error("Removing the following "
                                       f"folder: {folder}")

        mounted_devs = check_mounted()
        target = choose_target()
        dismount_target()
        remove_empty_dirs()


Mounting().main()
