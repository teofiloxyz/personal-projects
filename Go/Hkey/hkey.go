// Hkey (ou hotkey) atua como launcher (semelhante ao dmenu/rofi), através
// da execução de comandos na shell. Este programa podia ser substituído por
// 'bashrc aliases' no terminal, no entanto, isso iria criar conflitos com comandos
// da shell, dada a enorme diversidade de potenciais hotkeys.
// Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
// específica deste programa. Em breve, o mesmo terá uma interface gráfica.
// Com interface gráfica, deixará de haver a opção 'shell_session',
// passando todos os comandos a serem executados numa 'new_session'.

// Os nomes das variáveis e das funções estão em 'snake_case'

package main

import (
     "os"
     "os/exec"
     "log"
     "time"
     "fmt"
     "strings"
     "bufio"
     "io/ioutil"
     "encoding/json"
     "gopkg.in/ini.v1"
     "sort"
)

var hkeys_path string 
var history_path string 
var python_hist_file string 
var hkeys map[string][]string
var rkeys map[int][]string

func main() {
    get_info_from_config()
    go get_hkeys_from_json()
    // Fiz assim apenas para ficar nesta ordem específica quando é mostrado o 'help dialog'
    // Talvez haja uma forma mais simples
    rkeys = map[int][]string{0: {"ls", "Show hotkeys list"},
                             1: {"ad", "Add entry to hotkeys list"},
                             2: {"rm", "Remove entry from hotkeys list"},
                             3: {"ed", "Edit entry from hotkeys list"},
                             4: {"hs", "Go to history menu"},
                             5: {"h", "Show help dialog"},
                             6: {"q", "Quit"}}

    hkeyloop:for {
        fmt.Print("Enter hkey: ")
        reader := bufio.NewReader(os.Stdin)
        hkey, _ := reader.ReadString('\n')
        hkey = strings.TrimSuffix(hkey, "\n")
        full_hkey := hkey

        // Caso a hkey tenha input (e.g.: s <search entry>)
        var command_input string
        if strings.Contains(hkey, " ") {
            hkey = strings.SplitAfter(full_hkey, " ")[0]
            command_input = strings.TrimPrefix(full_hkey, hkey)

            if strings.ReplaceAll(command_input, " ", "") == "" {
                fmt.Println("Input should be something...")
                fmt.Println()
                continue hkeyloop
            }
        }

        // Reconhecimento da hkey
        for hk := range hkeys {
            if hkey == hk {
                command := hkeys[hkey][0] + " " + command_input

                new_session := false
                if hkeys[hkey][2] == "New Session" {
                    new_session = true
                }

                go history_append(full_hkey)

                launch_hkey(command, new_session)
                os.Exit(0)
            }
        }
        
        // Rkeys e respetivas funções
        switch(hkey) {
        case "ls":
            show_hkeys()
        case "ad":
            add_hkey()
        case "rm":
            remove_hkey()
        case "ed":
            edit_hkey()
        case "hs":
            history_menu()
        case "h":
            show_help_dialog()
        case "q":
            os.Exit(0)
        default:
            fmt.Println("Invalid key...\nEnter 'h' for help")
            fmt.Println()
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

func launch_hkey(command string, new_session bool) {
    // Melhorar a forma como o processo começa noutra shell session
    if new_session {
        command = "setsid " + command
    } 

    command_array := strings.Fields(command)
    cmd := exec.Command(command_array[0], command_array[1:]...)

    var err error
    if new_session {
        // Aqui tenho que dar um delay para o programa não fechar antes do comando ser executado
        // É estranho...
        err = cmd.Start()
        time.Sleep(time.Second / 10)
    } else {
        cmd.Stdin = os.Stdin
        cmd.Stdout = os.Stdout
        cmd.Stderr = os.Stderr
        err = cmd.Run()
    }
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
}

func history_append(full_hkey string) {
    // Melhorar esta func
    // Se não existir history, escreve o header
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

    full_hkey = strings.ReplaceAll(full_hkey, ",", "")
    now := time.Now().Format("2006-01-02 15:04:05")
    entry := now + "," + full_hkey + "\n"
    _, err = hs.WriteString(entry)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

func history_menu() {
    // Isto inicia o script de python hkey no history menu
    // Futuramente o programa deixará de depender de Python para analisar o histórico
    cmd := exec.Command("python", python_hist_file, "history_menu")
    cmd.Stdin = os.Stdin
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr

    err := cmd.Run()
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
}

func show_help_dialog() {
    // Não posso usar 'range rkeys', para manter a ordem específica
    for i := 0; i < len(rkeys); i++ {
        rkey := rkeys[i][0]
        description := rkeys[i][1]
        fmt.Println("'" + rkey + "': " + description)
    }
    fmt.Println()
}

func show_hkeys() {
    if len(hkeys) == 0 {
        fmt.Println("Hkeys list is empty...\nEnter 'ad' to add a new hkey")
        fmt.Println()
        return
    }

    // Organiza alfabeticamente as hkeys para mostrar as mesmas
    keys := make([]string, 0, len(hkeys))
    for key := range hkeys {
        keys = append(keys, key)
    }
    sort.Strings(keys)

    for _, key := range keys {
        description := hkeys[key][1]
        fmt.Println("'" + key + "': " + description)
    }
    fmt.Println()
}

func add_hkey() {
    fmt.Println("\nAdding mode")

    new_hkey := name_hkey()
    if new_hkey == "q" {
        return
    }

    new_command := get_command()
    if new_command == "q" {
        return
    }

    new_description := get_description()
    if new_description == "q" {
        return
    }

    new_shell_session := get_shell_session()
    if new_shell_session == "q" {
        return
    }

    if !confirmation("Add", new_hkey, new_command, new_description, new_shell_session) {
        return
    }

    hkeys[new_hkey] = []string{new_command, new_description, new_shell_session}
    go update_hkeys_json()

    fmt.Println("Added!")
    fmt.Println()
}

func remove_hkey() {
    fmt.Println("\nRemoving mode")

    hkey := hkey_search()
    if hkey == "q" {
        return
    }

    command := hkeys[hkey][0]
    description := hkeys[hkey][1]
    shell_session := hkeys[hkey][2]

    if !confirmation("Remove", hkey, command, description, shell_session) {
        return
    }

    delete(hkeys, hkey)
    go update_hkeys_json()

    fmt.Println("Removed!")
    fmt.Println()
}

func edit_hkey() {
    fmt.Println("\nEditing mode")

    hkey := hkey_search()
    if hkey == "q" {
        return
    }

    command := hkeys[hkey][0]
    description := hkeys[hkey][1]
    shell_session := hkeys[hkey][2]

    for {
        fmt.Println()
        fmt.Println("[1] Hkey: " + hkey + "\n[2] Command: " + command + "\n[3] Description: " + description + "\n[4] Shell: " + shell_session)

        fmt.Print("Edit what? (Enter 'q' to exit edition mode): ")
        reader := bufio.NewReader(os.Stdin)
        section, _ := reader.ReadString('\n')
        section = strings.TrimSuffix(section, "\n")

        if section == "q" || section == "" {
            fmt.Println("Exited edition mode")
            fmt.Println()
            return
        }

        // Optimizar isto... (talvez com uma nested func)
        switch(section) {
        case "1":
            fmt.Println("Current Hkey: " + hkey)

            new_hkey := name_hkey()
            if new_hkey == "q" {
                return
            } else if new_hkey == hkey {
                fmt.Println("Nothing has been changed...")
                continue
            }

            delete(hkeys, hkey)
            hkeys[new_hkey] = []string{command, description, shell_session}
            go update_hkeys_json()

            fmt.Println("Hkey changed from '" + hkey + "' to '" + new_hkey + "'")
            hkey = new_hkey
        case "2":
            fmt.Println("Current Command: " + command)

            new_command := get_command()
            if new_command == "q" {
                return
            } else if new_command == command {
                fmt.Println("Nothing has been changed...")
                continue
            }

            hkeys[hkey] = []string{new_command, description, shell_session}
            go update_hkeys_json()

            fmt.Println("Command changed from '" + command + "' to '" + new_command + "'")
            command = new_command
        case "3":
            fmt.Println("Current Description: " + description)

            new_description := get_description()
            if new_description == "q" {
                return
            } else if new_description == description {
                fmt.Println("Nothing has been changed...")
                continue
            }

            hkeys[hkey] = []string{command, new_description, shell_session}
            go update_hkeys_json()

            fmt.Println("Description changed from '" + description + "' to '" + new_description + "'")
            description = new_description
        case "4":
            fmt.Println("Current Shell: " + shell_session)

            new_shell_session := get_shell_session()
            if new_shell_session == "q" {
                return
            } else if new_shell_session == shell_session {
                fmt.Println("Nothing has been changed...")
                continue
            }

            hkeys[hkey] = []string{command, description, new_shell_session}
            go update_hkeys_json()

            fmt.Println("Shell changed from '" + shell_session + "' to '" + new_shell_session + "'")
            shell_session = new_shell_session
        } 
    }
}

func hkey_search() string {
    hkey_search_loop:for {
        fmt.Print("\nEnter hkey to search: ")
        reader := bufio.NewReader(os.Stdin)
        hkey, _ := reader.ReadString('\n')
        hkey = strings.TrimSuffix(hkey, "\n")

        if hkey == "q" || hkey == "" {
            fmt.Println("Aborted...")
            fmt.Println()
            return "q"
        }

        for hk := range hkeys {
            if hkey == hk {
                return hkey
            }
        }

        for i := range rkeys {
            rkey := rkeys[i][0]
            if hkey == rkey {
                description := rkeys[i][1]
                fmt.Println("'" + rkey + "' is a reserved key used to: " + description)
                continue hkey_search_loop
            }

        }

        fmt.Println("'" + hkey + "' not found")
    }
}

func name_hkey() string {
    fmt.Println("\n[If you'll run the command with an input (e.g.: google <input>) make sure the hkey has a space at the end, otherwise don't leave a space]")

    name_hkey_loop:for {
        fmt.Print("\nEnter the new hkey: ")
        reader := bufio.NewReader(os.Stdin)
        new_hkey, _ := reader.ReadString('\n')
        new_hkey = strings.TrimSuffix(new_hkey, "\n")

        if new_hkey == "q" || new_hkey == "" {
            fmt.Println("Aborted...")
            fmt.Println()
            return "q"
        }  

        for hk := range hkeys {
            if new_hkey == hk {
                command := hkeys[new_hkey][0]
                fmt.Println("'" + new_hkey + "' already exists for the following command: '" + command + "'")
                continue name_hkey_loop
            }
        }

        for i := range rkeys {
            rkey := rkeys[i][0]
            if new_hkey == rkey {
                description := rkeys[i][1]
                fmt.Println("'" + rkey + "' is a reserved key used to: " + description)
                continue name_hkey_loop
            }
        }

        return new_hkey
    }
}

func get_command() string {
    fmt.Print("Enter the full command to link to the hkey: ")
    reader := bufio.NewReader(os.Stdin)
    new_command, _ := reader.ReadString('\n')
    new_command = strings.TrimSuffix(new_command, "\n")

    if new_command == "q" || new_command == "" {
        fmt.Println("Aborted...")
        fmt.Println()
        return "q"
    }

    return new_command
}

func get_description() string {
    for {
        fmt.Print("Enter a description of the command: ")
        reader := bufio.NewReader(os.Stdin)
        new_description, _ := reader.ReadString('\n')
        new_description = strings.TrimSuffix(new_description, "\n")

        if new_description == "q" || new_description == "" {
            fmt.Println("Aborted...")
            fmt.Println()
            return "q"
        } else if len(new_description) > 80 {
            fmt.Println("Description is too long...")
            continue
        }

        return new_description
    }
}

func get_shell_session() string {
    fmt.Print(":: When launched, should the command be started on a new shell session? [y/N] ")
    reader := bufio.NewReader(os.Stdin)
    new_shell_session, _ := reader.ReadString('\n')
    new_shell_session = strings.TrimSuffix(new_shell_session, "\n")
    new_shell_session = strings.ToLower(new_shell_session)

    if new_shell_session == "n" || new_shell_session == "" {
        return "Same Session"
    } else if new_shell_session == "y" {
        return "New Session"
    } else {
        fmt.Println("Aborted...")
        fmt.Println()
        return "q"
    }
}

func confirmation(mode string, hkey string, command string, description string, shell_session string) bool{
    fmt.Print("\nHkey: " + hkey + "\nCommand: " + command + "\nDescription: " + description + "\nShell: " + shell_session + "\n:: " + mode + " this entry? [Y/n] ")
    reader := bufio.NewReader(os.Stdin)
    confirmation, _ := reader.ReadString('\n')
    confirmation = strings.TrimSuffix(confirmation, "\n")
    confirmation = strings.ToLower(confirmation)

    if confirmation == "y" || confirmation == "" {
        return true
    } else {
        fmt.Println("Aborted...")
        fmt.Println()
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
