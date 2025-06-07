#!/usr/bin/env bash

VCB_TMP=/tmp/vcb_usd_rate.tmp
font=${font:-0}

function VCBRate {
    if ! data=$(curl -s https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx); then
        rateBuy=$(cat $VCB_TMP 2> /dev/null | xmllint --xpath '//*[@CurrencyCode="USD"]/@Buy' - \
        | awk 'match($0, /\s+\w+="(.*)\.[0-9]{2}"/, ary) {print ary[1]}')
        rateBuy=${rateBuy}
    else
        rateBuy=$(echo "$data" | xmllint --xpath '//*[@CurrencyCode="USD"]/@Buy' - \
        2> /dev/null | awk 'match($0, /\s+\w+="(.*)\.[0-9]{2}"/, ary) {print ary[1]}')
        echo "$data" > $VCB_TMP
    fi
    echo -e "%{T${font}}$rateBuy%{T-}"
}

function binanceRate {
    urlSearch="https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    data=$(curl -s -X POST --header 'Content-Type: application/json' \
        --data '{"page": 1, "rows": 10, "asset": "USDT", "tradeType": "SELL",
            "fiat": "VND", "payTypes": ["BankTransferVietnam"], "merchantCheck": true }' \
        $urlSearch | zcat)
    prices=($(echo "$data" | jq '.data[].adv.price' | sort -r))
    LC_NUMERIC="en_US.UTF-8"
    printf "%'d\n" ${prices[0]//\"/}
}

function rofiShowRates {
    data=$(cat $VCB_TMP )
    curCol="<b>Currencies</b>"
    buyCol="<b>Buy</b>"
    selCol="<b>Sell</b>"
    traCol="<b>Transfer</b>"
    l=2

    # currencies=$(echo "$data" | xmllint --xpath '//*/@CurrencyCode' - | cut -d "=" -f2 | sed 's:\"::g')
    # for c in "${currencies[@]}"; do
    for c in CAD USD; do
        ((l++))
        curCol="${curCol}\n${c}"

        buy=$(echo "$data" | xmllint --xpath '//*[@CurrencyCode="'$c'"]/@Buy' - | awk 'match($0, /\s+\w+="(.*)"/, ary) {print ary[1]}')
        buyCol="${buyCol}\n${buy}"

        sel=$(echo "$data" | xmllint --xpath '//*[@CurrencyCode="'$c'"]/@Sell' - | awk 'match($0, /\s+\w+="(.*)"/, ary) {print ary[1]}')
        selCol="${selCol}\n${sel}"

        tra=$(echo "$data" | xmllint --xpath '//*[@CurrencyCode="'$c'"]/@Transfer' - | awk 'match($0, /\s+\w+="(.*)"/, ary) {print ary[1]}')
        traCol="${traCol}\n${tra}"
    done

    curCol="${curCol}\nUSDT (BEX)"
    buyCol="${buyCol}\n$(binanceRate)"
    selCol="${selCol}\n-"
    traCol="${traCol}\n-"

    select=$(echo -e "${curCol}\n${buyCol}\n${selCol}\n${traCol}" | rofi -monitor -3 -markup-rows -dmenu -no-custom -p "USD Rate" \
            -theme overlays/context-menu-right \
            -theme+window+width 70ch \
            -theme+listview+lines $l \
            -theme+listview+columns 4 )
    case $select in
        "USDT (BEX)")
            sensible-browser -new-tab "https://p2p.binance.com/en/trade/sell/USDT?fiat=VND&payment=ALL"
            ;;
    esac
}

$1