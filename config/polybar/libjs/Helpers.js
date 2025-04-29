const fs = require("fs");
const cp = require("node:child_process")

class DataHelper {
    static DATA_DIR = `${process.env.HOME}/.config/polybar/data`

    constructor(dataFileName, needLock = false) {
        this.fileName = dataFileName.endsWith(".json") ? dataFileName : `${dataFileName}.json`
        this.fileFull = `${DataHelper.DATA_DIR}/${this.fileName}`
        this.lockFile = `${this.fileFull}.lock`
        this.needLock = needLock
    }

    async lock() {
        if (!this.needLock) {
            return
        }
        let MaxWait = 10000
        while (fs.existsSync(this.lockFile)) {
            await new Promise(resolve => setTimeout(resolve, 300))
            MaxWait -= 300
            if (MaxWait < 0) {
                process.exit(1)
            }
        }
        fs.writeFileSync(this.lockFile, "")
    }

    unlock() {
        try { fs.unlinkSync(this.lockFile) }
        catch (e) { }
    }

    readJsonData() {
        var data
        try { data = require(this.fileFull) }
        catch { data = {} }
        this.unlock()
        return data
    }

    async writeJsonData(data) {
        await this.lock()
        fs.writeFileSync(this.fileFull, JSON.stringify(data, null, 3))
        this.unlock()
    }

    remove() {
        fs.unlinkSync(this.fileFull)
    }

    static list(subDir = "") { return fs.readdirSync(DataHelper.DATA_DIR + subDir) }
    isExist() {
        return fs.existsSync(this.fileFull)
    }
}

class BatteryTracker {
    constructor(file) {
        this.dh = new DataHelper(file)
    }
    recordLastPluggedIn() {
        let data = this.dh.readJsonData()
        data.pluggedIn = new Date()
        this.dh.writeJsonData(data)
    }
    recordPercent(percent = 0) {
        if (percent == null) return
        let data = this.dh.readJsonData()
        let history = data.history || {}
        let now = (new Date()).toISOString()
        let historyLen = Object.keys(history).length
        let dates = Object.keys(history).map(d => new Date(d))
        dates.sort((a, b) => new Date(b) - new Date(a))
        if (historyLen > 1) {
            let latest0 = dates[0].toISOString()
            let latest1 = (dates[1] || now).toISOString()
            let lastPercent0 = history[latest0]
            let lastPercent1 = history[latest1] || -1

            if ((percent != lastPercent0 && percent != lastPercent1) || (percent == lastPercent0 && lastPercent0 != lastPercent1)) {
                history[now] = Number(percent)
                this.dh.writeJsonData(data)
            } else if (percent == lastPercent0 && lastPercent0 == lastPercent1) {
                delete history[latest0]
                history[now] = percent
            }
        } else {
            history[now] = percent
            data.history = history
            this.dh.writeJsonData(data)
        }
    }

    trimData(fromDate = undefined) {
        if (!this.dh.isExist()) return
        var data = this.dh.readJsonData()

        let newData = { ...data },
            newHistory = {},
            history = data.history,
            dates = Object.keys(history)
        fromDate = fromDate || data.pluggedIn || this.findRecentFull()
        for (let d of dates) {
            if (new Date(d) < new Date(fromDate)) continue;
            let value = history[d]
            newHistory[d] = value
            newHistory[d] = value
        }
        newData.history = newHistory
        this.dh.writeJsonData(newData)
        cp.exec(`dunstify "Trimming data file: ${this.dh.fileName}" -t 3000`)
    }

    findRecentFull() {
        var data = this.dh.readJsonData().history,
            dates = Object.keys(data)
        dates.sort(function (a, b) { return new Date(b) - new Date(a) })
        for (let d of dates) { if (data[d] >= 100) return d }
        return dates.pop()
    }
}

module.exports = { DataHelper, BatteryTracker }