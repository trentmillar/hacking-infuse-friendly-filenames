# run -> sudo python3 rename_my_files.py

import os
import re

s_and_e = re.compile(r"(s[0-9]{1,3}(\.|_){0,1}e[0-9]{1,4})|([0-9]{1,3}x[0-9]{1,4})", re.IGNORECASE)


def contains_season_episode(name):
    return s_and_e.search(name) is not None


sea = re.compile(r"^((season|s){0,1}( ){0,1}[0-9])$", re.IGNORECASE)


def get_season_and_show(folder_parts):
    length = len(folder_parts)
    if length > 2:
        print("WARN: Path to video is {0} deep but shouldn't exceed 2 levels".format(length))

    if length == 0:
        return None, None

    # first folder is show name
    show = folders[0:1][0].replace(" ", "-")

    if length == 1:
        return show, None

    season = None
    for folder in folders[1:][::-1]:
        group = sea.search(folder)
        if not group:
            continue
        season = re.sub(r"[^0-9.]{1,3}", "", group.group(1))
        if season:
            season = season.zfill(2)
            break
    return show, season


ep = re.compile(r"^(e){0,1}[0-9]{1,4}( ){0,1}", re.IGNORECASE)


def get_episode_number(name):
    group = ep.search(name)
    if not group:
        return None
    return group.group(0).zfill(2)


def execute_command(command):
    return os.system(command)


"""
If connecting to a local folder then just set mount_dir with the path and remove all the mount logic
"""

# Needed if connecting to shared folders over SMB
smb_username = input("SMB Username:\n")
smb_password = input("SMB Password:\n")

# MacOS/POSIX specific pathing
mount_dir = "/Users/tmillar/dev/vids"
mkdir = "mkdir {0}".format(mount_dir)
mount = "mount_smbfs //{0}:{1}@NAS/video/home%20video/TV%20Shows {2}".format(smb_username, smb_password, mount_dir)
umount = "umount {0}".format(mount_dir)

# Easier to mount my NAS drive
result = execute_command(umount)
result = execute_command(mkdir)
result = execute_command(mount)

extensions = [".mkv", ".avi", ".mp4", ".m4v"]
for root, dirs, files in os.walk(mount_dir):
    video_files = [file for file in files if os.path.splitext(file)[1] in extensions]
    if len(video_files) == 0:
        continue

    folders = list(filter(None, root.replace(mount_dir, "").split("/")))
    show, season = get_season_and_show(folders)

    # This could get ugly
    for file in video_files:
        # does file match SNNENN
        if contains_season_episode(file):
            print("PASS-ABLE: this may be usable, {0}".format(file))
            # We can do better if we have a show and season
            if not show or not season:
                continue

        episode = get_episode_number(file)

        if not show or not season or not episode:
            print("ERROR: this, {0}/{1} became, {2}-s{3}_e{4}".format("/".join(folders), file, show, season, episode))
            continue

        extension = os.path.splitext(file)[1]
        print("PASS: {0}_s{1}e{2}.{3}".format(show, season, episode, extension))

result = execute_command(umount)
