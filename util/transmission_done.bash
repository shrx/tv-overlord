#!/usr/bin/env bash

log=~/shows/transmission-dl.log
torrentid=$TR_TORRENT_ID
torrentname=$TR_TORRENT_NAME
torrentpath=$TR_TORRENT_DIR
# shows_dir='~/net1/dl/TV Shows/'
shows_dir='/Volumes/Volume_1/dl/TV Shows/'

#  TR_APP_VERSION
#  TR_TIME_LOCALTIME
#x TR_TORRENT_DIR
#  TR_TORRENT_HASH
#x TR_TORRENT_ID
#x TR_TORRENT_NAME

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
    elif type terminal-notifier; then
        terminal-notifier -title 'Video Mover' -message "$1";
	fi
}

echo ' ' >> $log
echo $(date) '==============' >> $log

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
    if mkdir "$full_dest"; then
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
