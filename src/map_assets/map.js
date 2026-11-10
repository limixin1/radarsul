const STORAGE = "sentinela-corredor-v2";
const mountedMaps = new WeakMap();
const AXIS = "#315d69", HIGHLIGHT = "#ffd45f", AMBER = "#a44916";
const readView = () => {
  try { return JSON.parse(sessionStorage.getItem(STORAGE)) || {}; }
  catch (_) { return {}; }
};

function labelAt(layer, point, label, cls) {
  const text = document.createElement("span");
  text.textContent = label;
  L.marker(point, {keyboard:false, interactive:false, icon:L.divIcon({
    className:"map-label " + cls, html:text, iconAnchor:[cls === "map-focus-label" ? -19 : -8, 4], iconSize:[0, 0]
  })}).addTo(layer);
}

function groupNearby(map, records) {
  const groups = [];
  for (const record of records) {
    const pixel = map.latLngToContainerPoint(record.point);
    const nearby = groups.find(group => pixel.distanceTo(group.pixel) <= 29);
    if (nearby) nearby.records.push(record);
    else groups.push({pixel, point:record.point, records:[record]});
  }
  return groups;
}

function exportVector(map, data, marked) {
  const size = map.getSize(), canvas = document.createElement("canvas");
  canvas.width = size.x * 2;
  canvas.height = (size.y + 66) * 2;
  const ctx = canvas.getContext("2d");
  ctx.scale(2, 2);
  ctx.fillStyle = "#e9f1ee";
  ctx.fillRect(0, 0, size.x, size.y + 66);
  ctx.save();
  ctx.beginPath();
  ctx.rect(0, 0, size.x, size.y);
  ctx.clip();
  const line = (path, color, width) => {
    ctx.beginPath();
    path.forEach((coord, i) => {
      const p = map.latLngToContainerPoint(coord);
      if (i) ctx.lineTo(p.x, p.y); else ctx.moveTo(p.x, p.y);
    });
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
  };
  for (const [id, segment] of Object.entries(data.segments)) {
    const selected = marked.has(id);
    for (const path of segment.paths)
      line(path, selected ? "#9a6100" : data.antt[id] ? AMBER : AXIS, selected ? 6 : 2.5);
  }
  for (const [kind, records] of [["radar", data.radars], ["prf", data.prf]]) {
    for (const item of records.filter(r => r.point)) {
      const p = map.latLngToContainerPoint(item.point);
      ctx.beginPath();
      ctx.fillStyle = item.id === data.focus ? HIGHLIGHT : kind === "radar" ? "#087569" : AMBER;
      if (kind === "prf") {
        ctx.moveTo(p.x, p.y - 4);
        ctx.lineTo(p.x + 4, p.y);
        ctx.lineTo(p.x, p.y + 4);
        ctx.lineTo(p.x - 4, p.y);
        ctx.closePath();
      } else ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#142b3c";
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  }
  ctx.restore();
  ctx.fillStyle = "#142b3c";
  ctx.font = "bold 12px system-ui";
  ctx.fillText("SENTINELA · BR-101/SC", 10, size.y + 16, size.x - 20);
  ctx.font = "11px system-ui";
  ctx.fillText(data.places.find(item => item.id === data.focus)?.detail
    || data.segments[data.focus?.slice(3)]?.label || data.focus?.replace("cidade:", "") || "Corredor",
    10, size.y + 33, size.x - 20);
  ctx.fillText(data.axisCredit, 10, size.y + 51, size.x - 20);
  canvas.toBlob(blob => {
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "sentinela_mapa_br101_sc.png";
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1500);
  }, "image/png");
}

export default function ({parentElement, data, setTriggerValue}) {
  const canvas = parentElement.querySelector(".map-canvas");
  // Streamlit can render new data on the same element before calling the old cleanup.
  mountedMaps.get(canvas)?.();
  const status = parentElement.querySelector(".map-status");
  const axisCredit = parentElement.querySelector("[data-credit=axis]");
  const satelliteCredit = parentElement.querySelector("[data-credit=satellite]");
  const buttons = [...parentElement.querySelectorAll("[data-mode]")];
  const reset = parentElement.querySelector("[data-action=reset]");
  const download = parentElement.querySelector("[data-action=export]");
  const listeners = new AbortController();
  const satelliteLink = document.createElement("a");
  satelliteLink.href = "https://cloudless.eox.at/documentation/faq";
  satelliteLink.target = "_blank";
  satelliteLink.rel = "noopener noreferrer";
  satelliteLink.textContent = data.satelliteCredit;
  satelliteCredit.replaceChildren(satelliteLink);
  axisCredit.textContent = data.axisCredit;
  status.hidden = true;

  const previous = readView();
  let mode = "2d";
  const map = L.map(canvas, {maxZoom:16, minZoom:7, scrollWheelZoom:false, attributionControl:false,
    maxBounds:[[-30.1,-50.7],[-26.8,-47.7]], maxBoundsViscosity:1});
  const allPaths = Object.values(data.segments).flatMap(segment => segment.paths);
  const points = allPaths.flat();
  const corridor = L.latLngBounds(points);
  const defaultBounds = L.latLngBounds([[-29.55,-49.95],[-27.85,-48.45]]);
  const layer = L.layerGroup().addTo(map);
  const labels = L.layerGroup().addTo(map);
  const focus = data.places.find(r => r.id === data.focus);
  const focusCity = data.focus?.startsWith("cidade:") ? data.focus.slice(7) : null;
  const cityKey = city => city?.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
  const places = [...data.places, ...data.anchors];
  const focusSegment = data.focus?.startsWith("km:") ? data.focus.slice(3) : focus?.segment;
  const selectedSegments = new Set(focus?.point || !focusSegment ? [] : [focusSegment]);
  const segmentGeometry = id => data.segments[id]?.paths.flat() || [];
  const itemGeometry = item => item.point ? [item.point] : segmentGeometry(item.segment);
  const cityGeometry = city => places
    .filter(item => item.cityKey === city).flatMap(itemGeometry);
  if (focusCity) for (const item of places)
    if (item.cityKey === cityKey(focusCity) && item.segment && !item.point) selectedSegments.add(item.segment);

  const search = data.search;
  const searchKey = JSON.stringify(search);
  const intent = JSON.stringify([searchKey, data.focus]);
  const searchGeometry = search.kind === "trecho" ? segmentGeometry(search.value)
    : search.kind === "ponto" ? data.places.filter(r => r.id === search.value).flatMap(itemGeometry)
    : search.kind === "cidade" ? cityGeometry(search.value) : [];
  const focusedGeometry = focus ? itemGeometry(focus)
    : focusSegment ? segmentGeometry(focusSegment)
    : focusCity ? cityGeometry(cityKey(focusCity)) : [];
  const location = searchGeometry.length && (!focusedGeometry.length || previous.searchKey !== searchKey)
    ? searchGeometry : focusedGeometry;
  const fit = coords => map.fitBounds(coords.length ? L.latLngBounds(coords) : corridor.isValid() ? corridor : defaultBounds,
    {padding:[24,24], maxZoom:13, animate:false});
  if (previous.intent === intent && Array.isArray(previous.center) && previous.center.length === 2
      && previous.center.every(Number.isFinite) && Number.isFinite(previous.zoom)) {
    map.setView(previous.center, previous.zoom, {animate:false});
  } else fit(location);
  const save = () => {
    const {lat, lng} = map.getCenter();
    try { sessionStorage.setItem(STORAGE, JSON.stringify({intent, searchKey, center:[lat,lng], zoom:map.getZoom(), mode})); }
    catch (_) { /* Navegação continua disponível quando o armazenamento está bloqueado. */ }
  };

  const select = value => { save(); setTriggerValue("selected", value); };
  const showGroup = (marker, records, kind) => {
    if (kind === "radar" && records.length === 1) { select(records[0].id); return; }
    const popup = document.createElement("div");
    popup.className = "map-popup";
    const title = document.createElement("strong");
    title.textContent = kind === "radar" ? "Equipamentos próximos" : "Ocorrências PRF";
    popup.append(title);
    for (const record of records) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = record.detail + (kind === "prf" ? " · Abrir trecho" : "");
      button.disabled = kind === "prf" && !record.segment;
      button.addEventListener("click", () => select(kind === "radar" ? record.id : "km:" + record.segment));
      popup.append(button);
      if (kind === "prf") {
        const link = document.createElement("a");
        const url = new URL("https://www.google.com/maps/search/");
        url.searchParams.set("api", "1");
        url.searchParams.set("query", record.point.map(value => value.toFixed(6)).join(","));
        link.href = url.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "Abrir no Google Maps";
        link.setAttribute("aria-label", "Abrir no Google Maps · " + record.detail);
        popup.append(link);
      }
    }
    marker.bindPopup(popup, {autoPan:false}).openPopup();
    popup.querySelector("button:not([disabled])")?.focus();
  };

  const trackMarker = (group, kind) => {
    const items = group.records;
    const selected = items.some(r => kind === "radar" ? r.id === data.focus : selectedSegments.has(r.segment));
    const pin = document.createElement("div");
    pin.className = "map-pin " + kind + (selected ? " selected" : "")
      + (kind === "radar" && items.every(r => !r.active) ? " catalog" : "");
    if (items.length > 1) {
      const count = document.createElement("span");
      count.textContent = String(items.length);
      pin.append(count);
    }
    const title = items.length === 1 ? items[0].detail : items.length + (kind === "radar" ? " equipamentos próximos" : " ocorrências PRF próximas");
    const marker = L.marker(group.point, {title, alt:title, keyboard:true,
      icon:L.divIcon({className:"map-pin-hit",html:pin,iconSize:[44,44],iconAnchor:[22,22]})}).addTo(layer);
    marker.on("click", () => showGroup(marker, items, kind));
    marker.getElement()?.setAttribute("aria-label", title);
  };

  const draw = () => {
    layer.clearLayers();
    labels.clearLayers();
    const zoom = map.getZoom();
    const kmAtZoom = zoom >= 12 ? 5 : 20;
    const occupied = [];
    const placeLabel = (coord, label, cls, force = false) => {
      const {x, y} = map.latLngToContainerPoint(coord);
      const w = label.length * 6 + 10;
      if (!force && (x < 24 || x + w > map.getSize().x || y < 14 || y > map.getSize().y - 13
          || occupied.some(p => x < p.x + p.w && p.x < x + w && Math.abs(y - p.y) < 17))) return;
      occupied.push({x, y, w});
      labelAt(labels, coord, label, cls);
    };
    const shownFocus = data.radars.find(item => item.id === data.focus);
    if (shownFocus?.point) placeLabel(shownFocus.point, shownFocus.city + " · " + shownFocus.id, "map-focus-label", true);
    for (const [id, segment] of Object.entries(data.segments)) {
      const selected = selectedSegments.has(id);
      const events = data.antt[id] || data.prf.filter(r => r.segment === id && !r.point).length;
      const radarReference = data.radars.some(r => r.segment === id && r.precision === "trecho");
      for (const path of segment.paths) {
        if (mode === "satellite" || selected) L.polyline(path,
          {color:"#102a36", weight:selected ? 9 : 6, opacity:.85, interactive:false}).addTo(layer);
        const referenced = Boolean(events || radarReference);
        const line = L.polyline(path, {color:selected ? HIGHLIGHT : referenced ? AMBER : mode === "satellite" ? "#b8ebea" : AXIS,
          weight:selected ? 5 : referenced ? 4 : 3, opacity:.98, interactive:true}).addTo(layer);
        line.on("click", () => select("km:" + id));
        if (Number(id) % kmAtZoom === 0 && path === segment.paths[0]) {
          const start = segment.ranges[0][0].toLocaleString("pt-BR", {maximumFractionDigits:3});
          placeLabel(path[0], "km " + start, "km");
        }
      }
    }
    for (const [kind, records] of [["prf", data.prf], ["radar", data.radars]]) {
      for (const group of groupNearby(map, records.filter(r => r.point))) trackMarker(group, kind);
    }
    const cities = new Set(shownFocus?.point ? [shownFocus.cityKey] : []);
    for (const item of places) {
      if (cities.has(item.cityKey) || (!item.point && !item.segment)) continue;
      const coord = item.point || segmentGeometry(item.segment)[0];
      if (!coord || !map.getBounds().contains(coord)) continue;
      cities.add(item.cityKey);
      placeLabel(coord, item.city, "");
    }
  };

  let tiles;
  let requests = 0, errors = 0;
  const setMode = value => {
    mode = value;
    status.hidden = true;
    canvas.classList.toggle("satellite", mode === "satellite");
    satelliteCredit.hidden = mode !== "satellite";
    for (const button of buttons) button.setAttribute("aria-pressed", String(button.dataset.mode === mode));
    if (tiles) { tiles.remove(); tiles = null; }
    if (mode === "satellite") {
      requests = 0;
      errors = 0;
      tiles = L.tileLayer(data.satelliteUrl, {maxNativeZoom:14, maxZoom:16, noWrap:true,
        keepBuffer:1, updateWhenIdle:true, bounds:[[-30.1,-50.7],[-26.8,-47.7]]});
      tiles.on("tileloadstart", () => requests++);
      tiles.on("tileerror", () => {
        errors++;
        status.textContent = "Parte das imagens está indisponível. O traçado, as seleções e a lista continuam disponíveis.";
        status.hidden = false;
      });
      tiles.on("load", () => {
        if (requests > 0 && errors >= requests) {
          status.textContent = "Imagens indisponíveis. Use Mapa 2D ou siga pelo traçado e pela lista.";
          status.hidden = false;
        }
      });
      tiles.addTo(map);
    }
    draw();
    save();
  };

  for (const button of buttons) button.addEventListener("click", () => {
    if (button.dataset.mode !== mode) setMode(button.dataset.mode);
  }, {signal:listeners.signal});
  reset.addEventListener("click", () => fit([]), {signal:listeners.signal});
  download.addEventListener("click", () => exportVector(map, data, selectedSegments), {signal:listeners.signal});
  map.on("moveend", () => { draw(); save(); });
  const resize = new ResizeObserver(() => map.invalidateSize({debounceMoveend:true}));
  resize.observe(canvas);
  const dispose = () => {
    if (mountedMaps.get(canvas) !== dispose) return;
    mountedMaps.delete(canvas);
    listeners.abort();
    resize.disconnect();
    map.off("moveend");
    map.remove();
  };
  mountedMaps.set(canvas, dispose);
  setMode(previous.mode === "satellite" ? "satellite" : "2d");
  return dispose;
}
