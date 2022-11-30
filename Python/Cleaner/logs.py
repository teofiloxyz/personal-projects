#!/usr/bin/python3


class Logs:
    def manage(self):
        # Log files get copied and truncated
        var_logs = "/var/log"

        tmp_dir = f"/tmp/logs_management_{self.today}"
        tmp_var = f"{tmp_dir}/var"
        self.create_folder(tmp_var)

        if os.listdir(var_logs) != 0:
            [
                self.copy_file_or_folder(
                    os.path.join(var_logs, file_dir), tmp_var
                )
                for file_dir in os.listdir(var_logs)
            ]
            [
                os.truncate(os.path.join(root_dirs_files[0], file), 0)
                for root_dirs_files in os.walk(var_logs)
                for file in root_dirs_files[2]
            ]

        arc_dst = os.path.join(self.arcs_dir, f"Logs/{self.today}.tar.xz")
        self.create_archive(tmp_dir, arc_dst)
        self.remove_folder(tmp_dir)
