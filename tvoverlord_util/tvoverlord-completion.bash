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
	    commands='download showmissing info calendar addnew nondbshow editdbinfo providers history'
		COMPREPLY=( $(compgen -W "${commands}" -- $cur) )
		return 0

    # OPTIONS: -------------------------

    # download
	elif [[ "${prev}" == "download" ]]; then
        opts="--no-cache --today --ignore-warning --count --location --search-provider"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # showmissing
	elif [[ "${prev}" == "showmissing" ]]; then
        opts="--no-cache --today"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # info
	elif [[ "${prev}" == "info" ]]; then
        opts="--no-cache --show-all --sort-by-next --ask-inactive --show-links --synopsis"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # calendar
	elif [[ "${prev}" == "calendar" ]]; then
        opts="--no-cache --show-all --sort-by-next --no-color --days"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # addnew
    # nondbshow
	elif [[ "${prev}" == "nondbshow" ]]; then
        opts="--count --location --search-provider"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    # editdbinfo
    # providers
    # history
	elif [[ "${prev}" == "history" ]]; then
        opts="list copy redownload"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
    elif [[ "${prev}" == "list" ]]; then
        opts="--what-to-show"
		COMPREPLY=( $(compgen -W "${opts}" -- $cur) )
        return 0
	fi
}
complete -F _tv tvol
