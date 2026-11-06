const $=id=>document.getElementById(id);
let bag=[],catalog=[],active=null,searchVersion=0,detailVersion=0,shiftAnchor=null,lastShift=null;
try{const saved=JSON.parse(localStorage.getItem('fieldwork-bag')||'[]');if(Array.isArray(saved))bag=saved.filter(x=>typeof x==='string').slice(0,100)}catch{}
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n}
async function api(path,body){const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),70000);try{const r=await fetch(path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:controller.signal});const data=await r.json();if(!r.ok)throw Error(data.message||'The request could not be completed. Please retry.');return data}finally{clearTimeout(timer)}}
function saveBag(){try{localStorage.setItem('fieldwork-bag',JSON.stringify(bag))}catch{$('status').textContent='Your bag works for this session, but browser storage is unavailable.'}renderBag()}
function renderBag(){$('bag-count').textContent=bag.length;$('bag-items').replaceChildren();for(const id of bag){const d=catalog.find(x=>x.id===id);const row=el('div');row.append(el('span',d?`${d.brand} ${d.name}`:id));const remove=el('button','Remove');remove.onclick=()=>{bag=bag.filter(x=>x!==id);saveBag()};row.append(remove);$('bag-items').append(row)}if(!bag.length)$('bag-items').append(el('p','Your next favorite belongs here.'))}
function showTrace(data){$('trace').textContent=`Run ${data.run_id} · ${data.mode}\n`+data.trace.map(t=>`${t.tool}: ${t.status}${t.elapsed_ms!==undefined?` · ${t.elapsed_ms}ms · attempt ${t.attempt}`:''}`).join('\n')}
function cards(discs){$('results').replaceChildren();for(const d of discs){const card=el('button',undefined,'card');card.append(el('span',d.brand,'brand'),el('h3',d.name),el('span',`${d.category} · ${d.popularity||0} local selections`,'category'));const nums=el('div',undefined,'numbers');for(const k of ['speed','glide','turn','fade']){const b=el('b',d[k]);b.append(el('small',k));nums.append(b)}card.append(nums,el('span',d.reason||'Explore this disc','reason'),el('span','View disc ↗','arrow'));card.onclick=()=>openDisc(d);$('results').append(card)}}
const shiftPanel=el('div',undefined,'shift-panel');
shiftPanel.hidden=true;
const shiftLabel=el('p');shiftPanel.append(shiftLabel);
const shiftButtons=el('div',undefined,'suggestions');shiftPanel.append(shiftButtons);
for(const [direction,label] of [['overstable','More overstable'],['understable','More understable'],['faster','Faster'],['slower','Slower']]){
  const button=el('button',label);button.type='button';button.dataset.direction=direction;
  button.onclick=()=>shiftResults(direction);shiftButtons.append(button);
}
document.querySelector('.results-heading').after(shiftPanel);
function preferences(){return {brands:[...document.querySelectorAll('#brands input:checked')].map(n=>n.value),sort:$('sort').value,bag}}
function updateShiftControls(discs){
  shiftAnchor=discs[0]||null;shiftPanel.hidden=!shiftAnchor;
  if(!shiftAnchor)return;
  shiftLabel.textContent=`Shift from ${shiftAnchor.name} · speed ${shiftAnchor.speed} · stability ${shiftAnchor.turn+shiftAnchor.fade} (turn + fade)`;
  for(const b of shiftButtons.children)b.hidden=(b.dataset.direction==='slower'&&shiftAnchor.speed<=1)||(b.dataset.direction==='faster'&&shiftAnchor.speed>=14);
}
function setBusy(busy){$('find').disabled=busy;for(const b of shiftButtons.children)b.disabled=busy;$('results').setAttribute('aria-busy',String(busy))}
async function requestResults(path,body,isShift=false){
  const version=++searchVersion;setBusy(true);
  $('status').textContent=isShift?'Finding discs in that direction…':'Finding and ranking matching flights…';
  try{
    const data=await api(path,body);if(version!==searchVersion)return;
    showTrace(data);
    if(isShift&&!data.discs.length){$('status').textContent=data.message||'No matches for that shift. Try another direction.';return}
    cards(data.discs);updateShiftControls(data.discs);
    lastShift=isShift?{reference_id:body.reference_id,direction:body.direction}:null;
    $('result-title').textContent='Your next possibilities';$('result-count').textContent=`${data.discs.length} matches`;
    $('status').textContent=data.message||'Select a disc for manufacturer imagery and bag options.';
  }catch(e){if(version===searchVersion)$('status').textContent=e.name==='AbortError'?'This is taking too long. Please retry.':e.message}
  finally{if(version===searchVersion)setBusy(false)}
}
async function search(event){
  event?.preventDefault();const query=$('query').value.trim();
  if(!query){$('query').focus();return}
  await requestResults('/api/recommend',{query,...preferences()});
}
async function shiftResults(direction){
  if(!shiftAnchor)return;
  if(direction==='slower'&&shiftAnchor.speed<=1||direction==='faster'&&shiftAnchor.speed>=14)return;
  await requestResults('/api/shift',{reference_id:shiftAnchor.id,direction,...preferences()},true);
}
let stockVersion=0;
function stockLink(url,text){
  try{const parsed=new URL(url);if(parsed.protocol!=='https:'||parsed.username||parsed.password)return el('span',text)}catch{return el('span',text)}
  const link=el('a',text);link.href=url;link.target='_blank';link.rel='noopener noreferrer';return link;
}
function renderStock(data){
  $('stock-offers').replaceChildren();
  $('stock-status').textContent=data.message||`${data.offers.length} offers returned by DiscFinder.`;
  const context=data.query_context||{};
  $('stock-note').textContent=`Prices and availability are reported by DiscFinder for ${context.target_country_name||data.country_code}${context.target_currency?' in '+context.target_currency:''}. Shipping and checkout charges are excluded. Confirm the product and stock with the retailer.`;
  for(const offer of data.offers||[]){
    const row=el('article',undefined,'stock-offer');
    row.append(stockLink(offer.purchase_url,`${offer.retailer||'Retailer'} - ${offer.price||'See retailer for price'}`));
    const details=[offer.country,offer.plastic,offer.weight,Array.isArray(offer.colors)?offer.colors.join(', '):''].filter(Boolean).join(' | ');
    row.append(el('p',details));
    if(offer.is_local_retailer)row.append(el('small','Retailer in selected country'));
    if(offer.affiliate_disclosure)row.append(el('p',offer.affiliate_disclosure,'hint'));
    $('stock-offers').append(row);
  }
  $('stock-trace').textContent=`${data.source}\n${data.tool}\nRun ${data.run_id}\nChecked ${data.checked_at}\n`+JSON.stringify(data.trace,null,2);
}
async function loadStock(d,version){
  const request=++stockVersion;
  $('stock-status').textContent='Checking retailer stock through DiscFinder MCP?';
  $('stock-offers').replaceChildren();$('stock-note').textContent='';$('stock-trace').textContent='Connecting to https://finder.golfwithdiscs.com/mcp';
  $('stock-retry').disabled=true;$('stock-offers').setAttribute('aria-busy','true');
  try{
    const data=await api('/api/discs/'+encodeURIComponent(d.id)+'/stock',{country_code:$('stock-country').value});
    if(request!==stockVersion||version!==detailVersion)return;renderStock(data);
  }catch(e){
    if(request!==stockVersion||version!==detailVersion)return;
    $('stock-status').textContent='DiscFinder is unavailable. Refresh stock to retry. No alternate stock source was used.';
    $('stock-trace').textContent='https://finder.golfwithdiscs.com/mcp\nfind_retailer_stock: unavailable';
  }finally{if(request===stockVersion){$('stock-retry').disabled=false;$('stock-offers').setAttribute('aria-busy','false')}}
}
$('stock-country').onchange=()=>{if(active&&$('detail').open)loadStock(active,detailVersion)};
$('stock-retry').onclick=()=>{if(active&&$('detail').open)loadStock(active,detailVersion)};
async function openDisc(d){active=d;const version=++detailVersion;$('detail-brand').textContent=d.brand;$('detail-name').textContent=d.name;$('detail-flight').textContent=`Speed ${d.speed} · Glide ${d.glide} · Turn ${d.turn} · Fade ${d.fade}`;$('manufacturer').href=d.source;$('detail-image').hidden=true;$('detail-image').removeAttribute('src');$('image-status').hidden=false;$('image-status').textContent='Finding manufacturer image…';$('add-bag').textContent=bag.includes(d.id)?'Already in your bag':'Add to my bag';$('add-bag').disabled=bag.includes(d.id);$('detail').showModal();loadStock(d,version);try{const data=await api('/api/discs/'+encodeURIComponent(d.id),{});if(version!==detailVersion)return;showTrace(data);$('image-status').textContent=data.message||'';if(data.image_url&&/^https:\/\//.test(data.image_url)){const img=$('detail-image');img.alt=`${d.brand} ${d.name} — manufacturer image`;img.onload=()=>{if(version===detailVersion){img.hidden=false;$('image-status').hidden=!data.message}};img.onerror=()=>{if(version===detailVersion){img.hidden=true;$('image-status').hidden=false;$('image-status').textContent='The image could not load. Visit the manufacturer page below.'}};img.src=data.image_url}}catch(e){if(version===detailVersion)$('image-status').textContent='Manufacturer image unavailable. Visit the official page below.'}}
$('search').onsubmit=search;document.querySelectorAll('[data-query]').forEach(b=>b.onclick=()=>{$('query').value=b.dataset.query;search()});$('sort').onchange=()=>{if(lastShift)requestResults('/api/shift',{...lastShift,...preferences()},true);else if($('query').value.trim())search()};$('close-detail').onclick=()=>{$('detail').close();detailVersion++};$('detail').addEventListener('cancel',()=>detailVersion++);$('add-bag').onclick=()=>{if(active&&!bag.includes(active.id)){bag.push(active.id);saveBag();$('add-bag').disabled=true;$('add-bag').textContent='Added to your bag'}};$('bag-toggle').onclick=()=>{$('bag-panel').hidden=!$('bag-panel').hidden;if(!$('bag-panel').hidden)$('bag-panel').scrollIntoView({behavior:'smooth'})};
function renderBrands(data){
  const options=$('brand-options');options.replaceChildren();
  const popular=new Set(data.popular_brands||[]);
  const brands=data.brands||[...new Set(data.discs.map(d=>d.brand))].sort();
  for(const brand of brands){
    const label=el('label');const input=el('input');input.type='checkbox';input.value=brand;
    label.append(input,document.createTextNode(' '+brand));label.dataset.extra=String(!popular.has(brand));
    label.hidden=!popular.has(brand);options.append(label);
  }
  $('brand-total').textContent=`${brands.length} manufacturers available.`;
  const toggle=$('show-brands');const extra=brands.filter(b=>!popular.has(b)).length;
  toggle.hidden=!extra;
  const update=()=>{const expanded=toggle.getAttribute('aria-expanded')==='true';const selected=[...options.querySelectorAll('label[data-extra="true"] input:checked')].length;
    toggle.textContent=expanded?'Show less':`Show more (${extra})${selected?` · ${selected} selected`:''}`;
    for(const label of options.children)label.hidden=label.dataset.extra==='true'&&!expanded;
  };
  toggle.onclick=()=>{toggle.setAttribute('aria-expanded',String(toggle.getAttribute('aria-expanded')!=='true'));update()};
  options.onchange=update;update();
}
api('/api/catalog').then(data=>{catalog=data.discs;renderBrands(data);$('result-count').textContent=`${catalog.length} discs / ${data.brands.length} brands`;renderBag();cards(catalog.filter(d=>['leopard3','river','crave'].includes(d.name.toLowerCase())))}).catch(()=>{$('status').textContent='The catalog is unavailable. Refresh to retry.'});renderBag();
