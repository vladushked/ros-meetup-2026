_ros2_launch_completion() {
    local cur words cword
    _init_completion || return

    local workspace_dir
    workspace_dir=$(pwd)
    local install_dir="$workspace_dir/install"

    local has_v_flag=0
    for word in "${words[@]:1}"; do
        if [[ $word == "-v" ]]; then
            has_v_flag=1
            break
        fi
    done

    local package_pos=$((1 + has_v_flag))
    local launch_file_pos=$((2 + has_v_flag))

    if [[ $cword -eq 1 ]]; then
        local packages=()
        for pkg in "$install_dir"/*/share/ament_index/resource_index/packages/*; do
            [ -e "$pkg" ] || continue
            packages+=("$(basename "${pkg%/}")")
        done
        COMPREPLY=($(compgen -W "-v ${packages[*]}" -- "$cur"))
    elif [[ $has_v_flag -eq 1 && $cword -eq 2 ]]; then
        local packages=()
        for pkg in "$install_dir"/*/share/ament_index/resource_index/packages/*; do
            [ -e "$pkg" ] || continue
            packages+=("$(basename "${pkg%/}")")
        done
        COMPREPLY=($(compgen -W "${packages[*]}" -- "$cur"))
    elif [[ $cword -eq $launch_file_pos ]]; then
        local package_name="${words[$package_pos]}"
        local launch_dir="$workspace_dir/install/$package_name/share/$package_name/launch"
        if [[ -d "$launch_dir" ]]; then
            local launch_files=()
            for file in "$launch_dir"/*.launch.py; do
                [ -f "$file" ] || continue
                launch_files+=("$(basename "$file" .launch.py)")
            done
            COMPREPLY=($(compgen -W "${launch_files[*]}" -- "$cur"))
        fi
    fi
}

complete -F _ros2_launch_completion r
