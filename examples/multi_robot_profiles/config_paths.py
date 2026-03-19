import os
import shutil
from pathlib import Path


def get_profiled_config_path(
    package_share: Path,
    package_src: Path,
    config_dir: str,
    config_name: str,
    fallback_pkg_share: Path,
    fallback_pkg_src: Path,
    allow_shared_config: bool = False,
    copy_fallback_to_profile: bool = True,
):
    config_pkg = os.getenv("CONFIG_PKG", "").strip()
    robot_profile = os.getenv("ROBOT_PROFILE", "").strip()
    config_root = Path(config_dir) / config_pkg if config_pkg else Path(config_dir)

    fallback_source = fallback_pkg_src if fallback_pkg_src.exists() else fallback_pkg_share

    if not config_pkg or not robot_profile:
        return fallback_source

    profiled = package_share / config_root / robot_profile / config_name
    if profiled.exists():
        return profiled

    shared = package_share / config_root / config_name
    if allow_shared_config and shared.exists():
        return shared

    if copy_fallback_to_profile and fallback_source.exists():
        dst = package_src / config_root / robot_profile / config_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fallback_source, dst)
        return dst

    return profiled
