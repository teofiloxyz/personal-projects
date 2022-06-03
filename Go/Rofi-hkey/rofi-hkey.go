// Rofi-hkey (ou Rofi-hotkey) é a integração do hkey no rofi
// atua como launcher, através da execução de comandos na shell.
// Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
// específica deste programa.

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

var hkeysPath string 
var historyPath string 
var rofiListPath string
var hkeys map[string][]string
var rkeys map[int][]string

func main() {
    getInfoFromConfig()
    go getHkeysFromJson()
    // Fiz assim apenas para ficar nesta ordem específica quando é mostrado o 'help dialog'
    // Talvez haja uma forma mais simples
    rkeys = map[int][]string{0: {"ls", "Search for hkeys"},
                             1: {"ad", "Add entry to hotkeys list"},
                             2: {"rm", "Remove entry from hotkeys list"},
                             3: {"ed", "Edit entry from hotkeys list"},
                             4: {"h", "Show help dialog"},
                             5: {"q", "Quit"}}
    var menuMessage string

    hkeyLoop:for {
        userInput := rofiSimplePrompt("Enter Hkey", menuMessage)

        // Search/filter mode das hkeys, com dropdown menu
        if userInput == "ls" {
            userInput = rofiDmenuHkeys("Search Hkey", "")
            menuMessage = ""
        }

        fullUserInput := userInput

        // Caso tenha input (e.g.: s <search entry>)
        var commandInput string
        var needsInput bool
        if strings.Contains(userInput, " ") {
            userInput = strings.SplitAfter(fullUserInput, " ")[0]
            commandInput = strings.TrimPrefix(fullUserInput, userInput)

            // Ver se o input não é nulo
            if strings.ReplaceAll(commandInput, " ", "") == "" {
                needsInput = true
            }
        }

        // Reconhecimento e launch da hkey
        for hkey := range hkeys {
            if hkey == userInput {

                if needsInput {
                    commandInput = rofiSimplePrompt(hkeys[hkey][1], menuMessage)
                    if commandInput == "" || commandInput == "q" {
                        menuMessage = ""
                        continue hkeyLoop
                    }
                }

                command := hkeys[hkey][0] + " " + commandInput

                go historyAppend(fullUserInput)

                launchHkey(command)
                os.Exit(0)
            }
        }
        
        // Rkeys e respetivas funções
        switch(userInput) {
        case "ad":
            menuMessage = addHkey()
        case "rm":
            menuMessage = removeHkey()
        case "ed":
            menuMessage = editHkey()
        case "h":
            showHelpDialog()
            menuMessage = ""
        case "q":
            os.Exit(0)
        default:
            menuMessage = " -mesg \"Invalid key... \nEnter 'h' for help\""
            continue
        }

    }
}

func getInfoFromConfig() {
    configPath := "config.ini"
    config, err := ini.Load(configPath)
     if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    hkeysPath = config.Section("GENERAL").Key("hkeysPath").String()
    historyPath = config.Section("GENERAL").Key("historyPath").String()
    rofiListPath = config.Section("GENERAL").Key("rofiListPath").String()
}

func getHkeysFromJson() {
    hkeysJson, err := os.Open(hkeysPath)
    if err != nil {
        fmt.Println("No hkeys.json file found...\nCreating one...")
        fmt.Println()
        go updateHkeysJson()
    }
    defer hkeysJson.Close()

    hkeysContent, _ := ioutil.ReadAll(hkeysJson)

    json.Unmarshal(hkeysContent, &hkeys)
}

func launchHkey(command string) {
    // Melhorar a forma como o processo começa
    command = "setsid " + strings.TrimSpace(command)

    commandArray := strings.Fields(command)
    cmd := exec.Command(commandArray[0], commandArray[1:]...)

    // Aqui tenho que dar um delay para o programa não fechar antes do comando ser executado
    // É estranho...
    err := cmd.Start()
    time.Sleep(time.Second / 10)
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
}

func historyAppend(fullUserInput string) {
    // Melhorar esta func

    // Se não existir history.csv, escreve o header do csv
    var header string
    _, err := os.Stat(historyPath)
    if err != nil {
        header = "date,entry\n"
    }

    hs, err := os.OpenFile(historyPath, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0600)
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

    fullUserInput = strings.ReplaceAll(fullUserInput, ",", "")
    now := time.Now().Format("2006-01-02 15:04:05")
    entry := now + "," + fullUserInput + "\n"
    _, err = hs.WriteString(entry)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

func showHelpDialog() {
    message := "General options: \n"

    for i := 0; i < len(rkeys); i++ {
        rkey := rkeys[i][0]
        description := rkeys[i][1]
        message += "'" + rkey + "': " + description
        if i < len(rkeys) - 1 {
            message += "\n"
        }
    }

    rofiMessage(message)
}

func rofiSimplePrompt(prompt string, message string) string {
    cmd := "rofi -dmenu -p '" + prompt + "' -l 0 -theme-str 'entry { placeholder: \"\"; } inputbar { children: [prompt, textbox-prompt-colon, entry]; } listview { border: 0; }'" + message
    output, err := exec.Command("bash", "-c", cmd).Output()
    if err != nil {
        log.Fatal(err)
    }

    return strings.TrimSuffix(string(output), "\n")
}

func rofiDmenuHkeys(prompt string, message string) string {
    cmd := "rofi -dmenu -i -input " + rofiListPath + " -p '" + prompt + "' -theme-str 'entry { placeholder: \"\"; } inputbar { children: [prompt, textbox-prompt-colon, entry]; }'" + message
    output, err := exec.Command("bash", "-c", cmd).Output()
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }

    hkey := strings.Split(string(output), ":")[0]
    return strings.Trim(hkey, "'")
}

func rofiCustomDmenu(prompt string, message string, dmenu []string) string {
    var dmenuInput string
    for i, entry := range dmenu {
        dmenuInput += entry
        if i < len(dmenu) - 1 {
            dmenuInput += "|"
        }
    }
    
    var dmenuLines string
    if len(dmenu) < 15 {
        dmenuLines = strconv.Itoa(len(dmenu))
    } else {
        dmenuLines = "15"
    }

    cmd := "echo '" + dmenuInput + "' | rofi -sep '|' -dmenu -i -p '" + prompt + "' -l " + dmenuLines + " -theme-str 'entry { placeholder: \"\"; } inputbar { children: [prompt, textbox-prompt-colon, entry]; }'" + message
    output, err := exec.Command("bash", "-c", cmd).Output()
    if err != nil {
        log.Fatal(err)
    }

    return strings.TrimSuffix(string(output), "\n")
}

func rofiMessage(message string) {
    cmd := exec.Command("rofi", "-e", message)
    err := cmd.Run()
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
}

func addHkey() string {
    newHkey := nameHkey("")
    if newHkey == "q" {
        return " -mesg \"Aborted...\""
    }

    newCommand := getCommand("")
    if newCommand == "q" {
        return " -mesg \"Aborted...\""
    }

    newDescription := getDescription("")
    if newDescription == "q" {
        return " -mesg \"Aborted...\""
    }

    if !confirmation("Add", newHkey, newCommand, newDescription) {
        return " -mesg \"Aborted...\""
    }

    hkeys[newHkey] = []string{newCommand, newDescription}
    go updateHkeysJson()
    go updateRofiList()
    return " -mesg \"'" + newHkey + "' Added!\""
}

func removeHkey() string {
    hkey := hkeySearch("Search Hkey to Remove")
    if hkey == "q" {
        return " -mesg \"Aborted...\""
    }

    command := hkeys[hkey][0]
    description := hkeys[hkey][1]

    if !confirmation("Remove", hkey, command, description) {
        return " -mesg \"Aborted...\""
    }

    delete(hkeys, hkey)
    go updateHkeysJson()
    go updateRofiList()

    return " -mesg \"'" + hkey + "' Removed!\""
}

func editHkey() string {
    hkey := hkeySearch("Search Hkey to Edit")
    if hkey == "q" {
        return " -mesg \"Aborted...\""
    }

    command := hkeys[hkey][0]
    description := hkeys[hkey][1]

    menuMessage := ""
    for {
        prompt := "Edit what?"
        dmenuOpts := []string {"Hkey: " + hkey, "Command: " + command, "Description: " + description, "Quit"}

        section := rofiCustomDmenu(prompt, menuMessage, dmenuOpts)
        if strings.Contains(section, ":") {
            section = strings.Split(section, ":")[0]
        }

        // Optimizar isto... (talvez com uma nested func)
        switch(section) {
        case "Hkey":
            menuMessagePrefix := "Current Hkey: " + hkey + "\n"
            newHkey := nameHkey(menuMessagePrefix)
            if newHkey == "q" {
                return " -mesg \"Aborted...\""
            } else if newHkey == hkey {
                menuMessage = " -mesg \"Nothing has been changed...\""
                continue
            }

            delete(hkeys, hkey)
            hkeys[newHkey] = []string{command, description}
            go updateHkeysJson()
            go updateRofiList()

            menuMessage = " -mesg \"Hkey changed from '" + hkey + "' to '" + newHkey + "'\""
            hkey = newHkey
        case "Command":
            menuMessagePrefix := "Current Command: " + command
            newCommand := getCommand(menuMessagePrefix)
            if newCommand == "q" {
                return " -mesg \"Aborted...\""
            } else if newCommand == command {
                menuMessage = " -mesg \"Nothing has been changed...\""
                continue
            }

            hkeys[hkey] = []string{newCommand, description}
            go updateHkeysJson()
            go updateRofiList()

            menuMessage = " -mesg \"Command changed from '" + command + "' to '" + newCommand + "'\""
            command = newCommand
        case "Description":
            menuMessagePrefix := "Current Description: " + description
            newDescription := getDescription(menuMessagePrefix)
            if newDescription == "q" {
                return " -mesg \"Aborted...\""
            } else if newDescription == description {
                menuMessage = " -mesg \"Nothing has been changed...\""
                continue
            }

            hkeys[hkey] = []string{command, newDescription}
            go updateHkeysJson()
            go updateRofiList()

            menuMessage = " -mesg \"Description changed from '" + description + "' to '" + newDescription + "'\""
            description = newDescription
        case "Quit\n": // Bug (a func do menu já retira \n)
            return " -mesg \"Exited edition mode\""
        }
    }
}

func hkeySearch(prompt string) string {
    menuMessage := ""
    hkeySearchLoop:for {
        userInput := rofiDmenuHkeys(prompt, menuMessage)

        if userInput == "q" {
            return "q"
        }

        for i := range rkeys {
            rkey := rkeys[i][0]
            if userInput == rkey {
                description := rkeys[i][1]
                menuMessage = " -mesg \"'" + rkey + "' is a reserved key used to: " + description + "\""
                continue hkeySearchLoop
            }
        }

        return userInput
    }
}

func nameHkey(menuMessagePrefix string) string {
    menuMessage := " -mesg \"" + menuMessagePrefix + "[If you'll run the command with an input (e.g.: google 'input') make sure the hkey has a space at the end, otherwise don't leave a space]\""

    nameHkeyLoop:for {
        newHkey := rofiSimplePrompt("Enter the New Hkey", menuMessage)

        if newHkey == "q" || newHkey == "" {
            return "q"
        }  

        for hkey := range hkeys {
            if newHkey == hkey {
                command := hkeys[newHkey][0]
                menuMessage = " -mesg \"'" + newHkey + "' already exists for the following command: '" + command + "'\""
                continue nameHkeyLoop
            }
        }

        for i := range rkeys {
            rkey := rkeys[i][0]
            if newHkey == rkey {
                description := rkeys[i][1]
                menuMessage = " -mesg \"'" + rkey + "' is a reserved key used to: " + description + "\""
                continue nameHkeyLoop
            }
        }

        return newHkey
    }
}

func getCommand(menuMessagePrefix string) string {
    var menuMessage string
    if menuMessagePrefix != "" {
        menuMessage = " -mesg \"" + menuMessagePrefix + "\""
    } else {
        menuMessage = ""
    }
    newCommand := rofiSimplePrompt("Enter the full command to link to the Hkey", menuMessage)

    if newCommand == "q" || newCommand == "" {
        return "q"
    }

    return newCommand
}

func getDescription(menuMessagePrefix string) string {
    var menuMessage string
    if menuMessagePrefix != "" {
        menuMessage = " -mesg \"" + menuMessagePrefix + "\""
    } else {
        menuMessage = ""
    }
    for {
        newDescription := rofiSimplePrompt("Enter a description of the command", menuMessage)

        if newDescription == "q" || newDescription == "" {
            return "q"
        } else if len(newDescription) > 60 {
            menuMessage = " -mesg \"Description is too long...\""
            continue
        }

        newDescriptionArray := strings.Split(strings.TrimSpace(newDescription), " ")
        newDescription = ""
        // Faço desta forma pq podem haver siglas (com todas as letras maiúsculas)
        // Melhorar isto
        for i, word := range newDescriptionArray {
            word = strings.ToUpper(word[:1]) + word[1:]
            newDescription += word
            if i < len(newDescriptionArray) - 1 {
                newDescription += " "
            }
        }

        return strings.TrimSuffix(newDescription, " ")
    }
}

func confirmation(mode string, hkey string, command string, description string) bool{
    prompt := mode + " this entry?"
    menuMessage := " -mesg \"Hkey: " + hkey + "\nCommand: " + command + "\nDescription: " + description + "\""
    dmenuOpts := []string {"Yes", "No"}

    confirmation := rofiCustomDmenu(prompt, menuMessage, dmenuOpts)
    if confirmation == "Yes" {
        return true
    } else {
        return false
    }
}

func updateHkeysJson() {
    file, err := json.MarshalIndent(hkeys, "", "    ")
 
	err = ioutil.WriteFile(hkeysPath, file, 0644)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

func updateRofiList() {
    // Organizar as keys alfabeticamente
    hkeysArray := make([]string, 0, len(hkeys))
    for hkey := range hkeys {
        hkeysArray = append(hkeysArray, hkey)
    }
    sort.Strings(hkeysArray)

    e := os.Remove(rofiListPath)
    if e != nil {
        log.Fatal(e)
    }

    rl, _ := os.OpenFile(rofiListPath, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0600)
    defer rl.Close()

    for _, hkey := range hkeysArray {
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
