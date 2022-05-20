#!/bin/bash
# Redshift gradual que deve ser corrido a cada minuto (e.g.: systemd)
# Baseado na seguinte função afim: y = -11x + 8000;
# Onde x é o tempo decorrido após a hora inicial;
# E y é o valor a atribuir ao redshift

readonly REDSHIFT_MAX=8000
readonly REDSHIFT_MIN=1400
readonly TIME_START_DECREASE=12
readonly TIME_STOP_DECREASE=22
readonly TIME_LIGHT_RESET=6
readonly CURRENT_HOUR=$(date +"%H")

main() {
    if [[ $CURRENT_HOUR -ge $TIME_LIGHT_RESET ]] \
        && [[ $CURRENT_HOUR -lt $TIME_START_DECREASE ]]; then
            refresh_redshift $REDSHIFT_MAX
            return 0
    elif [[ $CURRENT_HOUR -ge $TIME_STOP_DECREASE ]] \
        || [[ $CURRENT_HOUR -lt $TIME_LIGHT_RESET ]]; then
            refresh_redshift $REDSHIFT_MIN 
            return 0
    fi

    redshift_dinamic
    return 0
}

refresh_redshift() {
    redshift -P -O "$1"
}

redshift_dinamic() {
    local current_time mins_from_start redshift_value

    get_mins_diff() {
        echo $((($(date --date="$1" +%s) - $(date --date="$2" +%s)) / 60))
    }
    
    get_redshift_value() {
        echo $((-11 * $1 + $REDSHIFT_MAX))
    }
    
    current_time=$(date +"%H:%M")
    mins_from_start=$(get_mins_diff "$current_time" "$TIME_START_DECREASE")
    redshift_value=$(get_redshift_value $mins_from_start)
    refresh_redshift $redshift_value
}

main
