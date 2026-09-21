const RPC_DIRECT = "https://rpc.cookiescan.io";
const RPC_PROXY = "/rpc";
const EXPLORER = "https://cookiescan.io";
const MEMO_PROGRAM = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr";
const GENESIS = "9wDaBRDgArEUpvhHxGguNkwozsZh4UpGZB9o2EoEcBB2";
const COOK_MINT = "So11111111111111111111111111111111111111112";
const BCOOK_MINT = "EkPafx58mgwkEnGwo62jXhXDAdJ37Z8G8MFBRPsr9uhz";

const $ = (id) => document.getElementById(id);
const state = {
  rpc: RPC_PROXY,
  connection: null,
  provider: null,
  publicKey: null,
};

function setStatus(text, ok) {
  const el = $("status");
  el.textContent = text;
  el.className = "status " + (ok === true ? "good" : ok === false ? "bad" : "");
}

async function rpcCall(method, params, rpcUrl) {
  const url = rpcUrl || state.rpc;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params: params || [] }),
  });
  const body = await res.json();
  if (body.error) throw new Error(body.error.message || JSON.stringify(body.error));
  return body.result;
}

async function pickRpc() {
  try {
    const health = await rpcCall("getHealth", [], RPC_PROXY);
    if (health === "ok") {
      state.rpc = RPC_PROXY;
      return "proxy";
    }
  } catch (_) {
    /* fall through to direct RPC */
  }
  const health = await rpcCall("getHealth", [], RPC_DIRECT);
  if (health !== "ok") throw new Error("Cookie Chain RPC no responde");
  state.rpc = RPC_DIRECT;
  return "direct";
}

function getNightly() {
  const n = window.nightly && window.nightly.solana;
  if (n) return n;
  if (window.nightlySolana) return window.nightlySolana;
  return null;
}

function lamportsToCook(lamports) {
  return (Number(lamports) / 1e9).toFixed(6);
}

function shortAddr(addr) {
  if (!addr) return "—";
  return addr.slice(0, 4) + "…" + addr.slice(-4);
}

async function refreshChain() {
  const [slot, genesis, version] = await Promise.all([
    rpcCall("getSlot"),
    rpcCall("getGenesisHash"),
    rpcCall("getVersion"),
  ]);
  $("kpiSlot").textContent = String(slot);
  $("kpiGenesis").textContent = genesis === GENESIS ? "Cookie Chain" : genesis;
  $("kpiVersion").textContent = (version && version["solana-core"]) || "—";
  if (genesis !== GENESIS) {
    setStatus("Genesis inesperado: " + genesis, false);
  }
}

async function refreshWallet() {
  if (!state.publicKey) return;
  const pubkey = state.publicKey.toString();
  $("kpiWallet").textContent = shortAddr(pubkey);
  $("walletFull").textContent = pubkey;
  $("walletFull").href = EXPLORER + "/account/" + pubkey;

  const bal = await rpcCall("getBalance", [pubkey]);
  const lamports = typeof bal === "object" ? bal.value : bal;
  $("kpiBal").textContent = lamportsToCook(lamports) + " COOK";

  const sigs = await rpcCall("getSignaturesForAddress", [pubkey, { limit: 12 }]);
  const rows = (sigs || [])
    .map((s) => {
      const sig = s.signature;
      const err = s.err ? "error" : "ok";
      const when = s.blockTime ? new Date(s.blockTime * 1000).toISOString() : "pending";
      return `<tr><td class="mono"><a href="${EXPLORER}/tx/${sig}" target="_blank" rel="noopener">${sig.slice(0, 12)}…</a></td><td>${err}</td><td>${s.slot || "—"}</td><td>${when}</td></tr>`;
    })
    .join("");
  $("txBody").innerHTML = rows || "<tr><td colspan='4'>Sin transacciones todavía. Mandá un ping on-chain.</td></tr>";
  $("kpiTx").textContent = String((sigs || []).length) + (sigs && sigs.length === 12 ? "+" : "");
}

async function connectWallet() {
  const provider = getNightly();
  if (!provider) {
    setStatus("Instalá Nightly y recargá. Es el wallet requerido por el bounty.", false);
    window.open("https://nightly.app/", "_blank", "noopener");
    return;
  }
  state.provider = provider;
  const res = await provider.connect();
  const key =
    (res && res.publicKey) ||
    provider.publicKey ||
    (res && res.address);
  if (!key) throw new Error("Nightly no devolvió publicKey");
  state.publicKey = window.solanaWeb3.PublicKey
    ? new window.solanaWeb3.PublicKey(key.toString ? key.toString() : key)
    : key;
  $("btnPing").disabled = false;
  setStatus("Wallet conectada. Red: Cookie Chain (" + state.rpc + ")", true);
  await refreshWallet();
}

async function pingOnchain() {
  if (!state.provider || !state.publicKey) throw new Error("Conectá Nightly primero");
  const web3 = window.solanaWeb3;
  const connection = new web3.Connection(
    state.rpc === RPC_PROXY ? window.location.origin + RPC_PROXY : RPC_DIRECT,
    "confirmed"
  );
  const memo = new web3.TransactionInstruction({
    keys: [{ pubkey: state.publicKey, isSigner: true, isWritable: false }],
    programId: new web3.PublicKey(MEMO_PROGRAM),
    data: new TextEncoder().encode("CookiePnL ping " + new Date().toISOString()),
  });
  const tx = new web3.Transaction().add(memo);
  tx.feePayer = state.publicKey;
  const latest = await connection.getLatestBlockhash();
  tx.recentBlockhash = latest.blockhash;

  let signature;
  if (typeof state.provider.signAndSendTransaction === "function") {
    const sent = await state.provider.signAndSendTransaction(tx);
    signature = typeof sent === "string" ? sent : sent.signature || sent;
  } else {
    const signed = await state.provider.signTransaction(tx);
    signature = await connection.sendRawTransaction(signed.serialize());
  }
  setStatus("Tx enviada: " + signature, true);
  $("lastSig").innerHTML = `<a href="${EXPLORER}/tx/${signature}" target="_blank" rel="noopener">${signature}</a>`;
  await connection.confirmTransaction({ signature, ...latest }, "confirmed");
  await refreshWallet();
}

async function refreshMarkets() {
  const res = await fetch("/api/markets");
  const data = await res.json();
  const rows = Array.isArray(data) ? data : data.data || [];
  const cook = rows.find((t) => (t.symbol || "").toUpperCase() === "COOK" || t.mint === COOK_MINT);
  if (cook && cook.price) $("kpiCookUsd").textContent = "$" + Number(cook.price).toPrecision(4);
  const top = rows
    .slice()
    .sort((a, b) => Number(b.marketCap || 0) - Number(a.marketCap || 0))
    .slice(0, 8);
  $("mktBody").innerHTML = top
    .map((t) => {
      const mint = t.mint || "";
      return `<tr><td>${t.symbol || t.name || "—"}</td><td>${t.price != null ? Number(t.price).toPrecision(4) : "—"}</td><td>${t.marketCap != null ? Number(t.marketCap).toLocaleString() : "—"}</td><td class="mono"><a href="${EXPLORER}/token/${mint}" target="_blank" rel="noopener">${mint.slice(0, 8)}…</a></td></tr>`;
    })
    .join("") || "<tr><td colspan='4'>No markets</td></tr>";
}

async function refreshQuote() {
  const qs =
    "/api/quote?inputMint=" +
    COOK_MINT +
    "&outputMint=" +
    BCOOK_MINT +
    "&amount=1000000000&slippageBps=500";
  const res = await fetch(qs);
  const data = await res.json();
  const route = data.route || data;
  if (!route || !route.netOutAmount) throw new Error(data.error || "sin ruta Cookiebox");
  const out = Number(route.netOutAmount) / 1e9;
  $("kpiQuote").textContent = out.toFixed(6) + " bCOOK";
  const hop = (route.segments && route.segments[0]) || {};
  $("kpiVenue").textContent = hop.venue || "Cookiebox";
  $("kpiImpact").textContent =
    route.priceImpactPct == null ? "—" : Number(route.priceImpactPct).toFixed(4) + "%";
}

async function boot() {
  try {
    const via = await pickRpc();
    setStatus("RPC Cookie Chain OK (" + via + "). Genesis " + GENESIS.slice(0, 8) + "…", true);
    await refreshChain();
    await Promise.all([refreshMarkets().catch(() => {}), refreshQuote().catch((err) => setStatus("Quote: " + err.message, false))]);
  } catch (err) {
    setStatus("RPC falló: " + err.message, false);
  }
}

$("btnConnect").addEventListener("click", () => {
  connectWallet().catch((err) => setStatus(err.message, false));
});
$("btnPing").addEventListener("click", () => {
  $("btnPing").disabled = true;
  pingOnchain()
    .catch((err) => setStatus(err.message, false))
    .finally(() => {
      $("btnPing").disabled = !state.publicKey;
    });
});
$("btnRefresh").addEventListener("click", () => {
  Promise.all([refreshChain(), refreshWallet(), refreshMarkets(), refreshQuote()]).catch((err) =>
    setStatus(err.message, false)
  );
});

boot();
