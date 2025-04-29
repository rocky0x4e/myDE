
const P1 = {
    70: { fg: "#e53238", bg: "#fff" },
    50: { fg: "#ff5555", bg: "#fff" },
    30: { fg: "#feff32", bg: "#000" },
    0: { fg: "#4bec13", bg: "#000" },
}

const P2 = {
    10: { fg: "#FF0000", bg: "#fff" },
    20: { fg: "#FF4000", bg: "#fff" },
    30: { fg: "#ff5555", bg: "#fff" },
    40: { fg: "#D0D017", bg: "#000" },
    80: { fg: "#FFFF33", bg: "#000" },
    100: { fg: "#4bec13", bg: "#000" }
}


const ColorMan = {
    getColorByPercent: function (percent, reverse = true) {
        let percentNum = []
        if (reverse) {
            percentNum = Object.keys(P1)
            percentNum.sort((a, b) => b - a)
            for (let p of percentNum) {
                if (Number(percent) >= Number(p)) { return P1[p] }
            }
        } else {
            percentNum = Object.keys(P2)
            percentNum.sort((a, b) => a - b)
            for (let p of percentNum) {
                if (Number(percent) <= Number(p)) {
                    return P2[p]
                }
            }
        }
    }
}

module.exports = { ColorMan }