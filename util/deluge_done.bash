#!/usr/bin/env bash

log=/home/sm/shows/deluge-dl.log
torrentid=$1
torrentname=$2
torrentpath=$3
shows_dir='/home/sm/net1/dl/TV Shows/'

function msg
{
	if notify-send --help &> /dev/null; then
		icon1='/usr/share/icons/Faenza/places/scalable/folder-videos.svg'
		icon2='/usr/share/icons/gnome-wine/scalable/places/folder-videos.svg'
		if [ -e icon1 ]; then
			icon=$icon1
		elif [ -e icon2 ]; then
			icon=$icon2
		fi
		# notify-send --hint=int:transient:1 --icon=$icon 'Video Mover' "$1"
		notify-send --icon=$icon 'Video Mover' "$1"
	elif kdialog --help &> /dev/null; then
		kdialog --title 'Video Mover' --passivepopup "$1" 10;
	fi
}

echo '\n' $(date) '==============' >> $log

echo "torrentid:   $torrentid" >> $log
echo "torrentname: $torrentname" >> $log
echo "torrentpath: $torrentpath" >> $log


dest=$(echo $torrentname |
    # 1x11.* or S11E11.*
    sed 's/[. ]\([[:digit:]]x[[:digit:]]\{2\}\|S[[:digit:]]\{2\}E[[:digit:]]\{2\}\).*//'|
    sed 's/[. ]/_/g')

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
    if cp -r "$torrentpath/$torrentname" "$full_dest"; then
        msg "Show copied: $torrentname\nTo: $full_dest"
    else
        msg "ERROR copying $torrentname\nTo: $full_dest"
        echo "ERROR copying $torrentname To: $full_dest" >> $log
    fi
fi
