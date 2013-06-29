#!/usr/bin/env bash

log=/home/sm/shows/deluge-dl.log
torrentid=$1
torrentname=$2
torrentpath=$3
shows_dir='/home/sm/net1/dl/TV Shows/'

echo $(date) '==============' >> $log

echo $torrentid >> $log
echo $torrentname >> $log
echo $torrentpath >> $log


dest=$(echo $torrentname |
    sed 's/\.\([[:digit:]]x[[:digit:]]\{2\}\|S[[:digit:]]\{2\}E[[:digit:]]\{2\}\).*//'|
    sed 's/\./_/g')

full_dest=$shows_dir$dest

echo "Destination dir: $full_dest" >> $log

if [ ! -d "$full_dest" ]; then

    if zenity --question --text="$full_dest does not exist.\nCreate new dir?"; then
        mkdir "$full_dest";
        echo "Creating dir: $dest" >> $log
    else
        echo "dir NOT created" >> $log
    fi
fi

if [ -d "$full_dest" ]; then
    cp -v "$torrentpath/$torrentname" "$full_dest"
fi
