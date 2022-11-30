#!/usr/bin/python3


class History:
    def manage(self):
        user_hist_list = "hist_1", "hist_2", "hist_3"
        root_hist_list = "hist_1", "hist_2", "hist_3"

        tmp_dir = f"/tmp/history_management_{self.today}"
        tmp_user, tmp_root = f"{tmp_dir}/user", f"{tmp_dir}/root"
        self.create_folder(" ".join([tmp_user, tmp_root]))

        [
            self.move_file_or_folder(file, tmp_user)
            for file in user_hist_list
            if os.path.isfile(file)
        ]

        [
            self.move_file_or_folder(file, tmp_root)
            for file in root_hist_list
            if os.path.isfile(file)
        ]

        arc_dst = os.path.join(self.arcs_dir, f"History/{self.today}.tar.xz")
        self.create_archive(tmp_dir, arc_dst)
        self.remove_folder(tmp_dir)
