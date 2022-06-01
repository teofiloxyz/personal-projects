#!/bin/bash
# Manager de arquivos: comprime, descomprime e adiciona ao arquivo, de forma rápida, simples e organizada
# Este script é mais antigo que o script em Python, e não tem tantas funcionalidades

COMMAND=$1
INPUT=$2
INPUT2=$3

error() {
    echo "Error: $1" &
    exit 1
}

main() {
    cmd
    action
}

cmd() {
	[ -z "$COMMAND" ] \
		&& read -p '[1] Extract | [2] Compress | [3] Add-to-archive | [other] Cancel: ' COMMAND
    readonly COMMAND
}

input() {
	[ -z "$INPUT" ] \
		&& { ls -lA; \
		read -p "$1 " input; }
    readonly INPUT
}

input2() {
	[ -z "$INPUT2" ] \
		&& { ls -lA; \
		read -p "$1 " input2; }
    readonly INPUT2
}

extract() {
    local input file_name extract_dir
	
    get_input() {
        if [ -z "$1" ]; then
            input 'Enter input to be extracted:'
            input="$INPUT"
        else
            input="$1"
        fi
    }

    get_extract_dir_name() {
        file_name=$(basename -- "$input" \
		    | cut -f 1 -d '.')
	    extract_dir="Extracted_$file_name"
    }

    check_extract_dir_name() {
		[ -d "$extract_dir" ] \
			&& error "Directory '$extract_dir' already exists."
    }

    make_extract_dir() {
		mkdir "$extract_dir"
    }
    
    move_to_extract_dir() {
		mv "$input" "$extract_dir"/
		cd "$extract_dir"/

        [[ "$input" == *"/"* ]] \
            && input=$(basename "$input")
    }

    extract_method() {
        case $input in
            *.tar.xz) tar xvf $input;;
          	*.tar.gz) tar xvzf $input;;
            *.tar.bz2)tar xvjf $input;;
       	    *.tar) tar xvf $input;;
		        *.xz) xz -dv $input;;
            *.gz) gunzip $input;;
          	*.bz2) bunzip2 $input;;
          	*.rar) unrar x $input;;
          	*.tbz2) tar xvjf $input;;
          	*.tgz) tar xvzf $input;;
          	*.zip) unzip $input;;
          	*.Z) uncompress $input;;
          	*.7z) 7z x $input;;
           	*) error "Don't know how to extract '$input'";;
        esac
	}
	
    move_out_extract_dir() {
		[ -f "$input" ] \
			&& mv "$input" .. \
		        && cd ..
    }

    echo_extract_dir_name_for_var() {
        [[ $COMMAND == 'add' ]] \
            || [[ $COMMAND == '3' ]] \
                && echo "$extract_dir"
    }

    ranger_extracted() {
        local ans
        [[ $COMMAND == 'extract' ]] \
            || [[ $COMMAND == '1' ]] \
                && read -p "Do you want to open ranger on the extraction folder? (Y/n): " ans \
                    && [ -z "$ans" ] \
                        || [ "$ans" == "y" ] \
                            && ranger "$extract_dir" 
    }

    get_input "$1"
    get_extract_dir_name
    check_extract_dir_name
    make_extract_dir
    move_to_extract_dir
    extract_method
    move_out_extract_dir
    echo_extract_dir_name_for_var
    ranger_extracted
} 

compress() {
	local input output_name
	
    get_input() {
        if [ -z "$1" ]; then
            input 'Enter input to be compressed (<all> for all files in current directory):'
            input="$INPUT"
        else
            input="$1"
        fi
    }

    name_output() {
        if [[ $COMMAND == 'add' ]] \
            || [[ $COMMAND == '3' ]]; then
            output_name=$(basename -- "$1" \
                | cut -f 1 -d '.')
        else
            read -p 'Name the output without extension (none for same as input): ' output_name

		    [ "$output_name" == "" ] \
			    && output_name=$(basename -- "$input" \
				    | cut -f 1 -d '.')
        fi
	}

	method_file() {
		local method encrypt
		read -p 'Choose compressing method: [1] xz(max) | [2] xz(med) | [3] gz | [4] 7zip: ' method
	    
        [ $method -eq 4 ] \
            && read -p 'Want encryption? Please do! (Y/n): ' encrypt
        
		case "$method" in
			1) xz -9kT0 "$input" --stdout > "$output_name".xz ;;
			2) xz -6kT0 "$input" --stdout > "$output_name".xz ;;
			3) gzip -k "$input" --stdout > "$output_name".gz ;;
      4) if [ "$encrypt" == "y" ] || [[ -z "$encrypt" ]]; then
             7z a "$output_name".7z -mhe=on "$input" -p
         elif [ "$encrypt" == "n" ]; then
             7z a "$output_name".7z "$input" 
         else
             error 'Must be y or n'
         fi;;
			*) error 'Invalid choice!';;
		esac
	}
	
	method_folder() {
		local method encrypt
		
        if [[ $COMMAND == 'add' ]] \
            || [[ $COMMAND == '3' ]]; then
            method="$1"        
        else
            read -p 'Choose compressing method: [1] tar.xz(max) | [2] tar.xz(med) | [3] tar.gz | [4] 7zip | [5] tar: ' method
        fi

        [ $method -eq 4 ] \
            && read -p 'Want encryption? (Y/n): ' encrypt

		case "$method" in
			1) tar cvf "$output_name".tar.xz --use-compress-program='xz -9T0' $input ;;
			2) tar cvf "$output_name".tar.xz --use-compress-program='xz -6T0' $input ;; 
			3) tar cvzf "$output_name".tar.gz $input ;;
			4) if [ "$encrypt" == "y" ] || [[ -z "$encrypt" ]]; then
             7z a "$output_name".7z -mhe=on "$input" -p
         elif [ "$encrypt" == "n" ]; then
             7z a "$output_name".7z "$input"
         else
             error 'Must be y or n'
         fi;;
			5) tar cvf "$output_name".tar $input ;;
			*) error 'Invalid choice!';;
		esac
	}
	
	input_type() {
		if [ -d "$input" ] \
            || [ "$input" == "all" ]; then
			    [ "$input" == "all" ] \
				    && input="."
			    method_folder "$1"
		else
			method_file
		fi
	}

    get_input "$1"
	name_output "$2"
	input_type "$3"
}

add_to_archive() {
    local input input2 input2_format extract_dir input_dst

    get_input() {
        input 'Enter input file/directory to be added:'
        input="$INPUT"
    }

    get_input2() {
        input2 'Enter input archive to add the file:'
        input2="$INPUT2"
    }

    check_input() {
        [ -d "$input" ] \
            || [ -f "$input" ] \
                || error "Input must be an existing file or directory" 
    }

    check_input2_format() {
        case $input2 in
            *.xz | *.tar.xz) input2_format='1';;
            *.gz | *.tar.gz) input2_format='3';;
            *.7z) input2_format='4';;
            *.tar) input2_format='5';;
            *) error "'$input2' format not supported";;
        esac
    }

    extract_input2() {
        extract_dir=$(extract "$input2" | tail -n1 \
            || error "Failed to extract $input2, is it an archive?")
    }
    
    change_input2_name() {
        mv "$input2" "$input2".old
    }

    copy_input() {
        cp -vi "$input" "$extract_dir"/ \
            || error "Couldn't copy input"
    }

    compress_output() {
        cd "$extract_dir"/ \
            && compress 'all' "$input2" "$input2_format" 
    }

    move_output() {
        mv "$input2" .. \
            && cd ..
    }

    get_input
    get_input2
    check_input
    check_input2_format
    extract_input2
    change_input2_name
    copy_input
    compress_output
    move_output
}

action() {
	case "$COMMAND" in
		1 | "extract") extract;;
		2 | "compress") compress;; 
		3 | "add") add_to_archive;; 
		*) echo 'Invalid choice!';;
	esac
}

main
