_ros2_build_completion() {
    local cur
    _init_completion || return

    local workspace_dir
    workspace_dir=$(pwd)
    local source_dir="$workspace_dir/src"

    local xmls
    xmls=$(find "${source_dir}" -type f -name package.xml)

    local packages=()
    for xml in $xmls; do
        local pkg_dir
        pkg_dir=$(dirname "${xml}")
        packages+=("$(basename "${pkg_dir%/}")")
    done

    COMPREPLY=($(compgen -W "${packages[*]}" -- "$cur"))
}

complete -F _ros2_build_completion b
