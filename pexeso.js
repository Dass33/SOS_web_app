/* ==========================================================================
   Senohrabské pexeso
   Vanilla JS, žádné závislosti. Obrázky leží v assets/pexeso/ jako čtverce.
   Dokud tam nějaký chybí, karta se vykreslí jako barevné políčko s číslem,
   takže hra funguje pořád.
   ========================================================================== */

(function () {
  "use strict";

  /* Šestnáct motivů — z každého je jedna dvojice, dohromady 32 karet.
     Popisek (alt) čte hlasová čtečka. Soubory vyrábí tools/crop-pexeso.py. */
  var MOTIFS = [
    { src: "assets/pexeso/hlaska-1.webp", alt: "Schody k Hlásce" },
    { src: "assets/pexeso/hlaska-2.webp", alt: "Vyhlídka Hláska" },
    { src: "assets/pexeso/kaple.webp", alt: "Kaple svatého Vojtěcha" },
    { src: "assets/pexeso/obecni-urad.webp", alt: "Obecní úřad" },
    { src: "assets/pexeso/plovarna.webp", alt: "Kabinky na plovárně" },
    { src: "assets/pexeso/poddubi-1.webp", alt: "Chata v Poddubí" },
    { src: "assets/pexeso/poddubi-2.webp", alt: "Les v Poddubí" },
    { src: "assets/pexeso/rybarska-chata.webp", alt: "Rybářská chata u vody" },
    { src: "assets/pexeso/u-altanu.webp", alt: "Jinovatka U Altánu" },
    { src: "assets/pexeso/chaty-za-trati.webp", alt: "Chata za tratí" },
    { src: "assets/pexeso/k-nadrazi.webp", alt: "Zasněžená cesta k nádraží" },
    { src: "assets/pexeso/hlavni.webp", alt: "Zasněžená Hlavní ulice" },
    { src: "assets/pexeso/borovice.webp", alt: "Borovice v jinovatce" },
    { src: "assets/pexeso/houba.webp", alt: "Muchomůrka červená" },
    { src: "assets/pexeso/tuscany-superb.webp", alt: "Růže Tuscany Superb" },
    { src: "assets/pexeso/jezek.webp", alt: "Ježek mezi šiškami" }
  ];

  /* Náhradní barvy políček — jedenáct pilířů programu z letáku.
     U světlých se píše tmavě, stejně jako na hlavní stránce. */
  var COLORS = [
    { token: "--p1", light: true },
    { token: "--p2", light: true },
    { token: "--p3", light: false },
    { token: "--p4", light: true },
    { token: "--p5", light: false },
    { token: "--p6", light: false },
    { token: "--p7", light: false },
    { token: "--p8", light: false },
    { token: "--p9", light: false },
    { token: "--p10", light: true },
    { token: "--p11", light: false },
  ];

  var HIDE_DELAY = 900;
  var STORE_KEY = "sos-pexeso-rekord";

  var el = {
    board: document.getElementById("hra-deska"),
    moves: document.getElementById("hra-tahy"),
    time: document.getElementById("hra-cas"),
    best: document.getElementById("hra-rekord"),
    status: document.getElementById("hra-stav"),
    win: document.getElementById("hra-vyhra"),
    winText: document.getElementById("hra-vyhra-text"),
    newGame: document.getElementById("hra-nova"),
    again: document.getElementById("hra-znovu"),
  };

  if (!el.board) return;

  var state = {
    first: null,
    second: null,
    pending: null,
    moves: 0,
    found: 0,
    started: false,
    finished: false,
    tick: null,
    startTime: 0,
  };

  /* --- Pomocné ----------------------------------------------------------- */

  function plural(n, one, few, many) {
    if (n === 1) return one;
    if (n >= 2 && n <= 4) return few;
    return many;
  }

  function formatTime(seconds) {
    var m = Math.floor(seconds / 60);
    var s = seconds % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  function elapsed() {
    if (!state.started) return 0;
    return Math.floor((Date.now() - state.startTime) / 1000);
  }

  function shuffle(list) {
    for (var i = list.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = list[i];
      list[i] = list[j];
      list[j] = tmp;
    }
    return list;
  }

  function readBest() {
    try {
      return JSON.parse(localStorage.getItem(STORE_KEY));
    } catch (e) {
      return null;
    }
  }

  function writeBest(record) {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(record));
    } catch (e) {
      /* soukromé okno nebo zakázané úložiště — rekord prostě neuložíme */
    }
  }

  /* --- Vykreslení -------------------------------------------------------- */

  function makeCard(motif, index, position) {
    var color = COLORS[index % COLORS.length];

    var button = document.createElement("button");
    button.type = "button";
    button.className = "card";
    button.dataset.key = String(index);
    button.dataset.position = String(position);
    button.setAttribute("aria-label", "Karta " + position);

    var inner = document.createElement("span");
    inner.className = "card__inner";

    var cover = document.createElement("span");
    cover.className = "card__face card__cover";
    var mark = document.createElement("img");
    mark.src = "assets/img/znak-sos.png";
    mark.alt = "";
    cover.appendChild(mark);

    var photo = document.createElement("span");
    photo.className =
      "card__face card__photo" + (color.light ? " is-light" : "");
    photo.style.setProperty("--c", "var(" + color.token + ")");

    var num = document.createElement("span");
    num.className = "card__num";
    num.textContent = String(index + 1);
    photo.appendChild(num);

    var img = document.createElement("img");
    img.src = motif.src;
    img.alt = "";
    img.decoding = "async";
    img.addEventListener("error", function () {
      /* fotka chybí — zůstane barevné políčko s číslem */
      img.remove();
    });
    photo.appendChild(img);

    inner.appendChild(cover);
    inner.appendChild(photo);
    button.appendChild(inner);

    button.addEventListener("click", function () {
      onCardClick(button, motif, position);
    });

    return button;
  }

  function render() {
    el.moves.textContent = String(state.moves);
    el.time.textContent = formatTime(elapsed());

    var best = readBest();
    el.best.textContent = best
      ? best.moves +
        " " +
        plural(best.moves, "tah", "tahy", "tahů") +
        " · " +
        formatTime(best.seconds)
      : "—";
  }

  function say(text) {
    el.status.textContent = text;
  }

  /* --- Průběh hry -------------------------------------------------------- */

  function startGame() {
    stopTimer();

    state.first = null;
    state.second = null;
    state.pending = null;
    state.moves = 0;
    state.found = 0;
    state.started = false;
    state.finished = false;
    state.startTime = 0;

    el.win.hidden = true;

    var deck = shuffle(
      MOTIFS.map(function (motif, i) {
        return { motif: motif, index: i };
      }).reduce(function (all, item) {
        return all.concat([item, item]);
      }, []),
    );

    el.board.textContent = "";
    deck.forEach(function (item, position) {
      el.board.appendChild(makeCard(item.motif, item.index, position + 1));
    });

    render();
    say("");
  }

  function startTimer() {
    state.started = true;
    state.startTime = Date.now();
    state.tick = window.setInterval(function () {
      el.time.textContent = formatTime(elapsed());
    }, 1000);
  }

  function stopTimer() {
    if (state.tick) window.clearInterval(state.tick);
    state.tick = null;
  }

  function flipDownPending() {
    if (!state.pending) return;
    window.clearTimeout(state.pending);
    state.pending = null;

    [state.first, state.second].forEach(function (card) {
      if (!card) return;
      card.classList.remove("is-up", "is-wrong");
      card.setAttribute("aria-label", "Karta " + card.dataset.position);
    });
    state.first = null;
    state.second = null;
  }

  function onCardClick(card, motif, position) {
    if (state.finished) return;

    /* Kliknutí do prodlevy nečeká — nesedící dvojici rovnou otočí zpět. */
    if (state.pending) flipDownPending();

    if (card.classList.contains("is-matched")) return;
    if (card === state.first) return;

    if (!state.started) startTimer();

    card.classList.add("is-up");
    card.setAttribute("aria-label", "Karta " + position + ": " + motif.alt);

    if (!state.first) {
      state.first = card;
      return;
    }

    state.second = card;
    state.moves += 1;
    render();

    if (state.first.dataset.key === card.dataset.key) {
      matchFound(motif);
    } else {
      state.first.classList.add("is-wrong");
      card.classList.add("is-wrong");
      say("Vedle.");
      state.pending = window.setTimeout(flipDownPending, HIDE_DELAY);
    }
  }

  function matchFound(motif) {
    [state.first, state.second].forEach(function (card) {
      card.classList.remove("is-up");
      card.classList.add("is-matched");
      card.disabled = true;
    });
    state.first = null;
    state.second = null;
    state.found += 1;
    render();

    var left = MOTIFS.length - state.found;
    if (left > 0) {
      say(
        motif.alt +
          " — zbývá " +
          left +
          " " +
          plural(left, "dvojice", "dvojice", "dvojic") +
          ".",
      );
    } else {
      finish();
    }
  }

  function finish() {
    var seconds = elapsed();
    stopTimer();
    state.finished = true;

    var best = readBest();
    var isRecord =
      !best ||
      state.moves < best.moves ||
      (state.moves === best.moves && seconds < best.seconds);
    if (isRecord) writeBest({ moves: state.moves, seconds: seconds });
    render();

    var text =
      "Všech " +
      MOTIFS.length +
      " dvojic na " +
      state.moves +
      " " +
      plural(state.moves, "tah", "tahy", "tahů") +
      " za " +
      formatTime(seconds) +
      ".";
    if (isRecord && best) text += " Nový rekord!";
    else if (!isRecord) {
      text +=
        " Váš rekord je " +
        best.moves +
        " " +
        plural(best.moves, "tah", "tahy", "tahů") +
        ".";
    }

    el.winText.textContent = text;
    el.win.hidden = false;
    say(text);
    el.again.focus();
  }

  /* --- Ovládání ---------------------------------------------------------- */

  function restart() {
    startGame();
    el.board.querySelector(".card").focus();
  }

  el.newGame.addEventListener("click", restart);
  el.again.addEventListener("click", restart);

  startGame();
})();
