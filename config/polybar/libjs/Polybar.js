#!/usr/bin/env node

const { DataHelper } = require("./Helpers")
const cp = require("node:child_process")

class MultiBLocksModule {
    Z_TITLE = "Multi-blocks module config"
    constructor(name = process.argv[1]) {
        this.name = name.split("/").pop().split(".")[0]
        this.blocks = []
        this.toPrint = ""
        this.labelIcon = this.name + ": set emptyIcon be4 printing module"
        this.labelAction = { 3: "enableBlocks" }
    }
    getModuleConf() {
        if (typeof this.config == "object") return this.config
        this.config = polybarControl.readModuleConf(this.name)
        return this.config
    }
    printModule(opt = {}) {
        let showLabelAlways = opt.showLabelAlways || false
        let defaultActions = { 3: "enableBlocks" }
        this.labelAction = { ...defaultActions, ...this.labelAction }
        for (let button in this.labelAction) {
            let action = this.labelAction[button]
            var label = `%{A${button}:${process.argv[1]} ${action}:}${this.labelIcon}%{A}`
        }
        this.toPrint = showLabelAlways ? label + this.toPrint : this.toPrint || label
        console.log(this.toPrint.trim())
    }
    getBlockConf() {
        let blockConf = this.config.blockConf
        if (blockConf == undefined || blockConf.length == 0 || typeof blockConf != "object") {
            let result = {}
            for (let item of this.blocks) { result[item] = false }
            this.config.blockConf = result
            return result
        }
        return blockConf
    }
    writeConfig() { polybarControl.writeModuleConf(this.name, this.config) }
    _default() { console.log(this.name, "_default") }
    show() { cp.exec(`polybar-msg action ${this.name} module_show`) }
    hide() { cp.exec(`polybar-msg action ${this.name} module_hide`) }
    toggle() { cp.exec(`polybar-msg action ${this.name} module_toggle`) }
    disable() {
        this.config.enable = false
        this.writeConfig()
        this.hide()
        let msg = (this.config.runWhileHidden) ? "Hide module" : "Disable module"
        cp.exec(`dunstify "${msg}" "${this.name}"`)
    }
    enable() {
        this.config.enable = true
        this.writeConfig()
        this.show()
        cp.exec(`dunstify "Enable module" "${this.name}"`)
    }
    toggleFunctional() {
        console.log(this.isEnable())
        if (this.isEnable()) this.disable()
        else this.enable()
    }
    isEnable() {
        if (this.config == undefined) { return false }
        if (typeof this.config.enable == "boolean") return this.config.enable
        else return false
    }
    run(input = process.argv[2]) {
        input = input || "_default"
        if (this.config != undefined && !this.config.runWhileHidden && !this.config.enable && input == "main") return
        try {
            this[input]()
        } catch (err) {
            if (err.name == "TypeError" && err.message == "this[input] is not a function")
                console.log(`!!! ERROR: Function/method "${input}" is not existed!\n   (${err.message})`)
            else { throw err }
        }
        // process.exit(0)
    }
    selectBlock() {
        const fs = require("fs");
        const { flockSync } = require('fs-ext');
        const fd = fs.openSync('/tmp/polybar_mm_config.lock', 'w');
        try {
            flockSync(fd, 'exnb')
        } catch (err) {
            cp.execSync(`i3-msg '[title="${this.Z_TITLE}"] kill'`)
            flockSync(fd, 'ex')
        }
        let blocksConf = this.getBlockConf()
        let zenityCheckList = ''
        for (let block in blocksConf) { zenityCheckList += `${blocksConf[block]} ${block} ` }
        try {
            var selected = cp.execSync(
                `zenity --list --title "${this.Z_TITLE}" ` +
                `--checklist --text="${this.name}: Select blocks" --hide-header --column null --column Blocks ` +
                zenityCheckList).toString().trim().split("|")
        } catch (error) { return }
        selected = selected == "" ? [] : selected
        for (let item of Object.keys(blocksConf)) { this.config.blockConf[item] = false }
        this.enableBlocks(selected)
        this.writeConfig()
    }
    enableBlocks(blocks) {
        let enabling = {}
        let blocksConf = this.getBlockConf()
        blocks = blocks ? blocks : Object.keys(blocksConf)
        console.log(blocks)
        for (let blk of blocks) {
            this.config.blockConf[blk] = !this.config.blockConf[blk]
            enabling[blk] = this.config.blockConf[blk]
        }
        cp.exec(`dunstify 'Multi-Blocks Module: ${this.name}' 'Block visibility toggle:\n${JSON.stringify(enabling, null, 3)}'`)
        this.writeConfig()
    }
    disableBlocks() {
        let blocksConf = this.getBlockConf()
        for (let blk in blocksConf) this.config.blockConf[blk] = false
        this.writeConfig()
    }
    toggleBlocks() {

    }
}

const polybarControl = {
    dh: new DataHelper("polybar", true),
    readModuleConf: (moduleName) => {
        let settings = polybarControl.dh.readJsonData()
        var moduleSetting = settings[moduleName]
        return moduleSetting ? moduleSetting : { enable: true, runWhileHidden: false }
    },
    writeModuleConf: (moduleName, setting) => {
        let settings = polybarControl.dh.readJsonData()
        settings[moduleName] = setting
        polybarControl.dh.writeJsonData(settings)
    },
    mbmConfig: () => {
        let settings = polybarControl.dh.readJsonData()
        let modules = Object.keys(settings)

    }
}

module.exports = { MultiBLocksModule }