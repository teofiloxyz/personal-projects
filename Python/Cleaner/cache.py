#!/usr/bin/python3


class Cache:
    def manage(self):
        user_cache, root_cache, var_cache = (
            os.path.expanduser("~/.cache"),
            "/root/.cache",
            "/var/cache",
        )
        user_cache_excp = "exception_1", "exception_2", "exception_3"
        root_cache_excp = "exception_1", "exception_2", "exception_3"
        var_cache_excp = "exception_1", "exception_2", "exception_3"

        tmp_dir = f"/tmp/cache_management_{self.today}"
        tmp_user, tmp_root, tmp_var = (
            f"{tmp_dir}/user_cache",
            f"{tmp_dir}/root_cache",
            f"{tmp_dir}/var_cache",
        )
        self.create_folder(" ".join([tmp_user, tmp_root, tmp_var]))

        if os.listdir(user_cache) != 0:
            [
                self.move_file_or_folder(
                    os.path.join(user_cache, file_dir), tmp_user
                )
                for file_dir in os.listdir(user_cache)
                if file_dir not in user_cache_excp
            ]

        if os.listdir(root_cache) != 0:
            [
                self.move_file_or_folder(
                    os.path.join(root_cache, file_dir), tmp_root
                )
                for file_dir in os.listdir(root_cache)
                if file_dir not in root_cache_excp
            ]

        if os.listdir(var_cache) != 0:
            [
                self.move_file_or_folder(
                    os.path.join(var_cache, file_dir), tmp_var
                )
                for file_dir in os.listdir(var_cache)
                if file_dir not in var_cache_excp
            ]

        arc_dst = os.path.join(self.arcs_dir, f"Cache/{self.today}.tar")
        # Não é necessário compressão pq não fará grande diferença em cache
        self.create_archive(tmp_dir, arc_dst, compress=False)
        self.remove_folder(tmp_dir)

        archives_max_mb = int("<number>")
        while self.check_dir_size_mb(self.arcs_dir) > archives_max_mb:
            self.remove_file(self.get_oldest_file(self.arcs_dir, ".tar"))
