import json
import os

from src.os_layer import config_path, post_update_file


class Config:
    def __init__(self):
        self.base_dir = os.environ.get("BASE_DIRECTORY")
        if not os.path.exists(post_update_file):
            with open(post_update_file, "w") as ff:
                ff.write("True")

        with open(post_update_file, "r") as f:
            x = f.read()
            self.post_update = True if x == "True" else False

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                dat = json.load(f)

                if (
                    "custom_ids" not in dat.keys()
                ):  # custom_ids was an addition to v1.5, must create for
                    # current users with existing config.json from v1.5
                    dat["custom_ids"] = {}
                    self.cfg = dat

                    with open(config_path, "w") as file:
                        json.dump(self.cfg, file)

        if not os.path.exists(config_path):  # Build dictionary for first time
            dat = {
                "post_update": True,
                "gamedir": "",
                "steamid": "",
                "seamless-coop": False,
                "custom_ids": {},
            }

            self.cfg = dat
            with open(config_path, "w") as f:
                json.dump(self.cfg, f)
        else:
            with open(config_path, "r") as f:
                js = json.load(f)
                self.cfg = js

    def set_update(self, val):
        self.post_update = val
        with open(post_update_file, "w") as f:
            f.write("True" if val else "False")

    def set(self, k, v):
        self.cfg[k] = v
        with open(config_path, "w") as f:
            json.dump(self.cfg, f)

    def add_to(self, k, v):
        self.cfg[k].update(v)
        with open(config_path, "w") as f:
            json.dump(self.cfg, f)

    def delete_custom_id(self, k):
        self.cfg["custom_ids"].pop(k)
        with open(config_path, "w") as f:
            json.dump(self.cfg, f)


config = Config()
gamedir = str(config.cfg["gamedir"])
