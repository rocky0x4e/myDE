#!/usr/bin/env node

const cp = require("node:child_process")
const { BatteryTracker } = require("../libjs/Helpers")
const { ColorMan } = require("../libjs/ColorManager")
const { MultiBLocksModule } = require("../libjs/Polybar")

const CONF = {
    powerIcons: {
        // "Unknown": "\ue55d",
        "Unknown": "\uf1e6",
        "true fully-charged": "\ue55c",
        "true charging": "\uf376",
        "true not charging": "\ue55e"
    },
    battIcons: {
        90: "\uf240",
        70: "\uf241",
        50: "\uf242",
        30: "\uf243",
        10: "\ue0b1",
        0: "\uf244",
    },
    battCrit: 15,
    toTrack: [["ZUOYA LMK67"], ["battery_BAT1"]],
    toShow: [
        {
            match: ["ZUOYA LMK67"],
            icon: "\uf11c"
        }
    ]
}

const tabCount = 2
function getIndentLevel(line) {
    for (var i in line) {
        let c = line[i]
        if (c != " ") {
            return i / tabCount
        }
    }
    return i
}
function storeData(key, value, path, obj) {
    let currentP = obj
    for (var item of path) {
        currentP = currentP[item]
    }
    currentP[key] = value
}

const upowerDevice = {
    default: {
        state: null,
        percentage: null,
        online: null
    },
    isMatch(criteria) {
        for (let criterion of criteria) {
            for (let match of [this["full-path"] || "", this["native-path"] || ""
                , this.vendor || "", this.model || ""]) {
                if (match.includes(criterion)) { return true }
            }
        }
        return false
    },
    getChargingStatus() {
        let obj = this.battery || this.mouse || this.keyboard || this.default
        return obj.state
    },
    getLinePower() {
        let obj = this["line-power"] || this.default
        return obj.online == "yes" ? true : false
    },
    polybarBatt(icon) {
        let color = ColorMan.getColorByPercent(this.percent(), false)
        return `%{F${color.fg}}${icon}%{F-}%{T4} ${this.percent()}%%{T-} `
    },
    tracker() {
        if (!this.battTracker) {
            var name1 = this.vendor || this.model
            var name2 = this.serial || this["native-path"]
            var trackFile = name1 + "_" + name2
            this.battTracker = new BatteryTracker(`upower/${trackFile}`)
        }
        return this.battTracker
    },
    percent() {
        let batInfo = this.battery || this.mouse || this.keyboard || this.default
        return Number(batInfo.percentage.replace("%", ""))
    }
}

class UPowerWrapper extends MultiBLocksModule {
    constructor() {
        super()
        this.data = this._parseJson(cp.execSync("upower -d").toString().trim())
        this.powerLine = this.findDevice(["line_power_ADP1"])
        this.coreBatt = this.findDevice(["battery_BAT1"])
        this.alertCoreBattCrit()
    }

    _parseJson(data) {
        data = data.split("\n")
        var jsonData = {}
        var indent = 0
        var keyQ = []
        for (let line of data) {
            if (line.trim() == "") { continue }
            var lineIndent = getIndentLevel(line)
            if (line.startsWith("Device")) {
                let dev = line.split(":")[1].trim()
                jsonData[dev] = { "full-path": dev, __proto__: upowerDevice }
                keyQ = [dev]
            } else if (line.startsWith("Daemon")) {
                jsonData["Daemon"] = { __proto__: upowerDevice }
                keyQ = ["Daemon"]
            } else {
                if (lineIndent < indent) {
                    let count = indent - lineIndent
                    for (let popCount = 0; popCount < count; popCount++) { keyQ.pop() }
                }
                let lineSplit = line.split(":")
                let key = lineSplit[0].trim()
                let value = lineSplit.slice(1).join(":")
                if (value == "") {
                    storeData(key.trim(), {}, keyQ, jsonData)
                    keyQ.push(key.trim())
                } else { storeData(key.trim(), value.trim(), keyQ, jsonData) }
            }
            indent = lineIndent
        }
        return jsonData
    }

    polybarPowerLineNBatt() {
        let powerLineStt = this.powerLine.getLinePower()
        let percent = this.coreBatt.percent()
        let color = ColorMan.getColorByPercent(percent, false)
        let delta = []
        let powerIcon = "n/a"
        if (!powerLineStt) {
            let percents = Object.keys(CONF.battIcons)
            for (let p of percents) { delta.push(Math.abs(percent - p)) }
            let minDelta = Math.min(...delta)
            let indexMin = delta.indexOf(minDelta)
            powerIcon = CONF.battIcons[percents[indexMin]]
        } else {
            for (let state in CONF.powerIcons) {
                let icon = CONF.powerIcons[state]
                let battState = this.coreBatt.getChargingStatus()
                if (state.includes(battState) && powerLineStt) { powerIcon = icon; break }
            }
        }

        return `%{F${color.fg}}${powerIcon}%{F-}%{T4} ${percent}%%{T-} `
    }

    findDevice(match) {
        for (let dev of Object.values(this.data)) {
            if (dev.isMatch(match)) { return dev }
        }
    }

    alertCoreBattCrit() {
        let percent = this.coreBatt.percent()
        if (percent <= CONF.battCrit && !this.powerLine.getLinePower()) {
            cp.exec(`notify-send -e -a "Battery stats" "Battery low!!!" "Battery is at ${percent}%, please charge!!!" -u critical`)
        }
    }
    _default() {
        var pbFormat = ""
        let showList = [...CONF.toShow]
        let trackList = [...CONF.toTrack]
        for (let dev of Object.values(this.data)) {
            for (let i of showList) {
                if (dev.isMatch(i.match)) {
                    pbFormat += dev.polybarBatt(i.icon)
                    showList = showList.filter((item) => item !== i)
                }
            }
            for (let criteria of trackList) {
                if (dev.isMatch(criteria)) {
                    trackList = trackList.filter((item) => item !== criteria)
                    dev.tracker().recordPercent(dev.percent())
                    if (dev["power supply"] == "yes") dev.tracker().recordLastPluggedIn()
                }
            }
        }
        pbFormat += this.polybarPowerLineNBatt()
        console.log(pbFormat.trim())
    }
    selectiveDataTrimming() {
        let zenityCmd = 'zenity --list --title "Trimming battery log" --width=600 --height=300 ' +
            '--checklist --text="Select files to trim" --hide-header --column null --column file '
        for (let dev of Object.values(this.data)) {
            if (dev.tracker().dh.isExist()) {
                let file_name = dev.tracker().dh.fileName.split("/")[1]
                zenityCmd += `true "${file_name}" `
            }
        }
        try {
            var toTrimName = cp.execSync(zenityCmd).toString().trim().split("|")
        } catch (error) {
            return
        }
        var toTrimTrackers = []
        for (let dev of Object.values(this.data)) {
            for (let f of toTrimName) {
                if (dev.tracker().dh.fileName.includes(f)) {
                    toTrimTrackers.push(dev.tracker())
                }
            }
        }
        let fromDate = toTrimTrackers[0].findRecentFull()
        for (let i = 1; i < toTrimTrackers.length; i++) {
            let tracker = toTrimTrackers[i]
            let lastFull = tracker.findRecentFull()
            fromDate = lastFull < fromDate ? lastFull : fromDate
        }
        for (let tracker of toTrimTrackers) tracker.trimData()
    }
    test() {
        console.log(JSON.stringify(this.data, null, 3))
    }
}

let myModule = new UPowerWrapper()
myModule.run()
