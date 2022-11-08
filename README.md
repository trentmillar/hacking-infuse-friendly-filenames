# hacking-infuse-friendly-filenames
I spent an afternoon getting my massive video library formatted for Infuse to index but found Infuse isn't so flexible with my naming convention. After many attempts at getting my entire library renamed only to find out hundreds of files still weren't recognized I decided to hack this out.
This is very ugly but saves me from manually renaming files.

## how to use
Well this is fairly specific to filenames that already have some structure. 
The all of following will get you a good name, some of the following may not
1. your file should have the episode number, E01 or x01
2. your file should have the season number, S01
3. your folders above must have the show name, Magnum PI
4. your folder(s) above should have the season number, season 1

If you have most of this then you should get a tight Infuse named video,

- magnum-pi_s01e03.mkv

The show's folder name will be what is used for these files so if you want to help Infuses' chance of finding the show try,

- add the show's originating year to the folder, Magnum PI 1980, to get,
  - magnum-pi-1980_s01e03.mkv

### how to name files
Bone up on how Infuse expects your files to look like, [Infuse - Metadata 101](https://support.firecore.com/hc/en-us/articles/215090947-Metadata-101)

### how to run the script
1. clone this repo somewhere
2. make sure Python 3.8 or greater is installed
3. `cd` to the folder where the py script is
4. run `python rename_my_files.py`

(optional) if your videos are on a NAS or SMB share somewhere 
I added some mounting logic to mount the networked folder. As it stands you will be prompted for a username & password for this share. FYI, I hard coded mine so you'll need to change this in the code.

If you have the video's locally or you already have a mapped drive using Windows then you will need to gut my mounting logic and simply hard code your path in `mount_dir`

All the pathing here is pegged to a Mac or POSIX machine so if you're running Windows you'll need to swap some code, like `/` for `\\`.

### what is the output
If your folder and file names are somewhat clean (see #how to use) you will get this,

1. your video will be renamed (inline) to include, _show_season|episode.extension_ 
2. a _.orignal_ file will be added in the same folder showing the original name if you want to revert
3. any warnings or errors for this file will also be added in the folder with the filename plus _.errors.txt_

The error log can give you some guidance as to why a name couldn't be used for your file.

### caveat emptor
This was built for my existing video file names so it is very likely it will not work out-of-the-box for you. I suggest you comment out any `os.rename` and `open(...)` in the script. Then run and look at the log output to see how close this is with your filenames.
