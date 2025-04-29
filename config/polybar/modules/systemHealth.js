#!/usr/bin/env node

const cp = require("node:child_process")
const fs = require('fs')
const { ColorMan } = require("../libjs/ColorManager")
const { MultiBLocksModule } = require("../libjs/Polybar")

const ACTIONS = {
    cpu: "i3-toggle-window.sh 'title=\"System Monitor\"' gnome-system-monitor",
    mem: "rofi-show-ram.sh",
    temp: 'dunstify "$(sensors -A)"',
}
class MyModule extends MultiBLocksModule {
    constructor() {
        super()
        this.getModuleConf()
        this.blocks = ["cpu", "mem", "temp"]
    }


    async getStat() {
        this.cpuBlk = this.memBlk = this.tmpBlk = ""
        let blkConf = this.getBlockConf()
        for (let blk in blkConf) {
            if (blkConf[blk]) {
                switch (blk) {
                    case "cpu":
                        new Promise((resolve, reject) => {
                            let mpStat = cp.execSync("mpstat 1 1").toString().trim()
                            let avgStat = mpStat.split("\n").pop().trim()
                            let idle = avgStat.split(" ").pop().replace(',', '.')
                            let cpu = 100 - idle
                            let color = ColorMan.getColorByPercent(cpu)
                            let cpuBlk = `%{A1:${ACTIONS.cpu}:}%{F${color.fg}}%{F-}%{A}%{T4} ${cpu.toFixed(1)}%%{T-} `
                            resolve(cpuBlk)
                        }).then(result => this.toPrint += result); break;
                    case "mem":
                        new Promise((resolve, reject) => {
                            let memInfo = fs.readFileSync("/proc/meminfo", 'utf8').toString().split("\n")
                            let memData = {}
                            for (let i = 0; i < 6; i++) {
                                let line = memInfo[i].split(":")
                                memData[line[0]] = line[1].trim().split(" ")[0]
                            }
                            let used = (1 - (memData.MemTotal - memData.Cached - memData.Buffers) / memData.MemTotal) * 100
                            let color = ColorMan.getColorByPercent(used)
                            resolve(`%{A1:${ACTIONS.mem}:}%{F${color.fg}}%{F-}%{A}%{T4} ${used.toFixed(1)}%%{T-} `)
                        }).then(result => this.toPrint += result); break;
                    case "temp":
                        new Promise((resolve, reject) => {
                            let sensors = JSON.parse(cp.execSync("sensors -j").toString())
                            let cpuTemp = sensors["amdgpu-pci-0400"]["edge"]["temp1_input"]
                            let color = ColorMan.getColorByPercent(cpuTemp)
                            resolve(`%{A1:${ACTIONS.temp}:}%{F${color.fg}}%{F-}%{A}%{T4} ${cpuTemp.toFixed(0)}C%{T-} `)

                        }).then(result => this.toPrint += result); break;
                    default:
                        break;
                }
            }
        }
    }
    async _default() {
        await this.getStat()
        this.labelIcon = ""
        this.printModule()
    }
}
const mm = new MyModule()
mm.run()


