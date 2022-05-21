#!/bin/bash
# Mount and dismount storage devices

COMMAND=$1

error() {
    echo "Error: $1" &
    exit 1
}

main() {
    cmd_check
    action
}

cmd_check() {
    get_cmd() {
        [ -z "$COMMAND" ] \
            && read -p 'Pick what to do? [1] Mount | [2] Dismount | [other] Cancel: ' COMMAND
    } 

    validate_cmd() {
        readonly COMMAND=$COMMAND

        local valid_cmd=(1 2 'mount' 'dismount')
        [[ " ${valid_cmd[*]} " =~ " ${COMMAND} " ]] \
            || error "Choose only 'mount' or 'dismount'"
    } 

    get_cmd
    validate_cmd
}

action() {
    case "$COMMAND" in
        1 | "mount") mounting_process;; 
        2 | "dismount") dismounting_process;;
    esac
}

mounting_process() {
    local unmounted_devs target_dev dev_mem mnt_point 

    ranger_mnt() {
        local ans
        read -p ":: Do you want to open ranger on the mounting point? [Y/n] " ans \
            && [ -z "$ans" ] \
                || [ "$ans" == "y" ] \
                    && ranger "$1"
    }

    dev_mount() {
        sudo mount "$1" "$2" -o uid=$USER -o gid=users \
            || error "Mounting"
    }
   
    check_unmounted() {
        local all_devs mounted_devs

        lsblk -I 8 > /dev/null 2>&1 \
            || error "No storage devices found to mount"

        all_devs=$(lsblk -I 8 | awk '{print $1}' | cut -c 7-) 
        mounted_devs=$(lsblk -I 8 | awk '/mnt/ {print $1}' | cut -c 7-)
        unmounted_devs=()

        for i in $all_devs; do
            [[ "${mounted_devs[*]}" =~ "$i" ]] \
                || unmounted_devs+=("$i")
        done
        
        [ -z "$unmounted_devs" ] \
            && error "It seems there are no devices/partitions to mount"
    }
    
    choose_target() {
        if [[ ${#unmounted_devs[@]} -eq 1 ]]; then
            target_dev=$unmounted_devs
        else
            echo "Found the following unmounted devices/partitions:"
            
            n=1
            for i in ${unmounted_devs[@]}; do
                echo "[$n] $i"
                let "n+=1"
            done
            
            read -p "Choose the one you want to mount: " ans
            
            until [[ $ans =~ ^-?[0-9]+$ ]] \
                && [[ $ans -ge 1 && $ans -le ${#unmounted_devs[@]} ]]; do
                read -p "Invalid answer, choose the number: " ans
            done
            
            ans=$(($ans - 1)) \
                && target_dev=${unmounted_devs[$ans]}
        fi  
            
        dev_mem=$(lsblk -I 8 | grep "$target_dev" | awk '{print $4}')
    }

    get_mount_dir() {
        [ ! -d "/mnt/$target_dev" ] \
            && sudo mkdir "/mnt/$target_dev"
        mnt_point="/mnt/$target_dev/"
    }

    mount_target() {
        echo "Mounting $target_dev (size: $dev_mem) in $mnt_point"
        dev_mount "/dev/$target_dev" "$mnt_point" \
            && echo "Mounted!" \
                && ranger_mnt "$mnt_point" 
    }

    check_unmounted
    choose_target 
    get_mount_dir
    mount_target
} 

dismounting_process() {
    local mounted_devs target_dev 

    dev_dismount() {
        sudo umount -f "$1" \
            || error "Dismounting"
    }
    
    check_mounted() {
        mounted_devs=()
        for i in $(lsblk -I 8 | awk '/mnt/ {print $1}' | cut -c 7-); do
            mounted_devs+=("$i")
        done

        if [ -z "$mounted_devs" ]; then
            for mdir in /mnt/*/; do
                if mountpoint "$mdir" > /dev/null 2>&1; then
                    mounted_devs+=("$mdir")
                fi
            done
        fi

        [ -z "$mounted_devs" ] \
            && error "It seems there are no devices/partitions to dismount"
    }
    
    choose_target() {
        if [[ ${#mounted_devs[@]} -eq 1 ]]; then
            target_dev=$mounted_devs
        else
            echo "Found the following mounted devices/partitions:"
            n=1
            for i in ${mounted_devs[@]}; do
                 echo "[$n] $i"
                 let "n+=1"
             done

             local ans
             read -p "Choose the one you want to dismount: " ans

             until [[ $ans =~ ^-?[0-9]+$ ]] \
                 && [[ $ans -ge 1 && $ans -le ${#mounted_devs[@]} ]]; do
                    read -p "Invalid answer, choose the number: " ans
             done

             ans=$(($ans - 1)) \
                 && target_dev=${mounted_devs[$ans]}
        fi
    }

    dismount_target() {
        echo "Dismounting $target_dev"
        dev_dismount "/dev/$target_dev" \
            && (paplay "$DMNT" & \
                echo "Dismounted!")
    }

    remove_empty_dirs() {
        for d in /mnt/*/; do
            mountpoint "$d" > /dev/null 2>&1 \
                || sudo rmdir "$d" 
        done
    }

    check_mounted
    choose_target
    dismount_target
    remove_empty_dirs
} 

main
