# Cookie PnL — Cookie Chain cApp

Live-ready web app for the Superteam bounty **Create an App on Cookie Chain** (1,000 USDC pool, due 2026-09-22).

## What it does

- Connects **Nightly** (required by the bounty)
- Shows COOK balance, slot, genesis, recent signatures
- Sends a real **on-chain memo ping** and links the tx on [Cookiescan](https://cookiescan.io)
- Proxies RPC locally because `rpc.cookiescan.io` currently has an expired TLS certificate

## Run

```powershell
python C:\Users\Pato\mooltbok\products\cookie-capp\server.py
```

Open http://127.0.0.1:8787/

Public demo (while this PC is on): https://info-magazines-dates-jewish.trycloudflare.com

## Submit on Superteam

Listing: https://superteam.fun/earn/listing/create-an-app-on-cookie-chain-app/

Need a Superteam login (human-only listing). After the live URL is up:

1. Live application URL (cloudflare tunnel or GitHub Pages + proxy)
2. GitHub repo with this folder
3. Program: SPL Memo `MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr`
4. X thread + share in https://t.me/TheCookieNetChain

Nightly: https://nightly.app/  
Bridge COOK for fees: https://bridge.cookiescan.io
