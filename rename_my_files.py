# run -> python3 rename_my_files.py

import os
import re
import sys
import stat


def get_expression(name, exp):
    group = exp.search(name)
    if group is None:
        return None, None
    sande = group.group()
    all = re.findall("[0-9]+", sande)
    if len(all) == 1:
        return None, all[0].zfill(2)  # assuming we just have episode
    if len(all) == 2:
        return all[0].zfill(2), all[1].zfill(2)
    else:
        print("ERROR: found {0}".format(",".join(all)))
        raise Exception("should never match more than 2 or less than 1")


s_and_e = re.compile(r"(s[0-9]{1,3}(\.|_| ){0,1}e[0-9]{1,4})|([0-9]{1,3}x[0-9]{1,4})", re.IGNORECASE)


def get_season_and_episode(name):
    return get_expression(name, s_and_e)


ep_and_s = re.compile(r"(s[0-9]{1,3}(\.|_| ){0,1}e[0-9]{1,4})|([0-9]{1,3}x[0-9]{1,4})|(^[0-9]{1,4}( ))|(^[0-9]{1,4}$)",
                      re.IGNORECASE)


def get_season_and_episode_aggressive(name):
    return get_expression(name, ep_and_s)


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


ep = re.compile(r"(^(e){0,1}[0-9]{1,4}( |.){0,1})|(( |.){1}(e){1}[0-9]{1,4}( ){0,1})", re.IGNORECASE)


def get_episode_number(name):
    group = ep.search(name)
    if not group:
        return None
    return re.findall("[0-9]+", group.group(0))[0].zfill(2)


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

extensions = [
    ".mkv", ".avi", ".mp4", ".m4v", ".flv", ".iso", ".img", ".mov", ".mpeg", ".mpg", ".ogv", ".webm"
]


def persist_log(msg, filename, root_path, level="error"):
    log_file = os.path.join(root_path, "{0}.{1}.txt".format(filename, level))
    with open(log_file, 'a') as log:
        log.write(msg)


for root, dirs, files in os.walk(mount_dir):
    video_files = [file for file in files if os.path.splitext(file)[1] in extensions]
    if len(video_files) == 0:
        continue

    folders = list(filter(None, root.replace(mount_dir, "").split("/")))
    show, folder_season = get_season_and_show(folders)

    # This could get ugly
    for file in video_files:
        # does file match SNNENN
        filename = str(os.path.splitext(file)[0]).replace(show, "")
        if folder_season:
            file_season, episode = get_season_and_episode_aggressive(filename)
        else:
            file_season, episode = get_season_and_episode(filename)
        if file_season is not None and episode is not None:
            print("\tPASS-ABLE: this may be usable, {0}".format(file))

        if episode is None:
            persist_log("ERROR: missing episode from, file:{0}".format(file), file, root)
            continue

        if file_season is None and folder_season is None:
            persist_log("ERROR: missing season from, file:{0} or folders:{1}".format(file, "/".join(folders)), file,
                        root)
            continue

        # We can do better if we have a show and season
        if not show:  # todo, get show from filename - now it is just from parent folder
            persist_log("ERROR: missing show name,{0} out of {1}".format(show, file), file, root)
            continue

        # other_episode = get_episode_number(file)

        if not folder_season and not file_season and folder_season != file_season:
            err = "WARN: folder season {0} is not equal to file season {1}".format(folder_season, file_season)
            persist_log(err, file, root, "warn")

        # if episode != other_episode:
        #     err = "WARN: episode {0} is not equal to episode {1}".format(episode, other_episode)
        #     persist_log(err, file, root, "warn")

        # Coalesce
        season = file_season or folder_season
        # episode = episode or other_episode

        if not show or not season or not episode:
            err = "ERROR: this, {0}/{1} became, {2}-s{3}_e{4}".format("/".join(folders), file, show, season, episode)
            persist_log(err, file, root)
            continue

        extension = os.path.splitext(file)[1]

        new_filename = "{0}_s{1}e{2}{3}".format(show, season, episode, extension)

        if new_filename == file:
            print("INFO: file name {0} already formatted".format(new_filename))
            continue

        shadow_filename = "{0}___{1}.original".format(new_filename, file)

        print("INFO: renamed, {0}\t{1}".format(new_filename, file))
        new_filepath = os.path.join(root, new_filename)

        # if new file exists we have a problem
        if os.path.isfile(new_filepath):
            err = "ERROR: new file exists, {0}".format(new_filename)
            persist_log(err, file, root)
            continue  # bug out before overwriting

        old_filepath = os.path.join(root, file)

        if sys.platform == 'darwin':  # locked files on my POSIX
            flags = os.stat(old_filepath).st_flags
            if flags & stat.UF_IMMUTABLE:
                os.chflags(old_filepath, flags & ~stat.UF_IMMUTABLE)

        os.rename(old_filepath, new_filepath)
        open(os.path.join(root, shadow_filename), 'a').close()

result = execute_command(umount)
