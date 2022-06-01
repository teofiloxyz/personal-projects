// Rofi-hkey (ou Rofi-hotkey) é a integração do hkey no rofi.
// Atua como launcher, através da execução de comandos na shell.
// Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
// específica deste programa.

// Variáveis e funções estão em 'snake_case'
// Há muito para melhorar aqui

package main

import (
     "os"
     "os/exec"
     "log"
     "time"
     "fmt"
     "strings"
     "strconv"
     "io/ioutil"
     "encoding/json"
     "gopkg.in/ini.v1"
     "sort"
)

var hkeys_path string 
var history_path string 
var rofi_list_path string
var python_hist_file string 
var hkeys map[string][]string
var rkeys map[int][]string

func main() {
    get_info_from_config()
    go get_hkeys_from_json()
    // Fiz assim apenas para ficar nesta ordem específica quando é mostrado o 'help dialog'
    // Talvez haja uma forma mais simples
    rkeys = map[int][]string{0: {"ls", "Search for hkeys"},
                             1: {"ad", "Add entry to hotkeys list"},
                             2: {"rm", "Remove entry from hotkeys list"},
                             3: {"ed", "Edit entry from hotkeys list"},
                             4: {"hs", "Open to history menu"},
                             5: {"h", "Show help dialog"},
                             6: {"q", "Quit"}}
    var menu_message string

    hkeyloop:for {
        user_input := rofi_simple_prompt("Enter Hkey", menu_message)

        // Search/filter mode das hkeys, com dropdown menu
        if user_input == "ls" {
            user_input = rofi_dmenu_hkeys("Search Hkey", "")
            menu_message = ""
        }

        full_user_input := user_input

        // Caso tenha input (e.g.: s <search entry>)
        var command_input string
        var needs_input bool
        if strings.Contains(user_input, " ") {
            user_input = strings.SplitAfter(full_user_input, " ")[0]
            command_input = strings.TrimPrefix(full_user_input, user_input)

            // Ver se o input não é nulo
            if strings.ReplaceAll(command_input, " ", "") == "" {
                needs_input = true
            }
        }

        // Reconhecimento e launch da hkey
        for hkey := range hkeys {
            if hkey == user_input {

                if needs_input {
                    command_input = rofi_simple_prompt(hkeys[hkey][1], menu_message)
                    if command_input == "" || command_input == "q" {
                        menu_message = ""
                        continue hkeyloop
                    }
                }

                command := hkeys[hkey][0] + " " + command_input

                go history_append(full_user_input)

                launch_hkey(command)
                os.Exit(0)
            }
        }
        
        // Rkeys e respetivas funções
        switch(user_input) {
        case "ad":
            menu_message = add_hkey()
        case "rm":
            menu_message = remove_hkey()
        case "ed":
            menu_message = edit_hkey()
        case "hs":
            history_menu()
        case "h":
            show_help_dialog()
            menu_message = ""
        case "q":
            os.Exit(0)
        default:
            menu_message = " -mesg \"Invalid key... \nEnter 'h' for help\""
            continue hkeyloop
        }

    }
}

func get_info_from_config() {
    config_path := "config.ini"
    config, err := ini.Load(config_path)
     if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    hkeys_path = config.Section("GENERAL").Key("hkeys_path").String()
    history_path = config.Section("GENERAL").Key("history_path").String()
    rofi_list_path = config.Section("GENERAL").Key("rofi_list_path").String()
    python_hist_file = config.Section("TMP").Key("python_hist_file").String()
}

func get_hkeys_from_json() {
    hkeys_json, err := os.Open(hkeys_path)
    if err != nil {
        fmt.Println("No hkeys.json file found...\nCreating one...")
        fmt.Println()
        go update_hkeys_json()
    }
    defer hkeys_json.Close()

    hkeys_content, _ := ioutil.ReadAll(hkeys_json)

    json.Unmarshal(hkeys_content, &hkeys)
}

func launch_hkey(command string) {
    // Melhorar a forma como o processo começa
    command = "setsid " + strings.TrimSpace(command)

    command_array := strings.Fields(command)
    cmd := exec.Command(command_array[0], command_array[1:]...)

    // Aqui tenho que dar um delay para o programa não fechar antes do comando ser executado
    // É estranho...
    err := cmd.Start()
    time.Sleep(time.Second / 10)
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
}

func history_append(full_user_input string) {
    // Melhorar esta func

    // Se não existir history.csv, escreve o header do csv
    var header string
    _, err := os.Stat(history_path)
    if err != nil {
        header = "date,entry\n"
    }

    hs, err := os.OpenFile(history_path, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0600)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer hs.Close()

    _, err = hs.WriteString(header)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    full_user_input = strings.ReplaceAll(full_user_input, ",", "")
    now := time.Now().Format("2006-01-02 15:04:05")
    entry := now + "," + full_user_input + "\n"
    _, err = hs.WriteString(entry)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

func history_menu() {
    // Isto inicia o script de python hkey no history menu
    // Futuramente o programa deixará de depender de Python para analisar o histórico
    launch_hkey("alacritty -e python " + python_hist_file + " history_menu")
    os.Exit(0)
}

func show_help_dialog() {
    message := "General options: \n"

    for i := 0; i < len(rkeys); i++ {
        rkey := rkeys[i][0]
        description := rkeys[i][1]
        message += "'" + rkey + "': " + description
        if i < len(rkeys) - 1 {
            message += "\n"
        }
    }

    rofi_message(message)
}

func rofi_simple_prompt(prompt string, message string) string {
    cmd := "rofi -dmenu -p '" + prompt + "' -l 0 -theme-str 'entry { placeholder: \"\"; } inputbar { children: [prompt, textbox-prompt-colon, entry]; } listview { border: 0; }'" + message
    output, err := exec.Command("bash", "-c", cmd).Output()
    if err != nil {
        log.Fatal(err)
    }

    return strings.TrimSuffix(string(output), "\n")
}

func rofi_dmenu_hkeys(prompt string, message string) string {
    cmd := "rofi -dmenu -i -input " + rofi_list_path + " -p '" + prompt + "' -theme-str 'entry { placeholder: \"\"; } inputbar { children: [prompt, textbox-prompt-colon, entry]; }'" + message
    output, err := exec.Command("bash", "-c", cmd).Output()
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }

    hkey := strings.Split(string(output), ":")[0]
    return strings.Trim(hkey, "'")
}

func rofi_custom_dmenu(prompt string, message string, dmenu []string) string {
    var dmenu_input string
    for i, entry := range dmenu {
        dmenu_input += entry
        if i < len(dmenu) - 1 {
            dmenu_input += "|"
        }
    }
    
    var dmenu_lines string
    if len(dmenu) < 15 {
        dmenu_lines = strconv.Itoa(len(dmenu))
    } else {
        dmenu_lines = "15"
    }

    cmd := "echo '" + dmenu_input + "' | rofi -sep '|' -dmenu -i -p '" + prompt + "' -l " + dmenu_lines + " -theme-str 'entry { placeholder: \"\"; } inputbar { children: [prompt, textbox-prompt-colon, entry]; }'" + message
    output, err := exec.Command("bash", "-c", cmd).Output()
    if err != nil {
        log.Fatal(err)
    }

    return strings.TrimSuffix(string(output), "\n")
}

func rofi_message(message string) {
    cmd := exec.Command("rofi", "-e", message)
    err := cmd.Run()
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
}

func add_hkey() string {
    new_hkey := name_hkey("")
    if new_hkey == "q" {
        return " -mesg \"Aborted...\""
    }

    new_command := get_command("")
    if new_command == "q" {
        return " -mesg \"Aborted...\""
    }

    new_description := get_description("")
    if new_description == "q" {
        return " -mesg \"Aborted...\""
    }

    if !confirmation("Add", new_hkey, new_command, new_description) {
        return " -mesg \"Aborted...\""
    }

    hkeys[new_hkey] = []string{new_command, new_description}
    go update_hkeys_json()
    go update_rofi_list()
    return " -mesg \"'" + new_hkey + "' Added!\""
}

func remove_hkey() string {
    hkey := hkey_search("Search Hkey to Remove")
    if hkey == "q" {
        return " -mesg \"Aborted...\""
    }

    command := hkeys[hkey][0]
    description := hkeys[hkey][1]

    if !confirmation("Remove", hkey, command, description) {
        return " -mesg \"Aborted...\""
    }

    delete(hkeys, hkey)
    go update_hkeys_json()
    go update_rofi_list()

    return " -mesg \"'" + hkey + "' Removed!\""
}

func edit_hkey() string {
    hkey := hkey_search("Search Hkey to Edit")
    if hkey == "q" {
        return " -mesg \"Aborted...\""
    }

    command := hkeys[hkey][0]
    description := hkeys[hkey][1]

    menu_message := ""
    for {
        prompt := "Edit what?"
        dmenu_opts := []string {"Hkey: " + hkey, "Command: " + command, "Description: " + description, "Quit"}

        section := rofi_custom_dmenu(prompt, menu_message, dmenu_opts)
        if strings.Contains(section, ":") {
            section = strings.Split(section, ":")[0]
        }

        // Optimizar isto... (talvez com uma nested func)
        switch(section) {
        case "Hkey":
            menu_message_prefix := "Current Hkey: " + hkey + "\n"
            new_hkey := name_hkey(menu_message_prefix)
            if new_hkey == "q" {
                return " -mesg \"Aborted...\""
            } else if new_hkey == hkey {
                menu_message = " -mesg \"Nothing has been changed...\""
                continue
            }

            delete(hkeys, hkey)
            hkeys[new_hkey] = []string{command, description}
            go update_hkeys_json()
            go update_rofi_list()

            menu_message = " -mesg \"Hkey changed from '" + hkey + "' to '" + new_hkey + "'\""
            hkey = new_hkey
        case "Command":
            menu_message_prefix := "Current Command: " + command
            new_command := get_command(menu_message_prefix)
            if new_command == "q" {
                return " -mesg \"Aborted...\""
            } else if new_command == command {
                menu_message = " -mesg \"Nothing has been changed...\""
                continue
            }

            hkeys[hkey] = []string{new_command, description}
            go update_hkeys_json()
            go update_rofi_list()

            menu_message = " -mesg \"Command changed from '" + command + "' to '" + new_command + "'\""
            command = new_command
        case "Description":
            menu_message_prefix := "Current Description: " + description
            new_description := get_description(menu_message_prefix)
            if new_description == "q" {
                return " -mesg \"Aborted...\""
            } else if new_description == description {
                menu_message = " -mesg \"Nothing has been changed...\""
                continue
            }

            hkeys[hkey] = []string{command, new_description}
            go update_hkeys_json()
            go update_rofi_list()

            menu_message = " -mesg \"Description changed from '" + description + "' to '" + new_description + "'\""
            description = new_description
        case "Quit\n": // Bug (a func do menu já retira \n)
            return " -mesg \"Exited edition mode\""
        }
    }
}

func hkey_search(prompt string) string {
    menu_message := ""
    hkey_search_loop:for {
        user_input := rofi_dmenu_hkeys(prompt, menu_message)

        if user_input == "q" {
            return "q"
        }

        for i := range rkeys {
            rkey := rkeys[i][0]
            if user_input == rkey {
                description := rkeys[i][1]
                menu_message = " -mesg \"'" + rkey + "' is a reserved key used to: " + description + "\""
                continue hkey_search_loop
            }
        }

        return user_input
    }
}

func name_hkey(menu_message_prefix string) string {
    menu_message := " -mesg \"" + menu_message_prefix + "[If you'll run the command with an input (e.g.: google 'input') make sure the hkey has a space at the end, otherwise don't leave a space]\""

    name_hkey_loop:for {
        new_hkey := rofi_simple_prompt("Enter the New Hkey", menu_message)

        if new_hkey == "q" || new_hkey == "" {
            return "q"
        }  

        for hkey := range hkeys {
            if new_hkey == hkey {
                command := hkeys[new_hkey][0]
                menu_message = " -mesg \"'" + new_hkey + "' already exists for the following command: '" + command + "'\""
                continue name_hkey_loop
            }
        }

        for i := range rkeys {
            rkey := rkeys[i][0]
            if new_hkey == rkey {
                description := rkeys[i][1]
                menu_message = " -mesg \"'" + rkey + "' is a reserved key used to: " + description + "\""
                continue name_hkey_loop
            }
        }

        return new_hkey
    }
}

func get_command(menu_message_prefix string) string {
    var menu_message string
    if menu_message_prefix != "" {
        menu_message = " -mesg \"" + menu_message_prefix + "\""
    } else {
        menu_message = ""
    }
    new_command := rofi_simple_prompt("Enter the full command to link to the Hkey", menu_message)

    if new_command == "q" || new_command == "" {
        return "q"
    }

    return new_command
}

func get_description(menu_message_prefix string) string {
    var menu_message string
    if menu_message_prefix != "" {
        menu_message = " -mesg \"" + menu_message_prefix + "\""
    } else {
        menu_message = ""
    }
    for {
        new_description := rofi_simple_prompt("Enter a description of the command", menu_message)

        if new_description == "q" || new_description == "" {
            return "q"
        } else if len(new_description) > 60 {
            menu_message = " -mesg \"Description is too long...\""
            continue
        }

        new_description_array := strings.Split(strings.TrimSpace(new_description), " ")
        new_description = ""
        // Faço desta forma pq podem haver siglas (com todas as letras maiúsculas)
        // Melhorar isto
        for i, word := range new_description_array {
            word = strings.ToUpper(word[:1]) + word[1:]
            new_description += word
            if i < len(new_description_array) - 1 {
                new_description += " "
            }
        }

        return strings.TrimSuffix(new_description, " ")
    }
}

func confirmation(mode string, hkey string, command string, description string) bool{
    prompt := mode + " this entry?"
    menu_message := " -mesg \"Hkey: " + hkey + "\nCommand: " + command + "\nDescription: " + description + "\""
    dmenu_opts := []string {"Yes", "No"}

    confirmation := rofi_custom_dmenu(prompt, menu_message, dmenu_opts)
    if confirmation == "Yes" {
        return true
    } else {
        return false
    }
}

func update_hkeys_json() {
    file, err := json.MarshalIndent(hkeys, "", "    ")
 
	err = ioutil.WriteFile(hkeys_path, file, 0644)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

func update_rofi_list() {
    // Organizar as keys alfabeticamente
    hkeys_array := make([]string, 0, len(hkeys))
    for hkey := range hkeys {
        hkeys_array = append(hkeys_array, hkey)
    }
    sort.Strings(hkeys_array)

    e := os.Remove(rofi_list_path)
    if e != nil {
        log.Fatal(e)
    }

    rl, _ := os.OpenFile(rofi_list_path, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0600)
    defer rl.Close()

    for _, hkey := range hkeys_array {
        description := hkeys[hkey][1]
        entry := "'" + hkey + "': " + description + "\n"
        rl.WriteString(entry)
    }
    for i := 0; i < len(rkeys); i++ {
        rkey := rkeys[i][0]
        description := rkeys[i][1]
        entry := "'" + rkey + "': " + description + "\n"
        rl.WriteString(entry)
    }
}
