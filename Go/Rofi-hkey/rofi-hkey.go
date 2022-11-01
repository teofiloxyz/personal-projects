// Rofi-hkey (ou Rofi-hotkey) é a integração do hkey no rofi
// atua como launcher, através da execução de comandos na shell.
// Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
// específica deste programa.

// Might change the rofi front-end to gioui in the future
// Needs a bit of tweaking and testing

package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"rofi-hkey/rofi"
	"sort"
	"strings"
	"time"

	"gopkg.in/ini.v1"
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
var userInput string
var commandInput string
var command string
var lsMode bool = false

func main() {
	getInfoFromConfig()
	go getHkeysFromJson()

	for {
		if !lsMode {
			userInput = rofi.SimplePrompt("Enter Hkey")
		}

		option := checkIfIsHkey()
		if option == "launch" {
			go historyAppend(userInput + commandInput)
			launchHkey(command)
		} else if option == "back" {
			lsMode = false
		} else {
			checkIfIsRkey()
		}
	}
}

func getInfoFromConfig() {
	home, _ := os.UserHomeDir()
	config, err := ini.Load(home + "/.config/hkey/hkey.ini")
	if err != nil {
		log.Fatal(err)
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

func checkIfIsHkey() string {
	// Separar, e ver se o input não é nulo, caso seja uma hkey que necessite de input (e.g.: "s <search entry>")
	var hkeyNeedsInput bool
	if strings.Contains(userInput, " ") {
		commandInput = userInput[strings.Index(userInput, " ")+1:]
		userInput = strings.SplitAfter(userInput, " ")[0]
		if strings.ReplaceAll(commandInput, " ", "") == "" {
			hkeyNeedsInput = true
		}
	}

	for hkey := range hkeys {
		if hkey == userInput {
			if hkeyNeedsInput {
				commandInput = rofi.SimplePrompt(hkeys[hkey][1])
				if commandInput == "" || commandInput == "q" {
					rofi.MenuMessage = " -mesg \"Aborted...\""
					return "back"
				}
			}
			command = hkeys[hkey][0] + " " + commandInput
			return "launch"
		}
	}
	return "notHkey"
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

func launchHkey(command string) {
	var cmd *exec.Cmd
	if strings.HasPrefix(command, "bash -c") {
		command = strings.TrimSpace(strings.TrimPrefix(command, "bash -c"))
		// trimming/stripping '' or "" of the command
		command = command[1 : len(command)-1]
		// setsid para iniciar cmd noutra shell
		cmd = exec.Command("setsid", "bash", "-c", command)
	} else {
		command = "setsid " + strings.TrimSpace(command)
		commandArray := strings.Fields(command)
		cmd = exec.Command(commandArray[0], commandArray[1:]...)
	}

	defer os.Exit(0)
	err := cmd.Start()
	if err != nil {
		log.Fatal(err)
	}
}

func checkIfIsRkey() {
	switch userInput {
	case "ls":
		if lsMode {
			rofi.MenuMessage = " -mesg \"You are already using ls...\""
		} else {
			rofi.MenuMessage = ""
		}
		// Search/filter mode das hkeys, com dropdown menu
		dmenu := createHkeysArray()
		userInput = rofi.CustomDmenu("Search Hkey", dmenu, true)
		lsMode = true
		return
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
	}
	lsMode = false
}

func createHkeysArray() []string {
	// Organizar as keys alfabeticamente
	hkeysArray := make([]string, 0, len(hkeys))
	for hkey := range hkeys {
		description := hkeys[hkey][1]
		hkeysArray = append(hkeysArray, "'"+hkey+"': "+description)
	}
	sort.Strings(hkeysArray)

	// Pôr rkeys no final da lista
	for _, rkeyEntry := range rkeys {
		rkey := rkeyEntry[0]
		description := rkeyEntry[1]
		hkeysArray = append(hkeysArray, "'"+rkey+"': "+description)
	}

	return hkeysArray
}

func showHelpDialog() {
	message := "General options: \n"

	for i, rkeyEntry := range rkeys {
		rkey := rkeyEntry[0]
		description := rkeyEntry[1]
		message += "'" + rkey + "': " + description
		if i < len(rkeys)-1 {
			message += "\n"
		}
	}

	rofi.MessageBox(message)
}
