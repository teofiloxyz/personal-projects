// Rofi-hkey (ou Rofi-hotkey) é a integração do hkey no rofi
// atua como launcher, através da execução de comandos na shell.
// Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
// específica deste programa.

// Há muito para melhorar aqui

package main

import (
    "rofi-hkey/rofi"
    "os"
    "os/exec"
    "log"
    "time"
    "fmt"
    "strings"
    "io/ioutil"
    "encoding/json"
    "gopkg.in/ini.v1"
    "sort"
)

var hkeysPath string 
var historyPath string 
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

    hkeyLoop:for {
        userInput := rofi.SimplePrompt("Enter Hkey")

        // Search/filter mode das hkeys, com dropdown menu
        if userInput == "ls" {
            dmenu := createHkeysArray()
            rofi.MenuMessage = ""
            userInput = rofi.CustomDmenu("Search Hkey", dmenu, true)
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
                    commandInput = rofi.SimplePrompt(hkeys[hkey][1])
                    if commandInput == "" || commandInput == "q" {
                        rofi.MenuMessage = ""
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
            addHkey()
        case "rm":
            removeHkey()
        case "ed":
            editHkey()
        case "h":
            showHelpDialog()
            rofi.MenuMessage = ""
        case "q":
            os.Exit(0)
        default:
            rofi.MenuMessage = " -mesg \"Invalid key... \nEnter 'h' for help\""
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
}

func getHkeysFromJson() {
    hkeysJson, err := os.Open(hkeysPath)
    if err != nil {
        fmt.Println("No hkeys.json file found...\nCreating one...")
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

    rofi.Message(message)
}

func createHkeysArray() []string {
    // Organizar as keys alfabeticamente
    hkeysArray := make([]string, 0, len(hkeys))
    for hkey := range hkeys {
        description := hkeys[hkey][1]
        hkeysArray = append(hkeysArray, "'" + hkey + "': " + description)
    }
    sort.Strings(hkeysArray)

    // Pôr rkeys no final da lista
    for i := 0; i < len(rkeys); i++ {
        rkey := rkeys[i][0]
        description := rkeys[i][1]
        hkeysArray = append(hkeysArray, "'" + rkey + "': " + description)
    }

    return hkeysArray
}
