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

func editHkey() {
    hkey := hkeySearch("Search Hkey to Edit")
    if hkey == "q" {
        return
    }
    command := hkeys[hkey][0]
    description := hkeys[hkey][1]
    rofi.MenuMessage = ""

    var section string
    sectionEdit := func(sectionOld *string, sectionFunc func(string) string) {
        menuMessagePrefix := "Current " + section + ": " + *sectionOld + "\n"
        sectionNew := sectionFunc(menuMessagePrefix)
        if sectionNew == "q" {
            return
        } else if sectionNew == *sectionOld {
            rofi.MenuMessage = " -mesg \"Nothing has been changed...\""
            return
        }

        if section == "Hkey" {
            delete(hkeys, *sectionOld)
        }

        rofi.MenuMessage = " -mesg \"" + section + " changed from '" + *sectionOld + "' to '" + sectionNew + "'\""
        *sectionOld = sectionNew
        hkeys[hkey] = []string{command, description}
        go updateHkeysJson()
    }

    for {
        prompt := "Edit what?"
        dmenu := []string {"Hkey: " + hkey, "Command: " + command, "Description: " + description, "Quit"}
        section = rofi.CustomDmenu(prompt, dmenu, false)
        if strings.Contains(section, ":") {
            section = strings.Split(section, ":")[0]
        }

        switch(section) {
        case "Hkey":
            sectionEdit(&hkey, nameHkey)
        case "Command":
            sectionEdit(&command, getCommand)
        case "Description":
            sectionEdit(&description, getDescription)
        case "Quit":
            rofi.MenuMessage = " -mesg \"Exited edition mode\""
            return
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
            rofi.MenuMessage = " -mesg \"Aborted...\""
            return "q"
        }

        for hkey := range hkeys {
            if newHkey == hkey {
                description := hkeys[newHkey][1]
                rofi.MenuMessage = " -mesg \"'" + newHkey + "' already exists to: '" + description + "'\""
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
        rofi.MenuMessage = " -mesg \"Aborted...\""
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
            rofi.MenuMessage = " -mesg \"Aborted...\""
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
        rofi.MenuMessage = " -mesg \"Aborted...\""
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
