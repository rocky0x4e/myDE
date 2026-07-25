#!/usr/bin/env node

const cp = require("node:child_process")
const { MultiBLocksModule } = require("../libjs/Polybar")

const DEX_DIR = "/usr/share/applications"
const baseBrowser = {
    foregr: "#fff",
    backgr: ""
}

let CONF = {
    findBy(key, value) {
        for (let item of this.browsers) if (value.includes(item[key])) return item
    },
    browsers: [
        {
            xdgName: "brave-browser.desktop",
            name: "Brave",
            processName: "brave-browser",
            wmclass: "Brave-browser",
            icon: "\ue572",
            appIcon: "\\0icon\\x1fbrave",
            __proto__: baseBrowser
        },
        {
            xdgName: "google-chrome.desktop",
            name: "Chrome",
            processName: "^chrome$",
            wmclass: "Google-chrome",
            icon: "\uf268",
            appIcon: "\\0icon\\x1fgoogle-chrome",
            __proto__: baseBrowser
        },
        {
            xdgName: "opera.desktop",
            name: "Opera",
            processName: "^opera$",
            wmclass: "Opera",
            icon: "\uf26a",
            appIcon: "\\0icon\\x1fopera",
            __proto__: baseBrowser
        },
        {
            xdgName: "firefox.desktop",
            name: "Firefox",
            processName: "^firefox-bin$",
            wmclass: "firefox",
            icon: "\uf269",
            appIcon: "\\0icon\\x1ffirefox",
            __proto__: baseBrowser
        }
    ],
    notificationTimeout: 2500
}

const ROFI_COMMON_CONF = "-hover-select -theme+inputbar+children '[ prompt ]' " +
    `-theme+listview+lines ${CONF.browsers.length} -theme overlays/context-menu-left -monitor -3`

class App extends MultiBLocksModule {

    constructor() {
        super()
        let xdgName = cp.execSync("xdg-settings get default-web-browser").toString().trim()
        this.current = CONF.findBy("xdgName", xdgName)
    }

    getNext(direction = "next") {
        if (direction != "next") {
            CONF.browsers.reverse()
        }
        const len = CONF.browsers.length
        let first = CONF.browsers[0]
        for (let index = 0; index < len; index++) {
            let obj = CONF.browsers[index]
            if (this.current.xdgName == obj.xdgName) {
                if (index != len - 1) return CONF.browsers[index + 1]
            }
        }
        return first
    }

    async switchBrowser(direction = "next") {
        let next = this.getNext(direction)
        cp.exec(`notify-send -e "Default browser ${this.current.name} -> ${next.name}" -t ${CONF.notificationTimeout}`)
        cp.execSync(`xdg-settings set default-web-browser ${next.xdgName}`)
        this.current = next
    }

    _default() {
        // console.log(`%{B${this.current.backgr}}%{F${this.current.foregr || "#fff"}}${this.current.icon}%{F-}%{B-}`)
        console.log(`${this.current.icon}`)
    }

    open(browser = null) {
        var isRunning
        if (browser == null) { browser = this.current }
        try {
            isRunning = cp.execSync(`pgrep ${browser.processName}`).toString().trim()
        } catch (error) {
            isRunning = ""
        }
        if (isRunning) {
            cp.exec(`notify-send -e -t ${CONF.notificationTimeout} "Focusing ${browser.name}"`)
            cp.exec(`i3-msg -q "[class=\"${browser.wmclass}\"] focus"`)
        } else {
            cp.exec(`dex ${DEX_DIR}/${browser.xdgName}`)
            cp.exec(`notify-send -e -t ${CONF.notificationTimeout} "Launched ${browser.name}"`)
            process.exit(0)
        }
    }

    rofiOpen() {
        let brList = ""
        for (let br of CONF.browsers) {
            brList += `${br.name}${br.appIcon}\n`
        }
        let rofiCmd = `echo -en "${brList.trim()}" | rofi -show-icons -dmenu -no-custom -p "Open browser" ` +
            ROFI_COMMON_CONF + `-select "${this.current.name}"`
        try {
            let selected = cp.execSync(rofiCmd, { shell: "/bin/bash" }).toString().trim()
            selected = CONF.findBy("name", selected)
            this.open(selected)
        } catch (error) { console.log(error) }
    }

    selectBrowser() {
        if (process.argv[3] != undefined) {
            let name = process.argv[3]
            let br = this.current = CONF.findBy("name", name)
            cp.exec(`notify-send -e "Default browser ${this.current.name} -> ${br.name}" -t ${CONF.notificationTimeout}`)
            cp.execSync(`xdg-settings set default-web-browser ${br.xdgName}`)
            this.current = br
        } else {
            let brList = ""
            for (let br of CONF.browsers) {
                brList += `${br.name}${br.appIcon}\n`
            }
            let rofiCmd = `echo -en "${brList.trim()}" | rofi -show-icons -dmenu -no-custom -p "Select a default browser" ` +
                ROFI_COMMON_CONF + `-select "${this.current.name}"`
            try {
                let selected = cp.execSync(rofiCmd, { shell: "/bin/bash" }).toString().trim()
                if (selected == this.current.name) { return }
                selected = CONF.findBy("name", selected)
                cp.exec(`notify-send -e "Default browser ${this.current.name} -> ${selected.name}" -t ${CONF.notificationTimeout}`)
                cp.execSync(`xdg-settings set default-web-browser ${selected.xdgName}`)
                this.current = selected
            } catch (error) { console.log(error) }
        }
    }
}

let app = new App()
app.run()
