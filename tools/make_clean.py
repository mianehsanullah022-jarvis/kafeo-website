"""Build the CLEAN version of the KAFEO site from index.html.

  python3 tools/make_clean.py preview   -> writes preview.html (draft preview: offer pop-up on, orders off)
  python3 tools/make_clean.py live      -> rewrites index.html as the clean site (offer stays as set in WEB_PROMO)

Nothing is deleted from index.html until 'live' is run on the owner's say-so.
"""
import re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
s = src

def cut_section(sec_id):
    """Remove <!-- comment --> + <section id=...> ... </section>"""
    global s
    i = s.index(f'<section id="{sec_id}"')
    c = s.rfind("<!--", 0, i)
    if c != -1 and s[c:i].strip().endswith("-->") and "\n" in s[c:i] and s[c:i].count("<!--") == 1:
        i = c
    j = s.index("</section>", i) + len("</section>")
    s = s[:i] + s[j:]

def rep(old, new, must=True):
    global s
    n = s.count(old)
    if must:
        assert n == 1, (n, old[:80])
    s = s.replace(old, new)

# ---- 1. sections that are mostly text or duplicates
for sid in ["quickTop", "mani", "day"]:
    cut_section(sid)
s = re.sub(r'\s*<div class="mq( rev)?" aria-hidden="true"><div class="t" id="mq[12]"></div></div>', "", s)

# ---- 1b. make the scripts safe without those sections
rep('$("#mq1").innerHTML=$("#mq2").innerHTML=', 'if($("#mq1"))$("#mq1").innerHTML=$("#mq2").innerHTML=')
rep('const mt=$("#maniT");', 'const mt=$("#maniT")||document.createElement("p");')
rep(' if(!RM){const p=prog(pins.mani);', ' if(!pins.mani){}else if(!RM){const p=prog(pins.mani);')
rep(' const dp=RM?.95:prog(pins.day);', ' if(pins.day){const dp=RM?.95:prog(pins.day);')
rep('dps.forEach((d,i)=>d.classList.toggle("on",i===di));', 'dps.forEach((d,i)=>d.classList.toggle("on",i===di));}')

# ---- 2. hero: no banner, no extra lines
s = re.sub(r'\s*<a class="kxpromo" href="#menu" id="kxPromo">.*?</a>', "", s, count=1, flags=re.S)
s = re.sub(r'\s*<a class="kxhero" href="#quickTop">.*?</a>', "", s, count=1, flags=re.S)
s = re.sub(r'\s*<p class="hero-p" data-i18n="hero.p">.*?</p>', "", s, count=1, flags=re.S)
rep('<a href="#quickTop" class="kxnav">⚡ Quick order</a>', "")

# ---- 3. shorter copy everywhere
rep("A juicy beef burger and two premium beef steaks are on the way. Our kitchen is still perfecting every recipe, so they're not on the menu just yet.",
    "A beef burger and two beef steaks. Coming soon.")
s = re.sub(r'\s*<ul class="beef-list" data-r>.*?</ul>', "", s, count=1, flags=re.S)
rep("Drag ingredients into the glass, or tap them. When it looks right, add it to your order and we'll pour it exactly like that.", "Tap ingredients to build it. Rs 800.")
rep("Five plates and glasses that define KAFEO. Tap + to make one yours.", "Our five favourites.")
rep("Everything we serve, from the morning cappuccino to the midnight pizza. Tap + and send your order on WhatsApp.", "Tap + to add. Send when ready.")
rep("Hover or tap a card to flip it and see what's inside.", "Tap a card to see what's inside.")
rep("Pick your KAFEO pizza and size, then drop on extra toppings. The price updates as you go.", "Pick a pizza, size and toppings.")
rep("Type your area or share your location. KAFEO delivers within about 6 km of Shadman Chowk.", "We deliver within 6 km of Shadman Chowk.")
rep("Move around the room. The best seats in the house are waiting, and one of them can have your name on it tonight.", "The best seats in the house, saved for you.")
s = re.sub(r'\s*<p data-r style="margin-top:20px">KAFEO started at Shadman Chowk.*?</p>\s*<p data-r>Students come to KAFEO.*?</p>',
           '\n        <p data-r style="margin-top:20px">Good coffee, generous food and a warm place to unwind at Shadman Chowk.</p>', s, count=1, flags=re.S)
rep("Your feedback goes straight to the KAFEO team. Loved it? A Google review helps more people in Lahore find us.", "Tell us how it went. Loved it? Leave us a Google review.")
s = re.sub(r'\s*<div class="fcta" data-r>.*?</div>\s*</div>\s*</div>', "\n  </div>", s, count=1, flags=re.S)
rep('<p style="margin-top:14px;color:var(--dim)">Kitchen and barista bar open all day.</p>', "")

# ---- 4. offer as an animated pop-up (instead of the hero banner)
POP_CSS = r"""
/* ===== Offer pop-up (replaces the hero banner) ===== */
#kxOffer{position:fixed;inset:0;z-index:92;display:grid;place-items:center;padding:20px;background:#0c0806b8;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);opacity:0;transition:opacity .35s}
#kxOffer[hidden]{display:none}
#kxOffer.on{opacity:1}
#kxOffer .oc{position:relative;width:min(400px,100%);border-radius:28px;padding:3px;background:conic-gradient(from var(--a,0deg),#e3a35a,#ff7a2f,#f6ecdc,#e3a35a);animation:kxSpin 4s linear infinite;transform:translateY(40px) scale(.86) rotate(-3deg);transition:transform .7s cubic-bezier(.2,1.6,.4,1)}
#kxOffer.on .oc{transform:none}
@property --a{syntax:"<angle>";inherits:false;initial-value:0deg}
@keyframes kxSpin{to{--a:360deg}}
#kxOffer .oi{position:relative;overflow:hidden;border-radius:25px;background:#140d0a;color:#f6ecdc;padding:34px 26px 24px;text-align:center}
#kxOffer .oi::after{content:"";position:absolute;top:0;bottom:0;width:70px;left:-120px;background:linear-gradient(90deg,transparent,#ffffff26,transparent);transform:skewX(-20deg);animation:kxSweep 3.2s 1.2s ease-in-out infinite}
@keyframes kxSweep{0%,55%{left:-120px}100%{left:120%}}
#kxOffer .x{position:absolute;right:12px;top:12px;width:40px;height:40px;border-radius:50%;border:1px solid #ffffff30;background:#ffffff10;color:#f6ecdc;font-size:22px;cursor:pointer;z-index:2}
#kxOffer .tag{font:500 11px var(--f-m);letter-spacing:.24em;text-transform:uppercase;color:#e3a35a}
#kxOffer .big{position:relative;display:inline-flex;align-items:flex-start;margin:8px 0 0;font-family:var(--f-d);line-height:.85;color:#e3a35a}
#kxOffer .big b{font-weight:400;font-size:132px;letter-spacing:-.03em;display:inline-block;animation:kxPulse10 2.4s 1.6s ease-in-out infinite}
#kxOffer .big i{font-style:normal;font-size:64px;margin-top:10px}
@keyframes kxPulse10{50%{transform:scale(1.06)}}
#kxOffer .stamp{position:absolute;right:-26px;bottom:6px;background:#ff7a2f;color:#140d0a;font:700 15px var(--f-m);letter-spacing:.16em;padding:7px 12px;border-radius:10px;transform:rotate(-14deg) scale(2.4);opacity:0}
#kxOffer.on .stamp{animation:kxStamp .45s .9s cubic-bezier(.3,1.6,.5,1) forwards}
@keyframes kxStamp{to{transform:rotate(-14deg) scale(1);opacity:1}}
#kxOffer h3{margin:14px 0 4px;font:400 30px/1.1 var(--f-d)}
#kxOffer p{margin:0;color:#d9b88f;font-size:14.5px}
#kxOffer .chips{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:18px 0 6px}
#kxOffer .chips span{border:1px solid #e3a35a;border-radius:999px;padding:7px 12px;font-size:13px;font-weight:600;opacity:0;transform:translateY(12px)}
#kxOffer.on .chips span{animation:kxUp .45s forwards}
#kxOffer.on .chips span:nth-child(1){animation-delay:1.1s}#kxOffer.on .chips span:nth-child(2){animation-delay:1.25s}#kxOffer.on .chips span:nth-child(3){animation-delay:1.4s}#kxOffer.on .chips span:nth-child(4){animation-delay:1.55s}
@keyframes kxUp{to{opacity:1;transform:none}}
#kxOffer .perf{margin:18px -26px 16px;border-top:2px dashed #4a3426;position:relative}
#kxOffer .perf::before,#kxOffer .perf::after{content:"";position:absolute;top:-13px;width:24px;height:24px;border-radius:50%;background:#0c0806}
#kxOffer .perf::before{left:-12px}#kxOffer .perf::after{right:-12px}
#kxOffer .go{width:100%;border:0;border-radius:999px;padding:16px;font:700 16px var(--f-b);color:#140d0a;background:linear-gradient(120deg,#e3a35a,#ff7a2f);cursor:pointer;box-shadow:0 0 0 0 #ff7a2f88;animation:kxGlow 2s 1.8s infinite}
@keyframes kxGlow{70%{box-shadow:0 0 0 16px #ff7a2f00}100%{box-shadow:0 0 0 0 #ff7a2f00}}
#kxOffer .later{margin-top:10px;background:none;border:0;color:#d9b88f;font-size:13px;cursor:pointer;padding:8px}
#kxOffer .fx{position:absolute;left:50%;top:38%;width:0;height:0;pointer-events:none}
#kxOffer .fx i{position:absolute;width:9px;height:14px;border-radius:2px;opacity:0;animation:kxPop 1.3s cubic-bezier(.15,.7,.3,1) var(--d) forwards}
@keyframes kxPop{0%{opacity:1;transform:translate(0,0) rotate(0)}80%{opacity:1}100%{opacity:0;transform:translate(var(--x),var(--y)) rotate(var(--r))}}
@media (prefers-reduced-motion:reduce){#kxOffer .oc,#kxOffer .oi::after,#kxOffer .big b,#kxOffer .go{animation:none}#kxOffer .stamp,#kxOffer .chips span{opacity:1;transform:rotate(-14deg)}#kxOffer .chips span{transform:none}}
"""
POP_HTML = """<div id="kxOffer" hidden role="dialog" aria-modal="true" aria-labelledby="kxOfferT">
  <div class="oc"><div class="oi">
    <button type="button" class="x" id="kxOfferX" aria-label="Close">×</button>
    <div class="fx" id="kxOfferFx" aria-hidden="true"></div>
    <div class="tag">Website launch offer</div>
    <div class="big" aria-label="10 percent off"><b id="kxOfferN">0</b><i>%</i><span class="stamp">OFF</span></div>
    <h3 id="kxOfferT">On every website order</h3>
    <p>No code needed. It comes off in your basket.</p>
    <div class="chips"><span>Delivery</span><span>Takeaway</span><span>Dine-in</span><span>From your table</span></div>
    <div class="perf" aria-hidden="true"></div>
    <button type="button" class="go" id="kxOfferGo">Start ordering</button>
    <button type="button" class="later" id="kxOfferL">Maybe later</button>
  </div></div>
</div>
"""
POP_JS = r"""
/* ===== Offer pop-up: once per visit, only while the offer is shown (WEB_PROMO.live or preview) ===== */
(function(){
 const box=$("#kxOffer");if(!box||!promoShown())return;
 let seen=false;try{seen=sessionStorage.getItem("kafeo-x-offer")==="1"}catch(e){}
 if(seen&&!/[?&]offer\b/.test(location.search))return;
 const wb=$("#wb"),wbBg=$("#wbBg");let wbWaiting=false,isOpen=false;
 if(wb){new MutationObserver(()=>{if(isOpen&&!wb.hidden){wb.hidden=true;if(wbBg)wbBg.hidden=true;wbWaiting=true}}).observe(wb,{attributes:true,attributeFilter:["hidden"]})}
 function confetti(){const fx=$("#kxOfferFx");if(!fx||RM)return;const C=["#e3a35a","#ff7a2f","#f6ecdc","#6b3d1f"];
  fx.innerHTML=Array.from({length:34},(_,i)=>{const a=Math.random()*Math.PI*2,r=120+Math.random()*170;return `<i style="background:${C[i%4]};--x:${Math.cos(a)*r}px;--y:${Math.sin(a)*r-60}px;--r:${Math.random()*720-360}deg;--d:${.75+Math.random()*.25}s"></i>`}).join("")}
 function count(){const n=$("#kxOfferN");if(RM){n.textContent="10";return}const t0=performance.now()+350;const step=t=>{const p=Math.min(1,Math.max(0,(t-t0)/700)),e=1-Math.pow(1-p,3);n.textContent=Math.round(10*e);if(p<1)requestAnimationFrame(step)};requestAnimationFrame(step)}
 function open(){isOpen=true;box.hidden=false;requestAnimationFrame(()=>box.classList.add("on"));count();confetti();try{sessionStorage.setItem("kafeo-x-offer","1")}catch(e){}setTimeout(()=>$("#kxOfferGo").focus(),400)}
 function close(go){box.classList.remove("on");setTimeout(()=>{box.hidden=true;isOpen=false;if(go){inkTo($("#menu"))}else if(wbWaiting&&wb){wb.hidden=false;if(wbBg)wbBg.hidden=false}},350)}
 $("#kxOfferX").onclick=()=>close(false);$("#kxOfferL").onclick=()=>close(false);$("#kxOfferGo").onclick=()=>close(true);
 box.addEventListener("click",e=>{if(e.target===box)close(false)});addEventListener("keydown",e=>{if(e.key==="Escape"&&isOpen)close(false)});
 setTimeout(open,RM?300:1500);
})();
"""
import re as _re
for _old in ["oc","oi","x","tag","big","stamp","chips","perf","go","later","fx"]:
    POP_CSS = _re.sub(r"\.%s(?![\w-])" % _old, ".kxo-" + _old, POP_CSS)
    POP_HTML = _re.sub(r'class="%s"' % _old, 'class="kxo-%s"' % _old, POP_HTML)
i = s.rfind("</style>", 0, s.find("<body"))
s = s[:i] + POP_CSS + s[i:]
rep('<div id="kxOk" hidden></div>', '<div id="kxOk" hidden></div>\n' + POP_HTML)
end = s.rfind("</script>")
s = s[:end] + POP_JS + s[end:]

mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
if mode == "live":
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(s)
    print("index.html is now the clean site")
else:
    pv = s.replace("<head>", '<head>\n<meta name="robots" content="noindex,nofollow">\n<script>window.__kxPreview=true</script><!--PREVIEW-->', 1)
    ribbon = '<div id="kxDraft" style="position:fixed;left:0;right:0;bottom:0;z-index:95;background:#ff7a2f;color:#140d0a;font:600 12px/1.3 \'Instrument Sans\',Arial,sans-serif;text-align:center;padding:6px 12px calc(6px + env(safe-area-inset-bottom,0px))">DRAFT PREVIEW · not live · orders are off on this page</div><!--PREVIEW-->'
    pv = pv.replace("<body>", "<body>\n" + ribbon, 1)
    blk = '<script>document.addEventListener("submit",function(e){var f=e.target,ids={orderForm:"omsg",resForm:"rmsg",revForm:"vmsg"};if(f&&ids[f.id]){e.preventDefault();e.stopImmediatePropagation();var m=document.getElementById(ids[f.id]);if(m)m.textContent="Preview only: sending is switched off on this draft page."}},true)</script><!--PREVIEW-->\n</body>'
    k = pv.rfind("</body>"); pv = pv[:k] + blk + pv[k + 7:]
    pv = pv.replace('serviceWorker.register("sw.js")', 'serviceWorker.getRegistration("sw.js")', 1)
    open(os.path.join(ROOT, "preview.html"), "w", encoding="utf-8").write(pv)
    print("preview.html written", len(pv))
