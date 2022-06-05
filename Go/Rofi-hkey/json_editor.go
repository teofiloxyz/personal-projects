package main

import (
    "rofi-hkey/rofi"
    "os"
    "fmt"
    "strings"
    "io/ioutil"
    "encoding/json"
)

func addHkey() {
    rofi.MenuMessage = " -mesg \"Aborted...\""

    newHkey := nameHkey("")
    if newHkey == "q" {
        return
    }

    newCommand := getCommand("")
    if newCommand == "q" {
        return
    }

    newDescription := getDescription("")
    if newDescription == "q" {
        return
    }

    if !confirmation("Add", newHkey, newCommand, newDescription) {
        return
    }

    hkeys[newHkey] = []string{newCommand, newDescription}
    go updateHkeysJson()
    rofi.MenuMessage = " -mesg \"'" + newHkey + "' Added!\""
}

func removeHkey() {
    rofi.MenuMessage = " -mesg \"Aborted...\""

    hkey := hkeySearch("Search Hkey to Remove")
    if hkey == "q" {
        return
    }

    command := hkeys[hkey][0]
    description := hkeys[hkey][1]

    if !confirmation("Remove", hkey, command, description) {
        return
    }

    delete(hkeys, hkey)
    go updateHkeysJson()

    rofi.MenuMessage = " -mesg \"'" + hkey + "' Removed!\""
}

func editHkey() string {
    hkey := hkeySearch("Search Hkey to Edit")
    if hkey == "q" {
        return " -mesg \"Aborted...\""
    }

    command := hkeys[hkey][0]
    description := hkeys[hkey][1]

    rofi.MenuMessage = ""
    for {
        prompt := "Edit what?"
        dmenu := []string {"Hkey: " + hkey, "Command: " + command, "Description: " + description, "Quit"}

        section := rofi.CustomDmenu(prompt, dmenu, false)
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
                rofi.MenuMessage = " -mesg \"Nothing has been changed...\""
                continue
            }

            delete(hkeys, hkey)
            hkeys[newHkey] = []string{command, description}
            go updateHkeysJson()

            rofi.MenuMessage = " -mesg \"Hkey changed from '" + hkey + "' to '" + newHkey + "'\""
            hkey = newHkey
        case "Command":
            menuMessagePrefix := "Current Command: " + command
            newCommand := getCommand(menuMessagePrefix)
            if newCommand == "q" {
                return " -mesg \"Aborted...\""
            } else if newCommand == command {
                rofi.MenuMessage = " -mesg \"Nothing has been changed...\""
                continue
            }

            hkeys[hkey] = []string{newCommand, description}
            go updateHkeysJson()

            rofi.MenuMessage = " -mesg \"Command changed from '" + command + "' to '" + newCommand + "'\""
            command = newCommand
        case "Description":
            menuMessagePrefix := "Current Description: " + description
            newDescription := getDescription(menuMessagePrefix)
            if newDescription == "q" {
                return " -mesg \"Aborted...\""
            } else if newDescription == description {
                rofi.MenuMessage = " -mesg \"Nothing has been changed...\""
                continue
            }

            hkeys[hkey] = []string{command, newDescription}
            go updateHkeysJson()

            rofi.MenuMessage = " -mesg \"Description changed from '" + description + "' to '" + newDescription + "'\""
            description = newDescription
        case "Quit\n": // Bug (a func do menu já retira \n)
            return " -mesg \"Exited edition mode\""
        }
    }
}

func hkeySearch(prompt string) string {
    rofi.MenuMessage = ""
    hkeySearchLoop:for {
        dmenu := createHkeysArray()
        userInput := rofi.CustomDmenu(prompt, dmenu, true)

        if userInput == "q" {
            return "q"
        }

        for _, rkeyEntry := range rkeys {
            rkey := rkeyEntry[0]
            if userInput == rkey {
                description := rkeyEntry[1]
                rofi.MenuMessage = " -mesg \"'" + rkey + "' is a reserved key used to: " + description + "\""
                continue hkeySearchLoop
            }
        }

        return userInput
    }
}

func nameHkey(menuMessagePrefix string) string {
    rofi.MenuMessage = " -mesg \"" + menuMessagePrefix + "[If you'll run the command with an input (e.g.: google 'input') make sure the hkey has a space at the end, otherwise don't leave a space]\""

    nameHkeyLoop:for {
        newHkey := rofi.SimplePrompt("Enter the New Hkey")

        if newHkey == "q" || newHkey == "" {
            return "q"
        }

        for hkey := range hkeys {
            if newHkey == hkey {
                command := hkeys[newHkey][0]
                rofi.MenuMessage = " -mesg \"'" + newHkey + "' already exists for the following command: '" + command + "'\""
                continue nameHkeyLoop
            }
        }

        for _, rkeyEntry := range rkeys {
            rkey := rkeyEntry[0]
            if newHkey == rkey {
                description := rkeyEntry[1]
                rofi.MenuMessage = " -mesg \"'" + rkey + "' is a reserved key used to: " + description + "\""
                continue nameHkeyLoop
            }
        }

        return newHkey
    }
}

func getCommand(menuMessagePrefix string) string {
    if menuMessagePrefix != "" {
        rofi.MenuMessage = " -mesg \"" + menuMessagePrefix + "\""
    } else {
        rofi.MenuMessage = ""
    }
    newCommand := rofi.SimplePrompt("Enter the full command to link to the Hkey")

    if newCommand == "q" || newCommand == "" {
        return "q"
    }

    return newCommand
}

func getDescription(menuMessagePrefix string) string {
    if menuMessagePrefix != "" {
        rofi.MenuMessage = " -mesg \"" + menuMessagePrefix + "\""
    } else {
        rofi.MenuMessage = ""
    }
    for {
        newDescription := rofi.SimplePrompt("Enter a description of the command")

        if newDescription == "q" || newDescription == "" {
            return "q"
        } else if len(newDescription) > 60 {
            rofi.MenuMessage = " -mesg \"Description is too long...\""
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
    rofi.MenuMessage = " -mesg \"Hkey: " + hkey + "\nCommand: " + command + "\nDescription: " + description + "\""
    dmenu := []string {"Yes", "No"}

    confirmation := rofi.CustomDmenu(prompt, dmenu, false)
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
