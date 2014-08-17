#!/usr/bin/env bash

# the easiest way to use this, is to source this in your .bashrc:
# source <path to tv-completion dir>/tv-completion.bash
# eg:
# source ~/projects/tv-downloader/src/util/tv-completion.bash
#
# or you can install this in you system's bash completion dir,
# which varies depending on your system

_tv()
{
	local cur prev all_options opts commands
	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"

    # COMMANDS: ------------------------

	if [ $COMP_CWORD -eq 1 ]; then
	    commands='download showmissing info calendar addnew nondbshow editdbinfo providers'
		COMPREPLY=( $(compgen -W "${commands}" -- $cur) )
		return 0

    # OPTIONS: -------------------------

    # download
	elif [[ "${prev}" == "download" ]]; then
        opts="-n --no-cache -c --count -l --location -p --search-provider"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # showmissing
	elif [[ "${prev}" == "showmissing" ]]; then
        opts="-n --no-cache"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # info
	elif [[ "${prev}" == "info" ]]; then
        opts="-n --no-cache -a --show-all -x --sort-by-next --ask-inactive --show-links --synopsis"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # calendar
	elif [[ "${prev}" == "calendar" ]]; then
        opts="-n --no-cache -a --show-all -x --sort-by-next --no-color --days"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # nondbshow
	elif [[ "${prev}" == "nondbshow" ]]; then
        opts="-n --no-cache -c --count -l --location -p --search-provider"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
	fi
}
complete -F _tv tv
