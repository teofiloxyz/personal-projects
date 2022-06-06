// Rofi-hkey (ou Rofi-hotkey) é a integração do hkey no rofi
// atua como launcher, através da execução de comandos na shell.
// Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
// específica deste programa.

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
// Not a map bc the order matters
var rkeys = [][]string{{"ls", "Search for hkeys"},
                       {"ad", "Add entry to hotkeys list"},
                       {"rm", "Remove entry from hotkeys list"},
                       {"ed", "Edit entry from hotkeys list"},
                       {"h", "Show help dialog"},
                       {"q", "Quit"}}

func main() {
    getInfoFromConfig()
    go getHkeysFromJson()

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
    config, err := ini.Load("config.ini")
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
        updateHkeysJson()
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
    defer time.Sleep(time.Second / 10)
    err := cmd.Start()
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
}

func historyAppend(fullUserInput string) {
    hs, err := os.OpenFile(historyPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        fmt.Println(err)
    }
    defer hs.Close()

    // Se history.csv estiver vazio, escreve o header do csv
    fInfo, _ := os.Stat(historyPath)
    if fInfo.Size() == 0 {
        _, err = hs.WriteString("date,entry\n")
        if err != nil {
            fmt.Println(err)
        }
    }

    now := time.Now().Format("2006-01-02 15:04:05")
    fullUserInput = strings.ReplaceAll(fullUserInput, ",", "")
    _, err = hs.WriteString(now + "," + fullUserInput + "\n")
    if err != nil {
        fmt.Println(err)
    }
}

func showHelpDialog() {
    message := "General options: \n"

    for i, rkeyEntry := range rkeys {
        rkey := rkeyEntry[0]
        description := rkeyEntry[1]
        message += "'" + rkey + "': " + description
        if i < len(rkeys) - 1 {
            message += "\n"
        }
    }

    rofi.MessageBox(message)
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
    for _, rkeyEntry := range rkeys {
        rkey := rkeyEntry[0]
        description := rkeyEntry[1]
        hkeysArray = append(hkeysArray, "'" + rkey + "': " + description)
    }

    return hkeysArray
}
