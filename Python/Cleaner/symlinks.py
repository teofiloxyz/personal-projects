#!/usr/bin/python3


class Symlinks:
    def manage(self):
        cmd = "find / -xtype l -print".split()
        broken_slinks_list = (
            subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            .stdout.decode("utf-8")
            .split("\n")
        )
        if len(broken_slinks_list) == 0:
            return

        for link in broken_slinks_list:
            if not os.path.islink(link):
                continue
            if (
                link.startswith("/run")
                or link.startswith("/proc")
                or link.startswith("/mnt")
            ):
                continue
            try:
                self.remove_file(link)
            except PermissionError:
                continue
