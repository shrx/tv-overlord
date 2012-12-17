#!/usr/bin/env bash

_getnzb()
{
	local cur all_options opts
	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"
	options='-h --help -d --db-file -l --location -n --no-cache'
	commands='download info showmissing addnew nondbshow editdbinfo'

	if [ $COMP_CWORD -eq 1 ]; then
		# select from $all_options for first choice
		COMPREPLY=( $(compgen -W "${commands}" -- $cur) )
		return 0

	elif [[ "${prev}" == "download" ]]; then
	elif [[ "${prev}" == "info" ]]; then
	elif [[ "${prev}" == "showmissing" ]]; then
	elif [[ "${prev}" == "addnew" ]]; then
	elif [[ "${prev}" == "nondbshow" ]]; then
	elif [[ "${prev}" == "editdbinfo" ]]; then
	fi
}

# add this to .bashrc:
complete -F _getnzb -o filenames getnzb

