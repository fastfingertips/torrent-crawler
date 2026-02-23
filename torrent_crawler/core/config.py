import os

from dynaconf import Dynaconf

current_dir = os.path.dirname(os.path.abspath(__file__))
# core/ is in torrent_crawler/, so go up two levels to reach project root where settings.toml is
root_dir = os.path.dirname(os.path.dirname(current_dir))

settings = Dynaconf(
    envvar_prefix="TORRENT_CRAWLER",
    settings_files=[os.path.join(root_dir, "settings.toml"), os.path.join(root_dir, ".secrets.toml")],
)

# `envvar_prefix` = export envvars with `export TORRENT_CRAWLER_FOO=bar`
# `settings_files` = Load these files in the order.
