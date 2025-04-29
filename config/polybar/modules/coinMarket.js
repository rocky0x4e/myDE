#!/usr/bin/env node

const { MultiBLocksModule } = require("../libjs/Polybar")
const cp = require("node:child_process")
/*
    oldPrvUsdt: {
        id: '0000000000000000000000000000000000000000000000000000000000000004-' +
            '076a4423fa20922526bd50b0d7b0dc1c593ce16e15ba141ede5fb5a28aa3f229-' +
            '33a8ceae6db677d9860a6731de1a01de7e1ca7930404d7ec9ef5028f226f1633',
        t1: "PRV",
        t2: "USDT"
    },
    newPrvUsdt: {
        id: '0000000000000000000000000000000000000000000000000000000000000004-' +
            '076a4423fa20922526bd50b0d7b0dc1c593ce16e15ba141ede5fb5a28aa3f229-' +
            'c8011262f3c7c173df1dea02370824460d15e5f473142a4709fd091c91969e2d',
        t1: "PRV",
        t2: "USDT"
    },
    newPrvUsdc: {
        id: '0000000000000000000000000000000000000000000000000000000000000004-' +
            '545ef6e26d4d428b16117523935b6be85ec0a63e8c2afeb0162315eb0ce3d151-' +
            'bb374ab5500e6cf3a12fabf8afe634fb1f254c11f04cc121b8a6625f106efce9',
        t1: "PRV",
        t2: "USDC"
    }
*/
const PRV = {
    t1: "PRV", t2: "USDT",
    poolId: '0000000000000000000000000000000000000000000000000000000000000004-' +
        '076a4423fa20922526bd50b0d7b0dc1c593ce16e15ba141ede5fb5a28aa3f229-' +
        'c8011262f3c7c173df1dea02370824460d15e5f473142a4709fd091c91969e2d',
    fullnode: new URL('https://rocky-0x4e.sytes.net/fn'),
    payloadBlkInfo: JSON.stringify({
        "id": 1,
        "jsonrpc": "1.0",
        "method": "getblockchaininfo",
        "params": null
    })
},
    HEADERS = { 'Content-Type': 'application/json' },
    BNB = {
        payload: {
            "page": 1,
            "rows": 10,
            "asset": "USDT",
            "tradeType": "SELL",
            "fiat": "VND",
            "payTypes": ["BankTransferVietnam"],
            "merchantCheck": true
        },
        urlSearch: "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
        urlTrade: "https://p2p.binance.com/en/trade/sell/USDT?fiat=VND&payment=ALL",
        notificationInterval: 15,  // second
        notificationTitle: "USDT-VND P2P",
        bigFib: 13,
        maxNotiCount: 20,
        goodRate: process.env.GOOD_RATE || 24500,
        color: {
            high: { fg: "#F72C5B", bg: "#519548" },
            normal: { fg: "", bg: "" },
        }
    }


function nextFibonacci(num) {
    if (num <= 0) { return 1 }
    if (num == 1) { return 2 }
    if (num == 2) { return 3 }
    let first = second = 1
    let f = first + second
    while (f <= num) {
        first = second
        second = f
        f = first + second
    }
    return f
}


class MyModule extends MultiBLocksModule {
    constructor() {
        super()
        this.blocks = ["prv", "bnb"]
        this.getModuleConf()
    }
    async fetchPRVPool() {
        this.prv = []
        this.prv.data = undefined
        try {


            let f = await (async () =>
                fetch(PRV.fullnode, {
                    method: "POST",
                    headers: HEADERS,
                    body: PRV.payloadBlkInfo,
                    keepalive: true
                }).then(res => res.json()
                ).then(json => json.Result.BestBlocks["-1"].Height
                ).then(beaconH => {
                    return JSON.stringify({
                        "id": 1, "jsonrpc": "1.0", "method": "pdexv3_getState", "params": [
                            {
                                "BeaconHeight": beaconH,
                                "Filter": {
                                    "Key": "PoolPair",
                                    "Verbosity": 1,
                                    "ID": PRV.poolId
                                }
                            }]
                    })
                }).then(PAYLOAD_pdeInfo => {
                    return fetch(PRV.fullnode, {
                        method: "POST",
                        headers: HEADERS,
                        body: PAYLOAD_pdeInfo,
                        keepalive: true
                    })
                }).then(res => res.json()
                ).then(data => {
                    this.prv.data = data["Result"]
                    let pool_info = this.prv.data.PoolPairs[PRV.poolId]
                    this.prv.v_pool_usdt = pool_info.State.Token1VirtualAmount
                    this.prv.v_pool_prv = pool_info.State.Token0VirtualAmount
                    this.prv.r_pool_usdt = pool_info.State.Token1RealAmount
                    this.prv.r_pool_prv = pool_info.State.Token0RealAmount
                    this.prv.amp = pool_info.State.Amplifier
                    this.prv.price = (this.prv.v_pool_usdt / this.prv.v_pool_prv).toFixed(4)
                    this.prv.infoVerbose = `Rate: ${this.prv.price} | AMP: ${this.prv.amp / 1e4}\n` +
                        `RPool: ${(this.prv.r_pool_prv / 1e9).toFixed(4)} | ${(this.prv.r_pool_usdt / 1e9).toFixed(4)}\n` +
                        `VPool: ${(this.prv.v_pool_prv / 1e9).toFixed(4)} | ${(this.prv.v_pool_usdt / 1e9).toFixed(4)}`
                })
            )();
        } catch (error) {
            this.prv.price = error.message
        }
    }
    async showPoolInfo() {
        await this.fetchPRVPool()
        cp.exec(`dunstify -t 8000 "${PRV.t1}-${PRV.t2}" "${this.prv.infoVerbose}"`)
    }

    async showOrderBook() {
        await this.fetchPRVPool()
        let zenity = 'zenity --list --title "Order book" --width 600 --height 600'
            + ' --column="Order" --column="Amount"'
            + ' --column="Rate" --column="Filled Amount" --column="Filled %" '
        let orders = this.prv.data.PoolPairs[PRV.poolId].Orderbook.orders,
            sell = [],
            buy = []
        for (let order of orders) {
            let direction = order.TradeDirection,
                amount0 = order.Token0Rate,
                amount1 = order.Token1Rate,
                balance0 = order.Token0Balance,
                balance1 = order.Token1Balance,
                rate = (amount1 / amount0).toFixed(4)
            if (direction == 1) {
                let fr = `${amount1 / 1e6} USDT`,
                    to = `${amount0 / 1e9} PRV`,
                    filled_amt = balance0 / 1e9,
                    filled = balance0 / amount0 * 100
                buy.push([to, rate, filled_amt, filled])
            } else {
                let fr = `${amount0 / 1e9} PRV`,
                    to = `${amount1 / 1e6} USDT`,
                    filled_amt = balance1 / 1e6,
                    filled = balance1 / amount1 * 100
                sell.push([fr, rate, filled_amt, filled])
            }
        }
        for (let o of sell) zenity += `Sell "${o[0]}" "${o[1]}" "${o[2]}" "${o[3]}" `
        for (let o of buy) zenity += `Buy "${o[0]}" "${o[1]}" "${o[2]}" "${o[3]}" `
        cp.exec(zenity)
    }
    async getPrvPrice() {
        await this.fetchPRVPool()
        return `%{A1:${process.argv[1]} showOrderBook:}%{A} %{A:${process.argv[1]} showPoolInfo:}${this.prv.price}%{A} `
    }

    // BNB part
    async fetchBnbAds() {
        this.bnb = {}
        try {
            await fetch(BNB.urlSearch, {
                method: "POST",
                headers: HEADERS,
                body: JSON.stringify(BNB.payload),
                keepalive: true
            }).then(response => response.json())
                .then(result => {
                    this.bnb.adsAll = result.data
                    this.bnb.adsAll.sort((a, b) => b['adv']['price'] - a['adv']['price'])
                    this.bnb.rateBest = this.bnb.adsAll[0]['adv']['price']
                    this.bnb.rate2nd = this.bnb.adsAll[1]['adv']['price']
                })

        } catch (error) { process.exit() }
    }
    async notifyUSDTBestRate() {
        if (!this.config.notificationEnable) { return }
        let now = new Date()
        let lastNotified = new Date(this.config.lastNotified)
        if (this.bnb.rateBest > BNB.goodRate) {
            if (this.bnb.rate2nd <= BNB.goodRate || now.getDay() != lastNotified.getDay()) {
                //  reset count for a new day
                // this.config.fibonacci = 0
                this.config.notificationCount = 0
                this.writeConfig()
            }
            let deltaTime = (now - lastNotified) / 1000
            if (this.bnb.rate2nd > BNB.goodRate && deltaTime >= BNB.notificationInterval * this.config.fibonacci
                && this.config.notificationCount <= BNB.maxNotiCount) {
                this.config.lastNotified = now.toISOString()
                cp.execSync(`dunstify -r 119257128 "(${this.config.fibonacci}-${this.config.notificationCount})` +
                    ` USD rate is high: ${this.bnb.rateBest}" '<a href=\"${BNB.urlTrade}\"> Holly Molly!!! Wanna swap???</a>'`)
                this.config.notificationCount += 1
                this.config.fibonacci = this.config.fibonacci >= BNB.bigFib ? BNB.bigFib : nextFibonacci(this.config.fibonacci)
                this.writeConfig()
            }
        }
    }
    async getUSDTPrice() {
        await this.fetchBnbAds()
        let range = this.bnb.rateBest > BNB.goodRate ? "high" : "normal"
        let color = BNB.color[range]
        let rate = Number(this.bnb.rateBest).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            currency: "VND",
            style: "currency"
        })
        return `%{F${color.fg}}%{A1:${process.argv[1]} show10:}${rate}%{A}%{F-} `
    }
    async show10() {
        await this.fetchBnbAds()
        const S = ""  // column separator
        let data = []
        let max0 = 5,
            max1 = 6
        for (let item of this.bnb.adsAll) {
            let price = Number(item.adv.price).toLocaleString('en-US', {
                minimumFractionDigits: 0
            }),
                amount = Number(item.adv.minSingleTransAmount).toLocaleString('en-US', {
                    minimumFractionDigits: 0
                })
            data.push([price, amount])
            max0 = price.length > max0 ? price.length : max0
            max1 = amount.length > max1 ? amount.length : max1
        }
        let prices = `<span weight='bold' color='#FF5E00'>  # ${S} ${"Price".padStart(max0)} ${S} ${"Amount".padStart(max1)}</span>`
        let c = 1
        for (let item of data) {
            prices += `\n ${String(c).padStart(2)} ${S} ${item[0].padStart(max0)} ${S} ${item[1].padStart(max1)}`
            c++
        }
        cp.exec(`dunstify "${BNB.notificationTitle}" "${prices}"`)
    }
    toggleNotificationSetting() {
        this.config.notificationEnable = !this.config.notificationEnable
        this.writeConfig()
        cp.exec(`dunstify "${this.name}" "Notification enable: ${this.config.notificationEnable}"`)
    }
    async _default() {
        let blocksConf = this.getBlockConf()
        let usdtPrice = await this.getUSDTPrice()
        this.notifyUSDTBestRate()

        for (let blk in blocksConf) {
            let blkConf = blocksConf[blk]
            if (blkConf)
                switch (blk) {
                    case "prv":
                        this.toPrint += await this.getPrvPrice()
                        break;
                    case "bnb":
                        this.toPrint += usdtPrice
                        break;
                }
        }
        this.labelIcon = ""
        this.labelAction = { 1: "enableBlocks" }
        this.printModule({ showLabelAlways: true })
        process.exit(0)
    }
    async showRateDunstify() {
        // await this.getPrvPrice()
        await this.getUSDTPrice()
        let usdtRate = Number(this.bnb.rateBest).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            currency: "VND",
            style: "currency"
        })
        // let ratePrv = Number(this.prv.price).toLocaleString('en-US', {
        //     minimumFractionDigits: 4,
        //     currency: "USD",
        //     style: "currency"
        // })
        cp.exec(`dunstify "Coins rate" 'USDT: ${usdtRate}'`)
    }
}

let mm = new MyModule()
mm.run()