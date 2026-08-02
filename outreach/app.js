(() => {
  "use strict";

  const canvas = document.querySelector("#card-canvas");
  const ctx = canvas.getContext("2d", { alpha: false });
  const formats = {
    landscape: {
      width: 1280, height: 720, label: "1280 × 720 PNG · 16:9",
      margin: 76, eyebrowY: 130, headlineY: 244, headlineWidth: 555,
      headlineMax: 76, descriptionWidth: 505, urlY: 655,
      sticker: { x: 1000, y: 370, minX: 790, maxX: 1130, minY: 190, maxY: 535, maxWidth: 470, maxHeight: 535 },
    },
    square: {
      width: 1080, height: 1080, label: "1080 × 1080 PNG · 1:1",
      margin: 72, eyebrowY: 108, headlineY: 204, headlineWidth: 850,
      headlineMax: 82, descriptionWidth: 650, urlY: 1010,
      sticker: { x: 750, y: 750, minX: 320, maxX: 850, minY: 610, maxY: 850, maxWidth: 520, maxHeight: 520 },
    },
  };

  const elements = {
    stickerSelect: document.querySelector("#sticker-select"),
    stickerName: document.querySelector("#sticker-name"),
    stickerUpload: document.querySelector("#sticker-upload"),
    loadSticker: document.querySelector("#load-sticker"),
    stickerStatus: document.querySelector("#sticker-status"),
    eyebrow: document.querySelector("#eyebrow"),
    headline: document.querySelector("#headline"),
    description: document.querySelector("#description"),
    url: document.querySelector("#url"),
    theme: document.querySelector("#theme"),
    tangyStyle: document.querySelector("#tangy-style"),
    format: document.querySelector("#format"),
    scale: document.querySelector("#sticker-scale"),
    x: document.querySelector("#sticker-x"),
    y: document.querySelector("#sticker-y"),
    scaleOutput: document.querySelector("#scale-output"),
    xOutput: document.querySelector("#x-output"),
    yOutput: document.querySelector("#y-output"),
    showDots: document.querySelector("#show-dots"),
    showBlobs: document.querySelector("#show-blobs"),
    reset: document.querySelector("#reset-card"),
    download: document.querySelector("#download-card"),
    dimensions: document.querySelector("#preview-dimensions"),
  };

  const themes = {
    sunset: { canvas: "#fffcf7", ink: "#212121", slate: "#686879", muted: "#92929f", dot: "#dedbd9", accent: "#ff7759", blobs: ["#ffdec7", "#ffcdd3", "#ffdd70", "#ff7759"] },
    berry: { canvas: "#fffaff", ink: "#281c2b", slate: "#716274", muted: "#9c8da0", dot: "#e4d9e5", accent: "#ed5a82", blobs: ["#f2d1ed", "#ffb7cf", "#d8c4ff", "#ed5a82"] },
    citrus: { canvas: "#fffdf5", ink: "#242419", slate: "#696956", muted: "#969680", dot: "#e1dfcf", accent: "#ff8b3d", blobs: ["#ffe199", "#cceca5", "#ffd060", "#ff8b3d"] },
    ocean: { canvas: "#f8fefd", ink: "#172728", slate: "#5c7173", muted: "#879b9d", dot: "#d5e3e2", accent: "#00a99b", blobs: ["#c6eeea", "#a8d9f2", "#ffd0b9", "#00a99b"] },
  };

  const defaults = {
    sticker: "053_reading_book.png",
    eyebrow: "A NOTE FROM OREO",
    headline: "Ideas deserve to travel",
    description: "Shape the message. Pick Oreo. Share it everywhere.",
    url: "elixpo.com",
    theme: "sunset",
    tangyStyle: "blobs",
    format: "landscape",
    scale: "92",
    x: "1000",
    y: "370",
  };

  let stickerImage = null;
  let stickerCrop = null;
  let uploadedObjectUrl = null;

  function activeFormat() {
    return formats[elements.format.value] || formats.landscape;
  }

  function organicBlob(cx, cy, rx, ry, fill, wobble = 0.14) {
    ctx.beginPath();
    const points = 64;
    for (let i = 0; i <= points; i += 1) {
      const angle = Math.PI * 2 * i / points;
      const wave = 1 + wobble * Math.sin(3 * angle + 0.7) + (wobble / 2) * Math.sin(5 * angle);
      const x = cx + Math.cos(angle) * rx * wave;
      const y = cy + Math.sin(angle) * ry * wave;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
  }

  function sunburst(cx, cy, innerRadius, outerRadius, points, fill) {
    ctx.beginPath();
    for (let i = 0; i < points * 2; i += 1) {
      const angle = -Math.PI / 2 + Math.PI * i / points;
      const radius = i % 2 === 0 ? outerRadius : innerRadius;
      const x = cx + Math.cos(angle) * radius;
      const y = cy + Math.sin(angle) * radius;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
  }

  function capsule(x, y, width, height, rotation, fill) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rotation);
    ctx.fillStyle = fill;
    ctx.beginPath();
    ctx.roundRect(-width / 2, -height / 2, width, height, height / 2);
    ctx.fill();
    ctx.restore();
  }

  function drawBlobParty(theme, square) {
    ctx.strokeStyle = theme.ink;
    ctx.lineWidth = 3;
    if (square) {
      organicBlob(760, 750, 270, 270, theme.blobs[0], 0.11);
      organicBlob(947, 584, 94, 82, theme.blobs[1], 0.17);
      organicBlob(922, 965, 126, 94, theme.blobs[2], 0.13);
      organicBlob(475, 924, 58, 44, theme.blobs[3], 0.18);
      ctx.beginPath(); ctx.arc(535, 594, 31, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.arc(962, 870, 88, Math.PI * 1.05, Math.PI * 1.65); ctx.stroke();
    } else {
      organicBlob(1015, 350, 226, 245, theme.blobs[0], 0.11);
      organicBlob(1162, 150, 82, 68, theme.blobs[1], 0.17);
      organicBlob(1200, 586, 96, 76, theme.blobs[2], 0.13);
      organicBlob(786, 594, 48, 38, theme.blobs[3], 0.18);
      ctx.beginPath(); ctx.arc(850, 143, 27, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.arc(1190, 585, 75, Math.PI * 1.05, Math.PI * 1.65); ctx.stroke();
    }
  }

  function drawSunburst(theme, square) {
    const cx = square ? 750 : 1010;
    const cy = square ? 750 : 365;
    sunburst(cx, cy, square ? 225 : 205, square ? 310 : 280, 22, theme.blobs[0]);
    sunburst(cx + (square ? 205 : 180), cy - (square ? 175 : 165), 34, 62, 12, theme.blobs[2]);
    ctx.fillStyle = theme.blobs[1];
    ctx.beginPath(); ctx.arc(cx - 230, cy + 180, 54, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = theme.ink;
    ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(cx, cy, square ? 335 : 300, 0.15, 1.45); ctx.stroke();
  }

  function drawRibbons(theme, square) {
    ctx.save();
    ctx.lineCap = "round";
    const shiftX = square ? -160 : 0;
    const shiftY = square ? 365 : 0;
    const ribbons = [
      { color: theme.blobs[0], width: 92, y: 245 },
      { color: theme.blobs[1], width: 48, y: 390 },
      { color: theme.blobs[2], width: 64, y: 535 },
    ];
    for (const ribbon of ribbons) {
      ctx.beginPath();
      ctx.moveTo(760 + shiftX, ribbon.y + shiftY);
      ctx.bezierCurveTo(880 + shiftX, ribbon.y - 110 + shiftY, 1040 + shiftX, ribbon.y + 120 + shiftY, 1270 + shiftX, ribbon.y - 20 + shiftY);
      ctx.strokeStyle = ribbon.color;
      ctx.lineWidth = ribbon.width;
      ctx.stroke();
    }
    ctx.strokeStyle = theme.ink;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(785 + shiftX, 175 + shiftY);
    ctx.bezierCurveTo(930 + shiftX, 80 + shiftY, 1090 + shiftX, 250 + shiftY, 1245 + shiftX, 125 + shiftY);
    ctx.stroke();
    ctx.restore();
  }

  function drawConfetti(theme, square) {
    const offsetX = square ? -155 : 0;
    const offsetY = square ? 365 : 0;
    const pieces = [
      [810, 170, 82, 28, -0.45, 0], [930, 125, 38, 38, 0.2, 1],
      [1130, 180, 96, 30, 0.6, 2], [1210, 320, 54, 24, -0.3, 3],
      [790, 420, 56, 24, 0.75, 2], [890, 570, 92, 28, -0.6, 1],
      [1085, 605, 42, 42, 0.1, 3], [1220, 545, 84, 26, 0.45, 0],
      [1010, 250, 54, 20, -0.8, 3], [1030, 495, 70, 24, 0.35, 2],
    ];
    for (const [x, y, w, h, angle, color] of pieces) {
      capsule(x + offsetX, y + offsetY, w, h, angle, theme.blobs[color]);
    }
    ctx.strokeStyle = theme.ink;
    ctx.lineWidth = 3;
    const cx = square ? 760 : 1010;
    const cy = square ? 750 : 360;
    ctx.beginPath(); ctx.arc(cx, cy, square ? 270 : 250, 0, Math.PI * 2); ctx.stroke();
  }

  function drawEditorialZest(theme, square) {
    const cx = square ? 760 : 1030;
    const cy = square ? 760 : 360;
    organicBlob(cx, cy, square ? 245 : 205, square ? 245 : 225, theme.blobs[0], 0.08);
    ctx.fillStyle = theme.blobs[3];
    ctx.fillRect(cx - (square ? 300 : 285), cy + (square ? 185 : 170), 82, 18);
    ctx.fillStyle = theme.blobs[2];
    ctx.beginPath(); ctx.arc(cx + 200, cy - 205, 46, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = theme.ink;
    ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(cx, cy, square ? 300 : 265, -0.65, 0.75); ctx.stroke();
  }

  function drawTangyTreatment(theme) {
    const square = elements.format.value === "square";
    const treatment = elements.tangyStyle.value;
    if (treatment === "burst") drawSunburst(theme, square);
    else if (treatment === "ribbons") drawRibbons(theme, square);
    else if (treatment === "confetti") drawConfetti(theme, square);
    else if (treatment === "minimal") drawEditorialZest(theme, square);
    else drawBlobParty(theme, square);
  }

  function drawBackground(theme) {
    const format = activeFormat();
    const W = format.width;
    const H = format.height;
    ctx.fillStyle = theme.canvas;
    ctx.fillRect(0, 0, W, H);

    if (elements.showDots.checked) {
      ctx.fillStyle = theme.dot;
      for (let y = 10; y < H; y += 14) {
        for (let x = 10; x < W; x += 14) {
          ctx.beginPath();
          ctx.arc(x, y, 1.15, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }

    if (elements.showBlobs.checked) {
      drawTangyTreatment(theme);
    }
  }

  function wrapLine(text, maxWidth) {
    const words = text.trim().split(/\s+/).filter(Boolean);
    const lines = [];
    let current = "";
    for (const word of words) {
      const trial = current ? `${current} ${word}` : word;
      if (!current || ctx.measureText(trial).width <= maxWidth) current = trial;
      else { lines.push(current); current = word; }
    }
    if (current) lines.push(current);
    return lines;
  }

  function wrapMultiline(text, maxWidth) {
    return text.split("\n").flatMap((paragraph) => paragraph.trim() ? wrapLine(paragraph, maxWidth) : [""]);
  }

  function fitHeadline(text, format) {
    for (let size = format.headlineMax; size >= 44; size -= 2) {
      ctx.font = `700 ${size}px Georgia, "Times New Roman", serif`;
      const lines = wrapMultiline(text, format.headlineWidth);
      if (lines.length <= 3) return { size, lines };
    }
    ctx.font = '700 42px Georgia, "Times New Roman", serif';
    return { size: 42, lines: wrapMultiline(text, format.headlineWidth) };
  }

  function drawTrackedText(text, x, y, spacing, theme) {
    ctx.fillStyle = theme.muted;
    ctx.font = '20px "Courier New", ui-monospace, monospace';
    for (const character of text.toUpperCase()) {
      ctx.fillText(character, x, y);
      x += ctx.measureText(character).width + spacing;
    }
  }

  function drawCopy(theme) {
    const format = activeFormat();
    drawTrackedText(elements.eyebrow.value || "A NOTE FROM OREO", format.margin, format.eyebrowY, 5, theme);

    const fitted = fitHeadline(elements.headline.value || "Untitled note", format);
    ctx.fillStyle = theme.ink;
    ctx.textBaseline = "alphabetic";
    ctx.font = `700 ${fitted.size}px Georgia, "Times New Roman", serif`;
    const lineHeight = fitted.size * 1.08;
    let y = format.headlineY;
    for (const line of fitted.lines) {
      ctx.fillText(line, format.margin, y);
      y += lineHeight;
    }

    const underlineY = y - fitted.size * 0.15;
    ctx.fillStyle = theme.accent;
    ctx.beginPath();
    ctx.roundRect(format.margin, underlineY, elements.format.value === "square" ? 360 : 320, 10, 5);
    ctx.fill();

    ctx.fillStyle = theme.slate;
    ctx.font = '22px Inter, Arial, sans-serif';
    let descriptionY = underlineY + 56;
    for (const line of wrapMultiline(elements.description.value, format.descriptionWidth)) {
      ctx.fillText(line, format.margin, descriptionY);
      descriptionY += 32;
    }

    drawTrackedText(elements.url.value, format.margin, format.urlY, 2, theme);
  }

  function cropTransparentImage(image) {
    const source = document.createElement("canvas");
    source.width = image.naturalWidth || image.width;
    source.height = image.naturalHeight || image.height;
    const sourceCtx = source.getContext("2d", { willReadFrequently: true });
    sourceCtx.drawImage(image, 0, 0);
    const pixels = sourceCtx.getImageData(0, 0, source.width, source.height).data;
    let left = source.width, top = source.height, right = -1, bottom = -1;

    for (let y = 0; y < source.height; y += 1) {
      for (let x = 0; x < source.width; x += 1) {
        if (pixels[(y * source.width + x) * 4 + 3] > 8) {
          if (x < left) left = x;
          if (x > right) right = x;
          if (y < top) top = y;
          if (y > bottom) bottom = y;
        }
      }
    }

    if (right < left || bottom < top) return source;
    const cropped = document.createElement("canvas");
    cropped.width = right - left + 1;
    cropped.height = bottom - top + 1;
    cropped.getContext("2d").drawImage(source, left, top, cropped.width, cropped.height, 0, 0, cropped.width, cropped.height);
    return cropped;
  }

  function drawSticker() {
    if (!stickerCrop) return;
    const format = activeFormat();
    const scale = Number(elements.scale.value) / 100;
    const fit = Math.min(format.sticker.maxWidth / stickerCrop.width, format.sticker.maxHeight / stickerCrop.height) * scale;
    const width = stickerCrop.width * fit;
    const height = stickerCrop.height * fit;
    const x = Number(elements.x.value) - width / 2;
    const y = Number(elements.y.value) - height / 2;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(stickerCrop, x, y, width, height);
  }

  function render() {
    const theme = themes[elements.theme.value] || themes.sunset;
    const format = activeFormat();
    if (canvas.width !== format.width || canvas.height !== format.height) {
      canvas.width = format.width;
      canvas.height = format.height;
    }
    drawBackground(theme);
    drawSticker();
    drawCopy(theme);
    elements.scaleOutput.value = `${elements.scale.value}%`;
    elements.xOutput.value = elements.x.value;
    elements.yOutput.value = elements.y.value;
    elements.dimensions.textContent = format.label;
  }

  function setStatus(message, isError = false) {
    elements.stickerStatus.textContent = message;
    elements.stickerStatus.classList.toggle("error", isError);
  }

  function loadStickerUrl(url, label) {
    const image = new Image();
    image.onload = () => {
      stickerImage = image;
      stickerCrop = cropTransparentImage(image);
      setStatus(`Using ${label}`);
      render();
    };
    image.onerror = () => setStatus(`Could not load ${label}. Serve the repo locally or upload the file.`, true);
    image.src = url;
  }

  function loadRepoSticker(filename) {
    const clean = filename.trim().replace(/^\/?stickers\//, "").replace(/^\/+/, "");
    if (!clean) return;
    if (clean.split("/").includes("..")) {
      setStatus("Sticker paths cannot leave the stickers folder.", true);
      return;
    }
    const withExtension = /\.(png|webp)$/i.test(clean) ? clean : `${clean}.png`;
    const encodedPath = withExtension.split("/").map(encodeURIComponent).join("/");
    loadStickerUrl(`../stickers/${encodedPath}`, withExtension);
  }

  function reset() {
    elements.stickerSelect.value = defaults.sticker;
    elements.stickerName.value = "";
    elements.eyebrow.value = defaults.eyebrow;
    elements.headline.value = defaults.headline;
    elements.description.value = defaults.description;
    elements.url.value = defaults.url;
    elements.theme.value = defaults.theme;
    elements.tangyStyle.value = defaults.tangyStyle;
    elements.format.value = defaults.format;
    const format = activeFormat();
    elements.x.min = format.sticker.minX;
    elements.x.max = format.sticker.maxX;
    elements.y.min = format.sticker.minY;
    elements.y.max = format.sticker.maxY;
    elements.scale.value = defaults.scale;
    elements.x.value = format.sticker.x;
    elements.y.value = format.sticker.y;
    elements.showDots.checked = true;
    elements.showBlobs.checked = true;
    loadRepoSticker(defaults.sticker);
  }

  function applyFormatDefaults() {
    const format = activeFormat();
    elements.x.min = format.sticker.minX;
    elements.x.max = format.sticker.maxX;
    elements.y.min = format.sticker.minY;
    elements.y.max = format.sticker.maxY;
    elements.x.value = format.sticker.x;
    elements.y.value = format.sticker.y;
    elements.scale.value = elements.format.value === "square" ? "90" : defaults.scale;
    render();
  }

  function slugify(value) {
    return value.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "oreo-outreach";
  }

  function download() {
    render();
    canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${slugify(elements.headline.value)}-${elements.format.value}.png`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }, "image/png");
  }

  elements.stickerSelect.addEventListener("change", () => loadRepoSticker(elements.stickerSelect.value));
  elements.loadSticker.addEventListener("click", () => loadRepoSticker(elements.stickerName.value));
  elements.stickerName.addEventListener("keydown", (event) => {
    if (event.key === "Enter") { event.preventDefault(); loadRepoSticker(elements.stickerName.value); }
  });
  elements.stickerUpload.addEventListener("change", () => {
    const file = elements.stickerUpload.files[0];
    if (!file) return;
    if (uploadedObjectUrl) URL.revokeObjectURL(uploadedObjectUrl);
    uploadedObjectUrl = URL.createObjectURL(file);
    loadStickerUrl(uploadedObjectUrl, file.name);
  });

  [elements.eyebrow, elements.headline, elements.description, elements.url].forEach((input) => input.addEventListener("input", render));
  elements.format.addEventListener("change", applyFormatDefaults);
  [elements.theme, elements.tangyStyle, elements.scale, elements.x, elements.y, elements.showDots, elements.showBlobs].forEach((input) => input.addEventListener("input", render));
  elements.reset.addEventListener("click", reset);
  elements.download.addEventListener("click", download);

  reset();
})();
