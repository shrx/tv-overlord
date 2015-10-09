#!/usr/bin/env bash

debug=false
if [[ $1 == 'debug' ]]; then
    debug=true
fi
logf=~/shows/transmission-dl.log
torrentid=$TR_TORRENT_ID
torrentname=$TR_TORRENT_NAME
torrentpath=$TR_TORRENT_DIR
if [ "$OSTYPE" == 'linux-gnu' ]; then
    shows_dir='/home/sm/net1/dl/TV Shows/'
elif [ "$OSTYPE" == 'darwin' ]; then
    shows_dir='/Volumes/Volume_1/dl/TV Shows/'
fi

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
		# notify-send --hint=int:transient:1 --icon=$icon 'Video Mover' "$3"
		notify-send --icon=$icon 'Video Mover' "$3"
	elif kdialog --help &> /dev/null; then
		kdialog --title 'Video Mover' --passivepopup "$3" 10;
    elif type terminal-notifier; then
        terminal-notifier -title "$1" -subtitle "$2" -message "$3";
	fi
}
function log
{
    if [[ $debug = true ]]; then
        echo $*
    else
        echo $* >> $logf
    fi
}

log ' '
log $(date) '=============='

log "torrentid:	  $torrentid"
log "torrentname: $torrentname"
log "torrentpath: $torrentpath"
log "Debugging command:"
# add a test command to try and debug any
# weird names that don't get parsed correctly:
log "\
export TR_TORRENT_ID='$torrentid'; \
export TR_TORRENT_NAME='$torrentname'; \
export TR_TORRENT_DIR='$torrentpath'; \
./transmission_done.bash debug"

dest=$(echo $torrentname |
# 1. first remove any extraneous strings that don't fit the pattern
#    from the torrent name before parsing.  There could end up being
#    several more here.

    sed 's/\[ www\.torrenting\.com \] - //' |

# 2. Now parse torrent name to get the name of the show.

    # search for this pattern: 1x11.* or S11E11.*
    # remove from episode and season to the end of string
    sed 's/[. ]*\([[:digit:]]x[[:digit:]]\{2\}\|S[[:digit:]]\{2\}E[[:digit:]]\{2\}\).*//' |
    # remove any spaces at start or end of string
    sed 's/^[[:space:]]\|[[:space:]]$//g' |
    # convert dots or spaces to underscores
    sed 's/[. _]\+/_/g')

full_dest=$shows_dir$dest

log "Destination dir: $full_dest"

if [[ $debug == true ]]; then exit; fi

if [ ! -d "$full_dest" ]; then
    if mkdir "$full_dest"; then
        log "Creating dir: $dest"
    else
        log "dir NOT created"
    fi
fi

if [ -d "$full_dest" ]; then
    if cp -r "$torrentpath/$torrentname" "$full_dest"; then
        msg "$dest" "$torrentname" "$full_dest"
    else
        msg "$dest" "$torrentname" "ERROR copying $torrentname
To: $full_dest"
        log "ERROR copying $torrentname To: $full_dest"
    fi
fi
