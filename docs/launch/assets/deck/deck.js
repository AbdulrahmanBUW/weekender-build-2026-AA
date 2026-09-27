/* Ankommen demo deck engine + slide choreography (GSAP). Offline, file:// safe.
   Keys: Right/Space/PageDown/click = next build · Left/PageUp = back · Home/End · F fullscreen ·
   N notes · O overview · B black · A replay step (audio) · M mute · V backup video · digits+Enter jump. */
(function () {
  'use strict';
  var D = window.DECK_DATA || {};
  D.audio = D.audio || {}; D.callTimeline = D.callTimeline || []; D.intakeTimeline = D.intakeTimeline || [];
  D.n8n = D.n8n || []; D.screens = D.screens || []; D.ivrWave = D.ivrWave || [];
  if (window.gsap) gsap.registerPlugin(window.DrawSVGPlugin, window.MotionPathPlugin, window.CustomEase);

  // English app voice for the language beat. Default: ElevenLabs Sarah (lang_en_sarah), the same assistant voice as
  // RU/UK/AR/TR (27 Sep: the team asked for the English voice to change). ?en=helena plays the old Deepgram Helena take.
  var EN_CLIP = /[?&]en=helena\b/.test(location.search) ? 'lang_en' : 'lang_en_sarah';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var stage = $('#stage');
  var EASE = 'power3.out';
  var PINE = '#1F5C4A', BORDER = '#D9D2C3';
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var SCREENS = {}; D.screens.forEach(function (s) { SCREENS[s.file] = s; });
  function hasShot(f) { return !D.screens.length || !!SCREENS[f]; }
  var CHECK_SVG = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1F5C4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m7.5 12.5 3 3 6-6.5"/></svg>';
  var CHECK_LIGHT = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#FFFDF8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7"/></svg>';

  // broken images degrade quietly
  document.addEventListener('error', function (e) {
    var t = e.target; if (t && t.tagName === 'IMG') { t.style.visibility = 'hidden'; t.setAttribute('data-missing', '1'); }
  }, true);

  // ------------------------------------------------------------------ audio
  var AU = {
    els: {}, cur: null, raf: 0, muted: false,
    get: function (id) {
      var a = this.els[id];
      if (!a) {
        a = document.createElement('audio'); a.preload = 'auto'; a.src = 'audio/' + id + '.mp3';
        a.setAttribute('data-audio', id); $('#audio-bank').appendChild(a); this.els[id] = a;
      }
      return a;
    },
    duration: function (id) {
      var a = this.els[id]; if (a && isFinite(a.duration) && a.duration > 0) return a.duration;
      var m = D.audio[id]; if (m && m.duration) return m.duration;
      var tl = id === 'call_full' ? D.callTimeline : id === 'intake_full' ? D.intakeTimeline : null;
      if (tl && tl.length) return tl[tl.length - 1].end + 0.3;
      return 6;
    },
    play: function (id, onFrame, onEnd) {
      this.stop();
      var self = this, a = this.get(id), me = { id: id, a: a, onFrame: onFrame, onEnd: onEnd, clock: false, t0: performance.now() };
      this.cur = me;
      try { a.currentTime = 0; } catch (e) { /* not loaded yet */ }
      a.muted = this.muted;
      var p = a.play(); if (p && p.catch) p.catch(function () { me.clock = true; me.t0 = performance.now(); });
      if (a.error) me.clock = true;
      a.onerror = function () { me.clock = true; };
      $('#speaking').classList.add('on');
      var dur = this.duration(id);
      var loop = function () {
        if (self.cur !== me) return;
        var t = me.clock ? (performance.now() - me.t0) / 1000 : a.currentTime;
        if (onFrame) onFrame(t, a);
        if ((me.clock && t > dur) || a.ended) { self._end(me); return; }
        self.raf = requestAnimationFrame(loop);
      };
      this.raf = requestAnimationFrame(loop);
      a.onended = function () { self._end(me); };
    },
    _end: function (me) {
      if (this.cur !== me) return;
      this.cur = null; cancelAnimationFrame(this.raf); $('#speaking').classList.remove('on');
      if (me.onFrame) me.onFrame(1e6, me.a);
      if (me.onEnd) me.onEnd();
    },
    stop: function () {
      if (this.cur) { var a = this.cur.a; a.onended = null; try { a.pause(); } catch (e) { } this.cur = null; }
      cancelAnimationFrame(this.raf); $('#speaking').classList.remove('on');
    },
    setMuted: function (v) {
      this.muted = v; var els = this.els; Object.keys(els).forEach(function (k) { els[k].muted = v; });
      $('#mutedflag').classList.toggle('on', v);
    }
  };

  // ------------------------------------------------------------------ word streaming
  function makeWords(container, words) {
    container.innerHTML = '';
    return words.map(function (w, i) {
      var s = el('span', 'w'); s.textContent = w.w; container.appendChild(s);
      if (i < words.length - 1) container.appendChild(document.createTextNode(' '));
      return s;
    });
  }
  function streamTo(spans, words, t) {
    for (var i = 0; i < spans.length; i++) {
      var on = t + 0.05 >= words[i].start;
      if (on !== spans[i]._on) { spans[i]._on = on; spans[i].classList.toggle('on', on); }
    }
  }
  function showAll(spans) { spans.forEach(function (s) { s._on = true; s.classList.add('on'); }); }
  function propWords(text, start, end) {
    var parts = String(text || '').split(/\s+/).filter(Boolean);
    var total = parts.reduce(function (a, p) { return a + p.length + 1; }, 0) || 1, acc = 0, dur = Math.max(0.6, end - start);
    return parts.map(function (p) { var w = { w: p, start: start + dur * 0.9 * (acc / total) }; acc += p.length + 1; return w; });
  }
  function clipWords(id, fallbackText) {
    var m = D.audio[id];
    if (m && m.words && m.words.length) return m.words;
    return propWords(fallbackText || (m && m.text) || '', 0, (m && m.duration) || 4);
  }
  function mmss(t) { t = Math.max(0, Math.floor(t)); return ('0' + Math.floor(t / 60)).slice(-2) + ':' + ('0' + (t % 60)).slice(-2); }

  // ------------------------------------------------------------------ slide registry + engine
  var SL = [];
  function slide(id, title, cfg) {
    var e = document.getElementById(id);
    SL.push(Object.assign({ id: id, title: title, el: e, tls: [], timers: [], stops: [] }, cfg));
  }
  function killSlide(S) {
    S.tls.forEach(function (t) { t.kill(); }); S.tls = [];
    S.timers.forEach(clearTimeout); S.timers = [];
    S.stops.forEach(function (f) { try { f(); } catch (e) { } }); S.stops = [];
    gsap.killTweensOf($$('*', S.el));
  }
  function mkCtx(S, anim) {
    return {
      anim: anim, S: S,
      tl: function (o) {
        var t = gsap.timeline(Object.assign({ defaults: { ease: EASE, duration: 0.6 } }, o || {}));
        if (!anim) t.pause();
        S.tls.push(t); return t;
      },
      later: function (fn, ms) { if (anim) S.timers.push(setTimeout(fn, ms)); },
      onStop: function (fn) { S.stops.push(fn); }
    };
  }
  function runBuild(S, i, anim) {
    var n0 = S.tls.length;
    S.builds[i](mkCtx(S, anim));
    if (!anim) for (var j = n0; j < S.tls.length; j++) S.tls[j].progress(1);
  }
  function titleIn(tl, S, at) {
    var t = $$('.h-slide, .sub', S.el);
    if (t.length) tl.fromTo(t, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.6, stagger: 0.08 }, at == null ? 0 : at);
    return tl;
  }

  var cur = { s: -1, k: 0 };
  function go(s, k, mode) {
    s = clamp(s | 0, 0, SL.length - 1);
    var S = SL[s];
    k = clamp(k | 0, 0, S.builds.length - 1);
    AU.stop(); closeVideo();
    var prevS = cur.s;
    if (mode === 'next' && s === prevS && k === cur.k + 1) {
      runBuild(S, k, true);
    } else {
      if (prevS !== s) {
        if (prevS >= 0) { var P = SL[prevS]; killSlide(P); P.el.classList.remove('active'); if (P.leave) P.leave(P); }
        S.el.classList.add('active');
      }
      killSlide(S);
      if (S.init) S.init(S);
      if (mode === 'replay') {
        for (var i = 0; i < k; i++) runBuild(S, i, false);
        runBuild(S, k, true);
      } else if (mode === 'next' && k === 0) {
        if (prevS !== s) gsap.fromTo(S.el, { opacity: 0 }, { opacity: 1, duration: 0.3, ease: 'power1.out' });
        runBuild(S, 0, true);
      } else {
        gsap.set(S.el, { opacity: 1 });
        for (var j = 0; j <= k; j++) runBuild(S, j, false);
      }
    }
    cur = { s: s, k: k };
    chrome();
  }
  function next() {
    if (cur.s < 0) return go(0, 0, 'next');
    var S = SL[cur.s];
    if (cur.k < S.builds.length - 1) go(cur.s, cur.k + 1, 'next');
    else if (cur.s < SL.length - 1) go(cur.s + 1, 0, 'next');
  }
  function prev() {
    if (cur.k > 0) go(cur.s, cur.k - 1, 'instant');
    else if (cur.s > 0) go(cur.s - 1, SL[cur.s - 1].builds.length - 1, 'instant');
  }
  var MAIN_COUNT = 0;
  function chrome() {
    var S = SL[cur.s];
    var frac = (cur.s + (cur.k + 1) / S.builds.length) / SL.length;
    $('#progress i').style.width = (frac * 100).toFixed(2) + '%';
    $('#counter').textContent = S.appendix ? ('Appendix ' + S.appendix) : ((cur.s + 1) + ' / ' + MAIN_COUNT);
    var h = '#' + (cur.s + 1) + '/' + cur.k;
    if (location.hash !== h) { try { history.replaceState(null, '', h); } catch (e) { location.hash = h; } }
    renderNotes();
    $$('#overview button').forEach(function (b, i) { b.classList.toggle('cur', i === cur.s); });
  }

  // ------------------------------------------------------------------ overlays
  function renderNotes() {
    var S = SL[cur.s]; if (!S) return;
    $('#notes').innerHTML = '<div class="nh">Slide ' + (cur.s + 1) + ' · ' + esc(S.title) + ' · build ' + (cur.k + 1) + ' of ' + S.builds.length + '</div>' + (S.notes || '');
  }
  function toggle(id, force) { var e = $(id); var on = force == null ? !e.classList.contains('on') : force; e.classList.toggle('on', on); return on; }
  var video = $('#video-ov video');
  function openVideo() {
    AU.stop();
    var ov = $('#video-ov'); ov.classList.remove('missing'); ov.classList.add('on');
    video.onerror = function () { ov.classList.add('missing'); };
    // Stage cut (1:49) by default; presentation.html?backup=full plays the full 2:29 walkthrough.
    var backupSrc = /[?&]backup=full\b/.test(location.search) ? 'video/demo/demo.mp4' : 'video/demo/demo_stage.mp4';
    if (!video.getAttribute('src') || video.error) { video.setAttribute('src', backupSrc); video.load(); }
    else { try { video.currentTime = 0; } catch (e) { } }
    var p = video.play(); if (p && p.catch) p.catch(function () { if (video.error) ov.classList.add('missing'); });
  }
  function closeVideo() { var ov = $('#video-ov'); if (ov.classList.contains('on')) { try { video.pause(); } catch (e) { } ov.classList.remove('on'); } }
  function toggleFs() {
    if (!document.fullscreenElement) { var r = document.documentElement.requestFullscreen; if (r) r.call(document.documentElement).catch(function () { }); }
    else if (document.exitFullscreen) document.exitFullscreen();
  }

  // =================================================================== SLIDES
  // helpers to split a wordmark into letters
  function splitChars(root) {
    $$('.an, .kommen', root).forEach(function (part) {
      if (part.getAttribute('data-split')) return;
      var txt = part.textContent; part.textContent = '';
      txt.split('').forEach(function (c) { var s = el('span', 'ch'); s.textContent = c; part.appendChild(s); });
      part.setAttribute('data-split', '1');
    });
    return $$('.ch', root);
  }

  // 1 · Title -----------------------------------------------------------
  slide('s-title', 'Title', {
    notes: '<b>3-minute slot route:</b> 1, then <b>5</b> (live demo, run-sheet 3.3), then <b>13</b> (pilot ask), then <b>14</b>. Use 6 and 7 only if the live call fails (type 6, Enter, then Right 3 times to reach the 63 s call). Slides 2-4 and 8-12 are for a longer slot or questions. Jump: type the slide number, then Enter.<br>' +
      '<b>Say:</b> Hello, we are Abdul and Anastasia. This is <b>Ankommen</b>, your guide to starting in Germany. We built it this weekend here in Dresden. It is live at ankommen-dresden.lovable.app.',
    init: function (S) {
      var ch = splitChars($('.wordmark', S.el));
      gsap.set(ch, { yPercent: 70, opacity: 0, rotation: 6, transformOrigin: '50% 100%' });
      gsap.set($('.tagline', S.el), { opacity: 0, y: 18 });
      gsap.set($$('.meta, .site', S.el), { opacity: 0, y: 14 });
      gsap.set($('.peek', S.el), { opacity: 0, x: 90 });
    },
    builds: [
      function (c) {
        var tl = c.tl();
        tl.to($$('.ch', c.S.el), { yPercent: 0, opacity: 1, rotation: 0, duration: 0.95, stagger: 0.055, ease: 'expo.out' })
          .to($('.tagline', c.S.el), { opacity: 1, y: 0, duration: 0.7 }, '-=0.45');
      },
      function (c) {
        var tl = c.tl();
        tl.to($('.peek', c.S.el), { opacity: 1, x: 0, duration: 0.9, ease: 'expo.out' })
          .to($$('.meta, .site', c.S.el), { opacity: 1, y: 0, stagger: 0.12 }, 0.15);
      }
    ]
  });

  // 2 · Problem ---------------------------------------------------------
  (function () {
    var waveBars = [], tickSpans = [], ivrWords = [];
    slide('s-problem', 'The moment parents stop', {
      notes: '<b>Say:</b> This is Maria. She is a proto-persona, not a real person. She is new in Dresden, her daughter is four, and she speaks Russian. ' +
        '<b>[click]</b> She finds a music course. And then the page says: trial lesson by phone appointment. In German. ' +
        '<b>[click]</b> So she calls, and this is what she hears. (Let the phone menu play, 12 s.) ' +
        '<b>[click]</b> 65 percent of immigrants in Germany say German is the biggest obstacle in everyday life (OECD 2024). This is where parents stop.',
      init: function (S) {
        var wave = $('.wave', S.el);
        if (!waveBars.length) {
          var peaks = D.ivrWave.length ? D.ivrWave : Array.apply(null, Array(120)).map(function (_, i) { return 0.3 + 0.5 * Math.abs(Math.sin(i * 0.7)); });
          peaks.forEach(function (p) { var b = el('i'); b.style.height = Math.max(3, Math.round(p * 120)) + 'px'; wave.appendChild(b); waveBars.push(b); });
          ivrWords = clipWords('ivr_de');
          tickSpans = makeWords($('.strip', S.el), ivrWords);
        }
        waveBars.forEach(function (b) { b.classList.remove('on'); });
        tickSpans.forEach(function (s) { s.style.opacity = 0; s.classList.remove('old', 'on'); s.classList.remove('w'); });
        gsap.set($('.strip', S.el), { x: 0 });
        gsap.set($$('.h-slide', S.el), { opacity: 0 });
        gsap.set($('.persona', S.el), { opacity: 0, y: 24 });
        gsap.set($('.course', S.el), { opacity: 0, y: 24 });
        gsap.set($('.course .mark', S.el), { scaleX: 0 });
        gsap.set($('.course .gloss', S.el), { opacity: 0 });
        gsap.set($('.ivr', S.el), { opacity: 0, y: 20 });
        gsap.set($('.oecd', S.el), { opacity: 0, y: 20 });
        $('.oecd .pct', S.el).textContent = '0%';
      },
      builds: [
        function (c) { var tl = c.tl(); titleIn(tl, c.S); tl.to($('.persona', c.S.el), { opacity: 1, y: 0, duration: 0.7 }, 0.2); },
        function (c) {
          var tl = c.tl();
          tl.to($('.course', c.S.el), { opacity: 1, y: 0, duration: 0.7 })
            .to($('.course .mark', c.S.el), { scaleX: 1, duration: 0.8, ease: 'power2.inOut' }, '+=0.25')
            .to($('.course .gloss', c.S.el), { opacity: 1, duration: 0.5 }, '-=0.1');
        },
        function (c) {
          var S = c.S, tl = c.tl(), strip = $('.strip', S.el);
          tl.to($('.ivr', S.el), { opacity: 1, y: 0, duration: 0.5 });
          var dur = AU.duration('ivr_de');
          var render = function (t) {
            var f = clamp(t / dur, 0, 1), n = Math.round(f * waveBars.length);
            for (var i = 0; i < waveBars.length; i++) { var on = i < n; if (waveBars[i]._on !== on) { waveBars[i]._on = on; waveBars[i].classList.toggle('on', on); } }
            var last = -1;
            for (var j = 0; j < tickSpans.length; j++) {
              var vis = t + 0.05 >= ivrWords[j].start;
              if (vis) last = j;
              tickSpans[j].style.opacity = vis ? '' : 0;
            }
            for (var k = 0; k < tickSpans.length; k++) tickSpans[k].classList.toggle('old', k < last - 2);
            if (last >= 0) {
              var sp = tickSpans[last], right = sp.offsetLeft + sp.offsetWidth;
              var target = Math.min(0, 980 - right);
              var curX = gsap.getProperty(strip, 'x') || 0;
              gsap.set(strip, { x: curX + (target - curX) * 0.35 });
            }
          };
          if (c.anim) {
            AU.play('ivr_de', function (t) { render(t); });
          } else {
            waveBars.forEach(function (b) { b._on = true; b.classList.add('on'); });
            tickSpans.forEach(function (s, i) { s.style.opacity = ''; s.classList.toggle('old', i < tickSpans.length - 3); });
            var lastSp = tickSpans[tickSpans.length - 1];
            if (lastSp) gsap.set(strip, { x: Math.min(0, 980 - (lastSp.offsetLeft + lastSp.offsetWidth)) });
          }
        },
        function (c) {
          var tl = c.tl(), num = $('.oecd .pct', c.S.el);
          tl.to($('.oecd', c.S.el), { opacity: 1, y: 0, duration: 0.6 });
          if (c.anim) { var o = { v: 0 }; tl.to(o, { v: 65, duration: 1.4, ease: 'power2.out', onUpdate: function () { num.textContent = Math.round(o.v) + '%'; } }, 0.1); }
          else num.textContent = '65%';
        }
      ]
    });
  })();

  // 3 · One place --------------------------------------------------------
  (function () {
    // screenshot: browser left 600, top 250, width 1220 -> image 1218 wide from x=601, y=302 (50 px bar); source display coords are 2000 wide
    var F = 1218 / 2000, X0 = 601, Y0 = 302;
    var P = [
      { en: 'Courses & activities', cx: 788, w: 177, row: 'a', anchor: 'right' },
      { en: 'Events', cx: 977, w: 145, row: 'b' },
      { en: 'Communities', cx: 1142, w: 129, row: 'a' },
      { en: 'Health & services', cx: 1333, w: 194, row: 'b' },
      { en: 'Library', cx: 1523, w: 129, row: 'a' }
    ];
    var built = false;
    slide('s-place', 'Ankommen: one place', {
      notes: '<b>Say:</b> Ankommen is one place for international families. <b>[click x5]</b> Courses and activities. Events. Bilingual communities. Health and services: doctors, pharmacies, offices. And a library of guides, in six languages. ' +
        '<b>[click]</b> And on every page there is one button: <b>Call for me</b>.',
      init: function (S) {
        var layer = $('.layer-pillars', S.el);
        if (!built) {
          built = true;
          P.forEach(function (p, i) {
            var x = X0 + p.cx * F, y = Y0 + 48 * F, w = p.w * F + 18, h = 40;
            var ring = el('div', 'ring'); ring.style.cssText = 'left:' + (x - w / 2) + 'px;top:' + (y - h / 2) + 'px;width:' + w + 'px;height:' + h + 'px';
            var labTop = p.row === 'a' ? 188 : 116;
            var line = el('div', 'lead-line'); line.style.cssText = 'left:' + (x - 1) + 'px;top:' + (labTop + 36) + 'px;height:' + (y - h / 2 - labTop - 36) + 'px';
            var lab = el('div', 'pillar', esc(p.en));
            lab.style.top = labTop + 'px';
            if (p.anchor === 'right') { lab.style.left = (x + 16) + 'px'; lab.setAttribute('data-xp', '-100'); }
            else { lab.style.left = x + 'px'; lab.setAttribute('data-xp', '-50'); }
            [ring, line, lab].forEach(function (e) { e.setAttribute('data-p', i); layer.appendChild(e); });
          });
          var fx = X0 + 1927 * F, fy = Y0 + 1177 * F;
          var fr = el('div', 'fab-ring'); fr.style.cssText = 'left:' + (fx - 36) + 'px;top:' + (fy - 36) + 'px;width:72px;height:72px';
          var fr2 = el('div', 'fab-ring pulse2'); fr2.style.cssText = fr.style.cssText;
          var fl = el('div', 'fab-label', 'Call for me<small>on every page</small>');
          fl.style.cssText = 'left:' + (fx - 50) + 'px;top:' + (fy - 6) + 'px';
          layer.appendChild(fr); layer.appendChild(fr2); layer.appendChild(fl);
        }
        gsap.set($$('.h-slide', S.el), { opacity: 0 });
        gsap.set($('.lead', S.el), { opacity: 0, y: 14 });
        gsap.set($('.browser', S.el), { opacity: 0, y: 40 });
        gsap.set($$('.ring', layer), { opacity: 0, scale: 1.25 });
        gsap.set($$('.lead-line', layer), { scaleY: 0 });
        $$('.pillar', layer).forEach(function (l) { gsap.set(l, { xPercent: +l.getAttribute('data-xp'), opacity: 0, y: 10 }); });
        gsap.set($$('.fab-ring', layer), { opacity: 0, scale: 1 });
        gsap.set($('.fab-label', layer), { xPercent: -100, yPercent: -50, opacity: 0, x: 20 });
      },
      builds: [
        function (c) {
          var tl = c.tl(); titleIn(tl, c.S);
          tl.to($('.lead', c.S.el), { opacity: 1, y: 0 }, 0.15).to($('.browser', c.S.el), { opacity: 1, y: 0, duration: 0.9, ease: 'expo.out' }, 0.1);
        }
      ].concat(P.map(function (p, i) {
        return function (c) {
          var L = $('.layer-pillars', c.S.el), sel = '[data-p="' + i + '"]';
          var tl = c.tl();
          tl.to($$('.ring' + sel, L), { opacity: 1, scale: 1, duration: 0.45 })
            .to($$('.lead-line' + sel, L), { scaleY: 1, duration: 0.4, transformOrigin: '50% 100%' }, 0.1)
            .to($$('.pillar' + sel, L), { opacity: 1, y: 0, duration: 0.45 }, 0.3);
          if (i > 0) tl.to($$('.ring[data-p="' + (i - 1) + '"]', L), { opacity: 0.45, duration: 0.3 }, 0);
        };
      })).concat([
        function (c) {
          var L = $('.layer-pillars', c.S.el), tl = c.tl();
          tl.to($$('.ring', L), { opacity: 0.3, duration: 0.3 }, 0)
            .to($$('.fab-ring', L)[0], { opacity: 1, duration: 0.3 }, 0)
            .fromTo($$('.fab-ring', L)[1], { opacity: 0.9, scale: 1 }, { opacity: 0, scale: 1.7, duration: 1.1, ease: 'power2.out', repeat: 2 }, 0.1)
            .to($('.fab-label', L), { opacity: 1, x: 0, duration: 0.5 }, 0.2);
        }
      ])
    });
  })();

  // 4 · Six languages ----------------------------------------------------
  (function () {
    var L = [
      { code: 'en', name: 'English', clip: function () { return EN_CLIP; }, gloss: '' },
      { code: 'de', name: 'Deutsch', gloss: '“I’ll call for you and tell you right away what they said.”' },
      { code: 'ru', name: 'Русский', cls: 'cy', gloss: '“I’ll call them in German for you and tell you the answer in Russian.”' },
      { code: 'uk', name: 'Українська', cls: 'cy', gloss: '“I’ll call in German for you and tell you the answer in Ukrainian.”' },
      { code: 'ar', name: 'العربية', cls: 'ar', gloss: '“I’ll call them in German for you and tell you the answer in Arabic.” Right to left.' },
      { code: 'tr', name: 'Türkçe', gloss: '“I’ll call them in German for you and tell you the answer in Turkish.”' }
    ];
    var EN_NAMES = { en: 'English', de: 'German', ru: 'Russian', uk: 'Ukrainian', ar: 'Arabic (right to left)', tr: 'Turkish' };
    var built = false;
    function setShot(S, code, c, tl) {
      var file = 'desktop-home-' + code + '.png';
      if (!hasShot(file)) return;
      var base = $('.shot img.base', S.el), alt = $('.shot img.alt', S.el);
      $('.lname', S.el).textContent = EN_NAMES[code];
      if (!c.anim) { base.src = 'assets/screens/' + file; gsap.set(alt, { opacity: 0 }); return; }
      alt.src = 'assets/screens/' + file;
      tl.fromTo(alt, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power1.out', onComplete: function () { base.src = alt.src; gsap.set(alt, { opacity: 0 }); } }, 0);
    }
    slide('s-langs', 'Six languages', {
      notes: '<b>Say:</b> Everything is in six languages: English, German, Russian, Ukrainian, Arabic from right to left, and Turkish. ' +
        'Each click plays the app assistant in that language. (6 clicks; you can skip ahead with 5 + Enter.)',
      init: function (S) {
        var box = $('.tiles', S.el);
        if (!built) {
          built = true;
          L.forEach(function (l) {
            var t = el('div', 'tile' + (l.cls === 'ar' ? ' ar-t' : l.cls === 'cy' ? ' cy' : ''));
            t.innerHTML = '<div class="nm" lang="' + l.code + '">' + esc(l.name) + '</div><div class="code">' + l.code.toUpperCase() + '</div>';
            box.appendChild(t);
          });
        }
        $$('.tile', box).forEach(function (t) { t.classList.remove('on', 'done'); });
        gsap.set($$('.tile', box), { opacity: 0, y: 16 });
        gsap.set($$('.h-slide', S.el), { opacity: 0 });
        gsap.set($('.browser', S.el), { opacity: 0, y: 30 });
        gsap.set($('.shotcap', S.el), { opacity: 0 });
        $('.say .who', S.el).textContent = ''; $('.say .line', S.el).innerHTML = ''; $('.say .gloss', S.el).textContent = '';
        $('.shot img.base', S.el).src = 'assets/screens/desktop-home-ru.png'; $('.lname', S.el).textContent = 'Russian';
        gsap.set($('.shot img.alt', S.el), { opacity: 0 });
      },
      builds: [
        function (c) {
          var tl = c.tl(); titleIn(tl, c.S);
          tl.to($$('.tile', c.S.el), { opacity: 1, y: 0, stagger: 0.07, duration: 0.5 }, 0.15)
            .to($('.browser', c.S.el), { opacity: 1, y: 0, duration: 0.8, ease: 'expo.out' }, 0.2)
            .to($('.shotcap', c.S.el), { opacity: 1 }, 0.6);
        }
      ].concat(L.map(function (l, i) {
        return function (c) {
          var S = c.S, tiles = $$('.tile', S.el), tl = c.tl();
          tiles.forEach(function (t, j) { t.classList.toggle('on', j === i); t.classList.toggle('done', j < i); });
          tl.fromTo(tiles[i], { scale: 0.96 }, { scale: 1, duration: 0.4, ease: 'back.out(2)' }, 0);
          var clip = l.clip ? l.clip() : 'lang_' + l.code;
          var line = $('.say .line', S.el);
          line.className = 'line stream' + (l.cls === 'cy' ? ' cy' : l.cls === 'ar' ? ' ar' : '');
          line.setAttribute('lang', l.code); line.setAttribute('dir', l.code === 'ar' ? 'rtl' : 'ltr');
          $('.say .who', S.el).textContent = 'Call for me · ' + EN_NAMES[l.code];
          var words = clipWords(clip);
          var spans = makeWords(line, words);
          var gloss = $('.say .gloss', S.el); gloss.textContent = l.gloss; gsap.set(gloss, { opacity: 0 });
          setShot(S, l.code, c, tl);
          if (c.anim) {
            AU.play(clip, function (t) { streamTo(spans, words, t); }, function () { gsap.to(gloss, { opacity: 1, duration: 0.5 }); });
          } else { showAll(spans); gsap.set(gloss, { opacity: 1 }); }
        };
      }))
    });
  })();

  // 5 · Live demo ---------------------------------------------------------
  slide('s-live', 'Live demo', {
    notes: '<b>Switch to the app tab</b> (interface in Русский). Path: Courses (age 3–6, music, Russian) · Olgas Musikstudio · <b>Call for me</b> · approval card · Call now · brief (about 10 s) · the call · result. ' +
      '<b>Say:</b> "Before anything happens, she sees exactly what it will say, including KI-Assistentin. She approves." During the call: "Listen to the first sentence." After the Saturday offer: "It said no. Maria did not approve Saturday." ' +
      '<b>If the live voice part fails:</b> "The live voice part failed. Here is a recording from this morning." For the call beat alone, go to slide 6 (type 6, Enter, then Right 3 times: the 63 s call). <b>V</b> plays the full 2:29 recording, which is almost the whole 3-minute slot.',
    init: function (S) {
      gsap.set($$('.big, .site, .actions, .backup, .flow', S.el), { opacity: 0, y: 18 });
      gsap.set($('.phone', S.el), { opacity: 0, y: 40 });
    },
    builds: [
      function (c) {
        var tl = c.tl();
        tl.to($$('.big, .site, .actions, .backup, .flow', c.S.el), { opacity: 1, y: 0, stagger: 0.09, duration: 0.6 })
          .to($('.phone', c.S.el), { opacity: 1, y: 0, duration: 0.9, ease: 'expo.out' }, 0.1);
      }
    ]
  });

  // 6 · Call for me, step by step ------------------------------------------
  (function () {
    var GLOSS = {
      intake_ru_1: 'Hello! I’ll call Olgas Musikstudio for you. What should I ask them?',
      maria_ru_1: 'Hello! I want to sign my daughter up for music. She is four. Tuesday or Thursday after three is best.',
      intake_ru_2: 'Got it. I’ll ask about a free place or a trial lesson on Tuesday or Thursday after 15:00. Shall I call them in German?',
      maria_ru_2: 'Yes, please call.'
    };
    var MOMENTS = ['Says it is an AI in the first sentence', 'Declines Saturday: Maria did not approve it', 'Reads everything back before it books'];
    // approval card pan targets (inner coords, see deck.css: header 84px, image 800 wide, top crop 94px)
    // last stop covers the consent box and the Call now button; approval-consent-ru.png (make_assets.py) fades in there
    var AP = [{ top: 92, h: 244, pan: 0 }, { top: 641, h: 162, pan: 401 }, { top: 826, h: 115, pan: 560 }, { top: 1212, h: 312, pan: 700 }];
    var bubbles = [], callBuilt = false;
    var callLines = D.callTimeline;
    function momentTimes() {
      var t = [];
      var l2 = callLines[1], l4 = callLines[3], l6 = callLines[5];
      function wordAt(line, re, dflt) { if (!line) return dflt; var ws = line.words || []; for (var i = 0; i < ws.length; i++) if (re.test(ws[i].w)) return ws[i].end; return line.start + 1; }
      t.push(wordAt(l2, /^KI-/, 5.6)); t.push(wordAt(l4, /^Samstag/, 28)); t.push(l6 ? l6.start + 0.6 : 44.6);
      return t;
    }
    function spkName(sp) { return sp === 'assistant' ? 'Assistant' : 'Musikstudio'; }
    function showView(tl, S, id) {
      var views = $$('.view', S.el), target = $('#' + id, S.el);
      views.forEach(function (v) { if (v !== target) tl.to(v, { autoAlpha: 0, x: -40, duration: 0.35, ease: 'power2.in' }, 0); });
      tl.fromTo(target, { autoAlpha: 0, x: 60 }, { autoAlpha: 1, x: 0, duration: 0.6 }, 0.3);
    }
    function stepper(S, n) { $$('.stepper .st', S.el).forEach(function (s, i) { s.classList.toggle('on', i === n - 1); s.classList.toggle('done', i < n - 1); }); }

    slide('s-call', 'Call for me, step by step', {
      notes: '<b>Use this if the live call fails.</b> <b>[click] Tell:</b> Maria taps Call for me and just says what she needs, in Russian. ' +
        '<b>[click] Check:</b> before anything happens, she sees exactly what the assistant will say in German, including "KI-Assistentin". Only her daughter\'s age, only the times she chose. She approves. <i>Wait about 11 s after this click, until all four callouts are shown and the consent box is ticked.</i> ' +
        '<b>[click] Call:</b> "Listen to the first sentence." Then be quiet. After the Saturday offer: "It said no. Maria did not approve Saturday." At the read-back: "This is why it repeats everything before it says yes." The call is 63 s; press Right to skip ahead.',
      init: function (S) {
        var chat = $('.chat', S.el);
        if (!bubbles.length) {
          D.intakeTimeline.forEach(function (e) {
            var b = el('div', 'bub ' + (e.speaker === 'parent' ? 'parent' : 'assistant'));
            b.innerHTML = '<div class="who">' + (e.speaker === 'parent' ? 'Maria' : 'Assistant') + '</div><div class="ru stream" lang="ru"></div><div class="en">' + esc(GLOSS[e.id] || '') + '</div>';
            chat.appendChild(b);
            var words = (e.words && e.words.length) ? e.words : propWords(e.ru || e.text, e.start, e.end);
            bubbles.push({ e: e, b: b, words: words, spans: makeWords($('.ru', b), words), en: $('.en', b) });
          });
        }
        if (!callBuilt) {
          callBuilt = true;
          var m = $('.moments', S.el);
          MOMENTS.forEach(function (t) { m.appendChild(el('div', 'moment', CHECK_LIGHT + '<span>' + esc(t) + '</span>')); });
        }
        stepper(S, 0);
        gsap.set($$('.h-slide', S.el), { opacity: 0 });
        gsap.set($('.stepper', S.el), { opacity: 0 });
        gsap.set($$('.view', S.el), { autoAlpha: 0, x: 0 });
        gsap.set($$('#v-intro .it, #v-intro .backup-note', S.el), { opacity: 0, y: 16 });
        bubbles.forEach(function (x) { gsap.set(x.b, { opacity: 0, y: 16 }); x.spans.forEach(function (s) { s._on = false; s.classList.remove('on'); }); x.en.classList.remove('on'); });
        gsap.set($('#v-intake .phone', S.el), { y: 0 });
        gsap.set($('#v-approve .inner', S.el), { y: 0 });
        gsap.set($('#v-approve .hlbox', S.el), { top: AP[0].top, height: AP[0].h, opacity: 0 });
        gsap.set($('#v-approve img.consent', S.el), { opacity: 0 });
        gsap.set($$('#v-approve .co', S.el), { opacity: 0, x: 24 });
        gsap.set($$('.moment', S.el), { opacity: 0, x: -20 });
        resetCall(S);
      },
      builds: [
        function (c) {
          var S = c.S, tl = c.tl(); titleIn(tl, S);
          tl.to($('.stepper', S.el), { opacity: 1, duration: 0.5 }, 0.1)
            .set($('#v-intro', S.el), { autoAlpha: 1 }, 0)
            .to($$('#v-intro .it', S.el), { opacity: 1, y: 0, stagger: 0.12 }, 0.2)
            .to($('#v-intro .backup-note', S.el), { opacity: 1, y: 0 }, 0.6);
        },
        function (c) {
          var S = c.S, tl = c.tl(); stepper(S, 1); showView(tl, S, 'v-intake');
          if (c.anim) {
            AU.play('intake_full', function (t) {
              bubbles.forEach(function (x) {
                if (t + 0.15 >= x.e.start && !x.shown) { x.shown = true; gsap.to(x.b, { opacity: 1, y: 0, duration: 0.4 }); }
                streamTo(x.spans, x.words, t);
                if (t >= x.e.end + 0.1) x.en.classList.add('on');
              });
            });
            c.onStop(function () { bubbles.forEach(function (x) { x.shown = false; }); });
          } else {
            bubbles.forEach(function (x) { gsap.set(x.b, { opacity: 1, y: 0 }); showAll(x.spans); x.en.classList.add('on'); });
          }
        },
        function (c) {
          var S = c.S, tl = c.tl(); stepper(S, 2); showView(tl, S, 'v-approve');
          var inner = $('#v-approve .inner', S.el), hl = $('#v-approve .hlbox', S.el), cos = $$('#v-approve .co', S.el);
          tl.to(hl, { opacity: 1, duration: 0.4 }, 0.9).to(cos[0], { opacity: 1, x: 0, duration: 0.5 }, 0.9);
          var at = 3.2;
          for (var i = 1; i < AP.length; i++) {
            tl.to(inner, { y: -AP[i].pan, duration: 1.0, ease: 'power2.inOut' }, at)
              .to(hl, { top: AP[i].top, height: AP[i].h, duration: 1.0, ease: 'power2.inOut' }, at)
              .to(cos[i], { opacity: 1, x: 0, duration: 0.5 }, at + 0.7);
            if (i === AP.length - 1) tl.to($('#v-approve img.consent', S.el), { opacity: 1, duration: 0.45, ease: 'power2.out' }, at + 1.5);
            at += 2.6;
          }
        },
        function (c) {
          var S = c.S, tl = c.tl(); stepper(S, 3); showView(tl, S, 'v-call');
          var mt = momentTimes(), moments = $$('.moment', S.el);
          if (c.anim) {
            var shownM = [false, false, false];
            setLive(S, true);
            AU.play('call_full', function (t) {
              renderCall(S, t);
              for (var i = 0; i < 3; i++) if (!shownM[i] && t >= mt[i]) { shownM[i] = true; gsap.to(moments[i], { opacity: 1, x: 0, duration: 0.5, ease: 'back.out(1.6)' }); }
            }, function () { setLive(S, false); });
          } else {
            var last = callLines.length ? callLines[callLines.length - 1].end : 63;
            renderCall(S, 1e6); setLive(S, false, last);
            gsap.set(moments, { opacity: 1, x: 0 });
          }
        }
      ]
    });

    var shownIdx = -1, curSpans = null;
    function resetCall(S) {
      shownIdx = -1; curSpans = null;
      $$('.transcript .tl-who, .transcript .de, .transcript .ruline', S.el).forEach(function (e) { e.innerHTML = ''; });
      $('.callcard .timer', S.el).textContent = '00:00';
      setLive(S, true);
      $$('.spk', S.el).forEach(function (s) { s.classList.remove('on'); });
    }
    function setLive(S, live, endT) {
      var dot = $('.live-dot', S.el), word = $('.live-word', S.el), st = $('.state-text', S.el);
      dot.style.display = live ? '' : 'none'; dot.classList.toggle('pulse', !!live);
      word.style.display = live ? '' : 'none';
      st.textContent = live ? 'German call' : 'Call ended';
      st.className = 'state-text ' + (live ? 'muted' : 'ended-word');
      if (!live) { $$('.spk', S.el).forEach(function (s) { s.classList.remove('on'); }); if (endT != null) $('.callcard .timer', S.el).textContent = mmss(endT); }
    }
    function fillLine(box, line, stream) {
      var who = $('.tl-who', box), de = $('.de', box), ru = $('.ruline', box);
      who.textContent = spkName(line.speaker); who.className = 'tl-who' + (line.speaker === 'assistant' ? ' a' : '');
      if (!stream) { de.textContent = line.de; ru.textContent = line.ru; return null; }
      var dw = (line.words && line.words.length) ? line.words : propWords(line.de, line.start, line.end);
      var rw = propWords(line.ru, line.start + 0.2, line.end + 0.4);
      return { dw: dw, rw: rw, ds: makeWords(de, dw), rs: makeWords(ru, rw) };
    }
    function renderCall(S, t) {
      if (!callLines.length) return;
      var idx = -1;
      for (var i = 0; i < callLines.length; i++) if (t + 0.05 >= callLines[i].start) idx = i;
      if (t < 1e5) $('.callcard .timer', S.el).textContent = mmss(t);
      if (idx !== shownIdx) {
        shownIdx = idx;
        var prevBox = $('.transcript .prev', S.el), curBox = $('.transcript .cur', S.el);
        if (idx > 0) { fillLine(prevBox, callLines[idx - 1], false); gsap.fromTo(prevBox, { opacity: 0.2, y: 30 }, { opacity: 1, y: 0, duration: 0.45 }); }
        else $$('.tl-who, .de, .ruline', prevBox).forEach(function (e) { e.textContent = ''; });
        if (idx >= 0) {
          curSpans = fillLine(curBox, callLines[idx], true);
          if (t < 1e5) gsap.fromTo(curBox, { y: 24, opacity: 0.4 }, { y: 0, opacity: 1, duration: 0.4 });
        }
      }
      if (curSpans) { streamTo(curSpans.ds, curSpans.dw, t); streamTo(curSpans.rs, curSpans.rw, t); }
      var sp = null;
      for (var j = 0; j < callLines.length; j++) if (t >= callLines[j].start - 0.05 && t <= callLines[j].end + 0.1) sp = callLines[j].speaker;
      $('#spk-a', S.el).classList.toggle('on', sp === 'assistant');
      $('#spk-r', S.el).classList.toggle('on', !!sp && sp !== 'assistant');
    }
  })();

  // 7 · Result -------------------------------------------------------------
  (function () {
    var spans = null, words = null;
    slide('s-result', 'The answer, in her language', {
      notes: '<b>Say:</b> The answer comes back in her language. <b>[click]</b> (Russian read-back plays.) <b>[click]</b> And the course page now shows "checked by phone", so the next parent sees fresh information. Add to calendar is one tap. <b>[click]</b> No audio was stored, only text. ' +
        '<i>Note: the real end-to-end test call on 26 Sep (RUN-026) booked Thursday 14:00; this card shows the story data (16:30).</i>',
      init: function (S) {
        if (!spans) { words = clipWords('result_ru'); spans = makeWords($('.result .say', S.el), words); }
        spans.forEach(function (s) { s._on = false; s.classList.remove('on'); });
        gsap.set($$('.h-slide', S.el), { opacity: 0 });
        gsap.set($('.result', S.el), { opacity: 0, y: 30 });
        gsap.set($$('.result .en, .result .bring, .result .actions', S.el), { opacity: 0, y: 12 });
        gsap.set($('.result .tick', S.el), { drawSVG: '0%' });
        gsap.set($('.checked', S.el), { opacity: 0 });
        gsap.set($('.checked .badge img', S.el), { clipPath: 'inset(0% 100% 0% 0%)' });
        gsap.set($('.checked rect.draw', S.el), { drawSVG: '0%' });
        gsap.set($$('.checked .why, .checked .gl', S.el), { opacity: 0 });
        gsap.set($('.noaudio', S.el), { opacity: 0, y: 20 });
        gsap.set($('.recap', S.el), { opacity: 0 });
      },
      builds: [
        function (c) {
          var tl = c.tl(); titleIn(tl, c.S);
          tl.to($('.result', c.S.el), { opacity: 1, y: 0, duration: 0.7 }, 0.1)
            .to($('.result .tick', c.S.el), { drawSVG: '100%', duration: 0.6, ease: 'power2.out' }, 0.6)
            .to($('.recap', c.S.el), { opacity: 1 }, 0.8);
        },
        function (c) {
          var S = c.S, tl = c.tl();
          tl.to($('.result .bring', S.el), { opacity: 1, y: 0 }, 0);
          var en = $('.result .en', S.el);
          if (c.anim) AU.play('result_ru', function (t) { streamTo(spans, words, t); }, function () { gsap.to(en, { opacity: 1, y: 0, duration: 0.5 }); });
          else { showAll(spans); gsap.set(en, { opacity: 1, y: 0 }); }
        },
        function (c) {
          var S = c.S, tl = c.tl();
          tl.to($('.checked', S.el), { opacity: 1, duration: 0.3 })
            .to($('.checked .badge img', S.el), { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.8, ease: 'power2.inOut' }, 0.1)
            .to($('.checked rect.draw', S.el), { drawSVG: '100%', duration: 1.0, ease: 'power2.inOut' }, 0.3)
            .to($('.checked .gl', S.el), { opacity: 1 }, 0.8)
            .to($('.checked .why', S.el), { opacity: 1 }, 1.0)
            .to($('.result .actions', S.el), { opacity: 1, y: 0 }, 0.5)
            .fromTo($('.result .btn.cal', S.el), { scale: 1 }, { scale: 1.05, duration: 0.25, yoyo: true, repeat: 1, ease: 'power1.inOut' }, 1.0);
        },
        function (c) {
          var tl = c.tl(); tl.to($('.noaudio', c.S.el), { opacity: 1, y: 0, duration: 0.7 });
        }
      ]
    });
  })();

  // 8 · Architecture ---------------------------------------------------------
  (function () {
    var A = D.arch;
    var CAP = {
      app: 'Maria asks in her language in the Ankommen app.',
      requests: 'Her approved request is saved in Supabase, in the EU.',
      brief: 'n8n and Claude write the German call brief, in about 10 seconds.',
      'relay-call': 'Our voice relay starts the call.',
      agent: 'The Deepgram voice agent speaks German. Claude does the thinking.',
      receptionist: 'The course answers. Today this is a browser role-play.',
      store: 'Every line is saved as text. No audio.',
      result: 'n8n translates each line and writes the result in her language.',
      'app-end': 'Maria sees the answer in Russian, live, through Supabase Realtime.'
    };
    var path = (A && A.main_path) || ['app', 'requests', 'brief', 'relay-call', 'agent', 'receptionist', 'store', 'result', 'app'];
    var F = A ? 1680 / A.width : 1, H = A ? A.height * F : 716;
    var NODES = {}; if (A) A.nodes.forEach(function (n) { NODES[n.id] = n; });
    var built = false;
    function box(id) { var n = NODES[id]; if (!n) return null; var p = 9; return { x: n.x * F - p, y: n.y * F - p, w: n.w * F + 2 * p, h: n.h * F + 2 * p }; }
    // camera: zoom the diagram toward the active node so its label is readable from the back (scale ZOOM, clamped to the frame)
    var ZOOM = 1.5;
    var CAM_WITH = { agent: 'claude' }; // the agent step also names Claude: keep that node in view
    function camera(b, id) {
      if (!b) return { scale: 1, x: 0, y: 0 };
      var cx = b.x + b.w / 2, cy = b.y + b.h / 2, o = CAM_WITH[id] && box(CAM_WITH[id]);
      if (o) { cx = (cx + o.x + o.w / 2) / 2; cy = (cy + o.y + o.h / 2) / 2; }
      return { scale: ZOOM, x: clamp(840 - ZOOM * cx, 1680 * (1 - ZOOM), 0), y: clamp(H / 2 - ZOOM * cy, H * (1 - ZOOM), 0) };
    }
    slide('s-arch', 'How it works', {
      notes: '<b>Say:</b> How it works, in nine steps. (Click through; one sentence each.) The app is Lovable with Supabase in Frankfurt. n8n and Claude write the German brief. Our voice relay runs the Deepgram voice agent, which says in the first sentence that it is an AI. Every line is stored as text, never audio. n8n translates and writes the answer back, and the app shows it live.',
      init: function (S) {
        var svg = $('svg.ov', S.el), caps = $('.caps', S.el);
        if (!built) {
          built = true;
          svg.setAttribute('width', 1680); svg.setAttribute('height', Math.round(H)); svg.setAttribute('viewBox', '0 0 1680 ' + Math.round(H));
          var ns = 'http://www.w3.org/2000/svg', visited = '';
          path.forEach(function (id, i) {
            var b = box(id); if (!b) return;
            visited += '<rect class="vis" data-i="' + i + '" x="' + b.x + '" y="' + b.y + '" width="' + b.w + '" height="' + b.h + '" rx="12" fill="' + PINE + '" fill-opacity="0.10" stroke="none"/>';
          });
          var b0 = box(path[0]) || { x: 0, y: 0, w: 100, h: 60 };
          svg.innerHTML = visited + '<rect class="mover" x="' + b0.x + '" y="' + b0.y + '" width="' + b0.w + '" height="' + b0.h + '" rx="12" fill="none" stroke="' + PINE + '" stroke-width="5"/>';
          path.forEach(function (id, i) {
            var key = (i === path.length - 1 && id === path[0]) ? 'app-end' : id;
            var d = el('div', 'caption', '<b>' + (i + 1) + ' / ' + path.length + '</b>' + esc(CAP[key] || (NODES[id] && NODES[id].label) || id));
            caps.appendChild(d);
          });
          caps.appendChild(el('div', 'caption intro', 'Nine steps, one call. Main path in green.'));
          void ns;
        }
        gsap.set($$('.h-slide, .sub, .ilink', S.el), { opacity: 0 });
        gsap.set($('.arch', S.el), { opacity: 0, y: 30, height: Math.round(H) + 2 });
        gsap.set($('.arch-in', S.el), { scale: 1, x: 0, y: 0, transformOrigin: '0 0' });
        gsap.set($$('rect.vis', svg), { opacity: 0 });
        var b0 = box(path[0]);
        if (b0) gsap.set($('rect.mover', svg), { attr: { x: b0.x, y: b0.y, width: b0.w, height: b0.h }, opacity: 0, drawSVG: '0%' });
        gsap.set($$('.caption', caps), { opacity: 0, y: 10 });
      },
      builds: [
        function (c) {
          var S = c.S, tl = c.tl(); titleIn(tl, S);
          tl.to($('.ilink', S.el), { opacity: 1 }, 0.3)
            .to($('.arch', S.el), { opacity: 1, y: 0, duration: 0.9, ease: 'expo.out' }, 0.15)
            .to($('.caption.intro', S.el), { opacity: 1, y: 0 }, 0.6);
        }
      ].concat(path.map(function (id, i) {
        return function (c) {
          var S = c.S, tl = c.tl(), svg = $('svg.ov', S.el), mover = $('rect.mover', svg), b = box(id);
          var caps = $$('.caption', S.el);
          tl.to(caps, { opacity: 0, duration: 0.2 }, 0).fromTo(caps[i], { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.45 }, 0.2);
          // last step (back in the app) zooms out again to show the whole loop
          tl.to($('.arch-in', S.el), Object.assign(camera(i === path.length - 1 ? null : b, id), { duration: 0.8, ease: 'power3.inOut' }), 0);
          if (!b) return;
          if (i === 0) tl.set(mover, { opacity: 1 }, 0).to(mover, { drawSVG: '100%', duration: 0.7, ease: 'power2.inOut' }, 0);
          else tl.set(mover, { opacity: 1, drawSVG: '100%' }, 0).to(mover, { attr: { x: b.x, y: b.y, width: b.w, height: b.h }, duration: 0.7, ease: 'power3.inOut' }, 0);
          tl.to($$('rect.vis[data-i="' + i + '"]', svg), { opacity: 1, duration: 0.4 }, 0.4);
        };
      }))
    });
  })();

  // 9 · n8n --------------------------------------------------------------------
  (function () {
    var ORDER = ['04', '01', '05', '06'];
    var wfs = ORDER.map(function (p) { return D.n8n.filter(function (w) { return (w.file || '').indexOf(p) === 0; })[0]; }).filter(Boolean);
    var cards = [], built = false, n = 0;
    function depthVars(d) { return { y: 40 - d * 22, scale: 1 - d * 0.03, zIndex: 10 - d, opacity: d > 3 ? 0 : 1 }; }
    function buildCard(w) {
      var card = el('div', 'card wf');
      var mp = (w.main_path || []).map(function (nm, i) { return '<li><i>' + (i + 1) + '</i>' + esc(nm) + '</li>'; }).join('');
      card.innerHTML = '<h3>' + esc(w.title || w.n8n_name || '') + '</h3>' +
        '<div class="what">' + esc(w.what_it_does || '') + '</div><div class="trig">Starts when: ' + esc((w.trigger || '').replace(/^A /, 'a ')) + (w.node_count ? ' · ' + w.node_count + ' nodes' : '') + '</div>' +
        '<div class="svgbox"></div><ol class="mp">' + mp + '</ol><div class="real"><img alt="The real n8n canvas" src="assets/n8n/' + esc(w.file) + '"><div class="cap">The real n8n canvas</div></div>';
      var sb = $('.svgbox', card);
      if (w.svg) {
        sb.innerHTML = w.svg;
        var svg = $('svg', sb);
        var vb = (svg.getAttribute('viewBox') || '0 0 1000 400').split(/\s+/).map(Number);
        var s = Math.min(1000 / vb[2], 440 / vb[3]);
        svg.setAttribute('width', Math.round(vb[2] * s)); svg.setAttribute('height', Math.round(vb[3] * s));
        var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('r', 11); dot.setAttribute('fill', PINE); dot.setAttribute('stroke', '#FFFDF8'); dot.setAttribute('stroke-width', 4); dot.setAttribute('class', 'dot');
        svg.appendChild(dot);
      } else {
        sb.innerHTML = '<img alt="" style="max-width:1000px;max-height:440px" src="assets/n8n/' + esc(w.file) + '">';
      }
      return card;
    }
    function mainPaths(card) {
      return $$('path[data-main="1"]', card).sort(function (a, b) { return (+a.getAttribute('data-order')) - (+b.getAttribute('data-order')); });
    }
    function nodeShape(card, name) {
      var g = $$('g[data-node]', card).filter(function (x) { return x.getAttribute('data-node') === name; })[0];
      return g ? $('[data-shape]', g) : null;
    }
    function travel(tl, card, at) {
      var paths = mainPaths(card), dot = $('circle.dot', card);
      if (!paths.length || !dot) return;
      tl.set(paths, { drawSVG: '0%' }, at).set(dot, { opacity: 1 }, at);
      var lis = $$('.mp li', card);
      var mark = function (i, when) { var li = lis[i]; if (!li) return; tl.to(li, { color: '#1C2420', duration: 0.2 }, when).to($('i', li), { backgroundColor: PINE, borderColor: PINE, color: '#FFFDF8', duration: 0.2 }, when); };
      var first = nodeShape(card, paths[0].getAttribute('data-from'));
      if (first) tl.to(first, { attr: { stroke: PINE, 'stroke-width': 2.5 }, duration: 0.3 }, at);
      mark(0, at);
      var t = at + 0.2;
      paths.forEach(function (p, i) {
        tl.to(p, { drawSVG: '100%', duration: 0.5, ease: 'none' }, t)
          .to(dot, { motionPath: { path: p, align: p, alignOrigin: [0.5, 0.5] }, duration: 0.5, ease: 'none' }, t);
        var tgt = nodeShape(card, p.getAttribute('data-to'));
        if (tgt) tl.to(tgt, { attr: { stroke: PINE, 'stroke-width': 2.5 }, duration: 0.25 }, t + 0.45);
        mark(i + 1, t + 0.45);
        t += 0.55;
      });
      tl.to(dot, { opacity: 0, duration: 0.4 }, t + 0.3);
    }
    function resetCard(card) {
      mainPaths(card).forEach(function (p) { gsap.set(p, { drawSVG: '100%' }); });
      $$('[data-shape]', card).forEach(function (s) { s.setAttribute('stroke', BORDER); s.setAttribute('stroke-width', 1); });
      var dot = $('circle.dot', card); if (dot) gsap.set(dot, { opacity: 0, x: 0, y: 0 });
      $$('.mp li', card).forEach(function (li) { gsap.set(li, { clearProps: 'color' }); gsap.set($('i', li), { clearProps: 'backgroundColor,borderColor,color' }); });
    }
    slide('s-n8n', 'n8n moves the work', {
      notes: '<b>Say:</b> n8n moves the work. Four workflows are in the loop. <b>04</b> turns the parent\'s words into a call task. <b>01</b> writes the German call brief with Claude. <b>05</b> translates every line during the call. <b>06</b> brings the answer back in the parent\'s language and marks the request as booked.',
      init: function (S) {
        var stack = $('.stack', S.el);
        if (!built) { built = true; wfs.forEach(function (w) { var cd = buildCard(w); stack.appendChild(cd); cards.push(cd); }); n = cards.length; }
        gsap.set($$('.h-slide, .sub', S.el), { opacity: 0 });
        cards.forEach(function (cd, i) { resetCard(cd); gsap.set(cd, Object.assign(depthVars(i), { opacity: 0 })); });
      },
      builds: [
        function (c) {
          var S = c.S, tl = c.tl(); titleIn(tl, S);
          cards.forEach(function (cd, i) { tl.to(cd, Object.assign(depthVars(i), { duration: 0.7, ease: 'expo.out' }), 0.15 + (n - 1 - i) * 0.08); });
          if (cards[0]) travel(tl, cards[0], 0.9);
        }
      ].concat(wfs.slice(1).map(function (w, k) {
        var front = k + 1;
        return function (c) {
          var tl = c.tl(), old = cards[front - 1];
          tl.to(old, { y: 160, scale: 0.94, opacity: 0, duration: 0.4, ease: 'power2.in' }, 0);
          cards.forEach(function (cd, i) {
            if (cd === old) return;
            var d = (i - front + n) % n;
            var v = depthVars(d);
            if (d === 0) tl.to(cd, Object.assign(v, { duration: 0.75, ease: 'expo.out' }), 0.25);
            else tl.to(cd, Object.assign(v, { duration: 0.6 }), 0.2);
          });
          tl.set(old, depthVars(n - 1), 0.45).set(old, { opacity: 0 }, 0.45).to(old, { opacity: 1, duration: 0.4 }, 0.6);
          travel(tl, cards[front], 0.9);
        };
      }))
    });
  })();

  // 10 · Lovable ---------------------------------------------------------------
  (function () {
    var STOPS = [
      ['P1b', 'Shell, 6 languages, RTL'], ['P2', 'Courses directory'], ['P3', 'Course page, button'], ['P4', 'Events'],
      ['P5', 'Communities, services'], ['P6', 'Library + guides'], ['P7', 'Tell us what you need'], ['P8', 'Approval card'],
      ['P9', 'Live call'], ['P10', 'Result + calendar'], ['P11', 'Home page'],
      ['P14', 'Legal pages, SEO'], ['P15', 'Dictation button'], ['P16', 'Language switch']
    ];
    var THUMBS = [
      ['P2', 'Courses', 'desktop-courses-ru.png'], ['P3', 'Course page', 'desktop-provider-ru.png'],
      ['P8', 'Approval card', 'desktop-ask-approval-ru.png'], ['P10', 'Result', 'desktop-result-ru.png'], ['P11', 'Home', 'desktop-home-ru.png']
    ];
    var built = false;
    slide('s-lovable', 'Built with Lovable', {
      notes: '<b>Say:</b> We built the app in Lovable, prompt by prompt, from a written plan. <b>[click]</b> These are real screens from those prompts. <b>[click]</b> How we worked: our design rules live in Lovable Knowledge; the code syncs both ways with GitHub; all UI text in six languages comes from our repo; Claude Code, n8n and Supabase do the backend. <b>[click]</b> And it started as two ideas: Abdul\'s HalloTermin, calls in German, and Anastasia\'s family guide. Together: Ankommen. Find it. We call for you.',
      init: function (S) {
        var rail = $('.rail', S.el), th = $('.thumbs', S.el);
        if (!built) {
          built = true;
          var x0 = 40, x1 = 1640;
          STOPS.forEach(function (s, i) {
            var x = x0 + (x1 - x0) * i / (STOPS.length - 1);
            var dot = el('div', 'stop'); dot.style.left = x + 'px'; dot.setAttribute('data-p', s[0]); rail.appendChild(dot);
            var lab = el('div', 'stop-lab ' + (i % 2 ? 'dn' : 'up'), '<b>' + s[0] + '</b>' + esc(s[1])); lab.style.left = x + 'px'; rail.appendChild(lab);
          });
          THUMBS.forEach(function (t) {
            var d = el('div', 'thumb');
            d.innerHTML = '<div class="img"><img alt="" src="assets/screens/' + t[2] + '"></div><div class="cap"><b>' + t[0] + '</b>' + esc(t[1]) + '</div>';
            d.setAttribute('data-p', t[0]); th.appendChild(d);
          });
        }
        gsap.set($$('.h-slide, .sub', S.el), { opacity: 0 });
        gsap.set($('.rail .line', S.el), { scaleX: 0 });
        gsap.set($$('.stop', S.el), { scale: 0 });
        $$('.stop', S.el).forEach(function (s) { s.classList.remove('hit'); });
        gsap.set($$('.stop-lab', S.el), { opacity: 0, y: 8 });
        gsap.set($$('.thumb', S.el), { opacity: 0, y: 24 });
        gsap.set($$('.howwe .note-tag', S.el), { opacity: 0, y: 12 });
        gsap.set($$('.ideas > *', S.el), { opacity: 0, x: -16 });
      },
      builds: [
        function (c) {
          var S = c.S, tl = c.tl(); titleIn(tl, S);
          tl.to($('.rail .line', S.el), { scaleX: 1, duration: 1.3, ease: 'power2.inOut' }, 0.2)
            .to($$('.stop', S.el), { scale: 1, duration: 0.35, stagger: 1.1 / STOPS.length, ease: 'back.out(2)' }, 0.25)
            .to($$('.stop-lab', S.el), { opacity: 1, y: 0, duration: 0.35, stagger: 1.1 / STOPS.length }, 0.35);
        },
        function (c) {
          var S = c.S, tl = c.tl();
          THUMBS.forEach(function (t) { var s = $('.stop[data-p="' + t[0] + '"]', S.el); if (s) s.classList.add('hit'); });
          tl.to($$('.thumb', S.el), { opacity: 1, y: 0, stagger: 0.1, duration: 0.6 }, 0);
        },
        function (c) { var tl = c.tl(); tl.to($$('.howwe .note-tag', c.S.el), { opacity: 1, y: 0, stagger: 0.1, duration: 0.5 }); },
        function (c) {
          var tl = c.tl(), it = $$('.ideas > *', c.S.el);
          tl.to(it.slice(0, 3), { opacity: 1, x: 0, stagger: 0.15, duration: 0.5 })
            .to(it.slice(3), { opacity: 1, x: 0, stagger: 0.2, duration: 0.6 }, '+=0.2');
        }
      ]
    });
  })();

  // 11 · Numbers ----------------------------------------------------------------
  (function () {
    var N = [
      { v: 162, l: 'places', s: 'in the directory' },
      { v: 92, l: 'family providers', s: 'courses, Kitas, schools, family places' },
      { v: 44, l: 'events', s: 'upcoming, for families' },
      { v: 8, suf: ' × 6', l: 'guides', s: 'each in 6 languages' },
      { v: 6, l: 'interface languages', s: 'EN · DE · RU · UK · AR · TR' },
      { v: 10, l: 'call types', s: 'tasks the assistant can call for' },
      { v: 4, l: 'n8n workflows', s: 'in the call loop' },
      { v: 70, v2: 95, suf: ' s', l: 'to a booking', s: 'role-play calls, start to booked' }
    ];
    var built = false;
    function fmt(d, a, b) { return d.v2 ? Math.round(a) + '–' + Math.round(b) + '<small>' + d.suf + '</small>' : Math.round(a) + (d.suf ? '<small>' + d.suf + '</small>' : ''); }
    function row(c, from) {
      var tl = c.tl(), items = $$('.num', c.S.el).slice(from, from + 4);
      tl.to(items, { opacity: 1, y: 0, stagger: 0.1, duration: 0.6 });
      items.forEach(function (it, i) {
        var d = N[from + i], v = $('.v', it);
        if (!c.anim) { v.innerHTML = fmt(d, d.v, d.v2 || 0); return; }
        var o = { a: 0, b: 0 };
        tl.to(o, { a: d.v, b: d.v2 || 0, duration: 1.3, ease: 'power2.out', onUpdate: function () { v.innerHTML = fmt(d, o.a, o.b); } }, 0.1 + i * 0.1);
      });
    }
    slide('s-numbers', 'In numbers', {
      notes: '<b>Say only these numbers.</b> 162 places, 92 family providers, 44 upcoming events, 8 guides in 6 languages, 6 interface languages, 10 call types, 4 n8n workflows. Role-play calls booked in 70 to 95 seconds. All calls this weekend are browser role-plays.',
      init: function (S) {
        var box = $('.nums', S.el);
        if (!built) { built = true; N.forEach(function (d) { box.appendChild(el('div', 'num', '<div class="v tnum"></div><div class="l">' + esc(d.l) + '<span>' + esc(d.s) + '</span></div>')); }); }
        $$('.num .v', S.el).forEach(function (v, i) { v.innerHTML = fmt(N[i], 0, 0); });
        gsap.set($$('.h-slide', S.el), { opacity: 0 });
        gsap.set($$('.num', S.el), { opacity: 0, y: 20 });
        gsap.set($('.src-line', S.el), { opacity: 0 });
      },
      builds: [
        function (c) { var tl = c.tl(); titleIn(tl, c.S); tl.to($('.src-line', c.S.el), { opacity: 1 }, 0.3); },
        function (c) { row(c, 0); },
        function (c) { row(c, 4); }
      ]
    });
  })();

  // 12 · Trust ----------------------------------------------------------------
  (function () {
    var T = [
      ['The AI says it is an AI, in its first sentence.', 'EU AI Act, Article 50'],
      ['The parent sees and approves the German opening line.', 'Nothing happens before she ticks consent.'],
      ['It only agrees to times the parent approved.', 'It reads the answer back before it books.'],
      ['No audio is stored.', 'Only the text transcript and the result.'],
      ['No child names. No health data.', 'Only facts the parent ticked, like the child\'s age.'],
      ['Honest status: all calls this weekend are browser role-plays.', 'No phone line yet.']
    ];
    var built = false;
    slide('s-trust', 'Trust by design', {
      notes: '<b>Say:</b> Trust is built in. <b>[click x6]</b> The assistant says it is an AI in its first sentence; this is what the EU AI Act, Article 50 asks for. The parent sees and approves the German opening line. It only agrees to times she approved. No audio is stored. No child names or health data. And to be honest: all calls this weekend are browser role-plays. We have no phone line yet. <i>Say "we built it for these rules", never "fully compliant".</i>',
      init: function (S) {
        var box = $('.trust', S.el);
        if (!built) {
          built = true;
          T.forEach(function (t, i) {
            var last = i === T.length - 1;
            box.appendChild(el('div', 'tr' + (last ? ' honest' : ''), (last ? '' : CHECK_SVG) + '<div>' + esc(t[0]) + '<small>' + esc(t[1]) + '</small></div>'));
          });
        }
        gsap.set($$('.h-slide', S.el), { opacity: 0 });
        gsap.set($$('.tr', S.el), { opacity: 0, x: -24 });
        gsap.set($('.trust-img', S.el), { opacity: 0, y: 30 });
      },
      builds: [
        function (c) { var tl = c.tl(); titleIn(tl, c.S); tl.to($('.trust-img', c.S.el), { opacity: 1, y: 0, duration: 0.8, ease: 'expo.out' }, 0.2); }
      ].concat(T.map(function (_, i) {
        return function (c) { var tl = c.tl(); tl.to($$('.tr', c.S.el)[i], { opacity: 1, x: 0, duration: 0.55 }); };
      }))
    });
  })();

  // 13 · Monday ----------------------------------------------------------------
  slide('s-monday', 'Monday-Morning Plan', {
    notes: '<b>Say:</b> What happens on Monday. <b>This week:</b> user accounts and owner-only data access instead of demo mode, rate limits, data processing agreements and EU endpoints. <b>Next:</b> a German +49 number, a public relay with signed per-call tokens, a legal check of live transcription under §201 StGB, and native speakers review Russian, Ukrainian and Arabic. <b>Friday goal:</b> one real call, with consent, to a friendly provider. <b>[click]</b> We are looking for pilot partners: TU Dresden International Office, the Welcome Center Dresden, and employers who hire skilled workers.',
    init: function (S) {
      gsap.set($$('.h-slide', S.el), { opacity: 0 });
      gsap.set($$('.col', S.el), { opacity: 0, y: 30 });
      gsap.set($$('.col li, .col .big, .col p', S.el), { opacity: 0, y: 10 });
      gsap.set($('.pilot', S.el), { opacity: 0, y: 16 });
    },
    builds: [
      function (c) { var tl = c.tl(); titleIn(tl, c.S); }
    ].concat([0, 1, 2].map(function (i) {
      return function (c) {
        var col = $$('.col', c.S.el)[i], tl = c.tl();
        tl.to(col, { opacity: 1, y: 0, duration: 0.6 }).to($$('li, .big, p', col), { opacity: 1, y: 0, stagger: 0.1, duration: 0.45 }, 0.25);
      };
    })).concat([
      function (c) { var tl = c.tl(); tl.to($('.pilot', c.S.el), { opacity: 1, y: 0, duration: 0.6 }); }
    ])
  });

  // 14 · Thanks -----------------------------------------------------------------
  slide('s-thanks', 'Thank you', {
    notes: '<b>Say:</b> Thank you. Try Call for me: the link and the QR code open the live app. We are happy to take questions. <i>Jury answers: Pitch Kit v2 section 4.</i>',
    init: function (S) {
      var q = $('.qrsvg', S.el);
      if (!q.firstChild) q.innerHTML = (D.qr && D.qr.svg) || '<div class="cap">QR code missing: run build_data.py</div>';
      var ch = splitChars($('.wordmark', S.el));
      gsap.set(ch, { yPercent: 70, opacity: 0, rotation: 6, transformOrigin: '50% 100%' });
      gsap.set($$('.ty, .site, .try, .team', S.el), { opacity: 0, y: 14 });
      gsap.set($('.qr', S.el), { opacity: 0, scale: 0.96 });
    },
    builds: [
      function (c) {
        var tl = c.tl();
        tl.to($$('.ch', c.S.el), { yPercent: 0, opacity: 1, rotation: 0, duration: 0.9, stagger: 0.05, ease: 'expo.out' })
          .to($$('.ty, .site, .try, .team', c.S.el), { opacity: 1, y: 0, stagger: 0.1 }, 0.5)
          .to($('.qr', c.S.el), { opacity: 1, scale: 1, duration: 0.7, ease: 'expo.out' }, 0.7);
      }
    ]
  });
  MAIN_COUNT = SL.length;

  // Appendix -----------------------------------------------------------------------
  slide('s-divider', 'Appendix', {
    appendix: '·',
    notes: 'Appendix: only if someone asks. A1 interactive architecture, A2 the four n8n workflows (real canvas), A3 the app on a phone.',
    init: function (S) { gsap.set($$('.big, .list', S.el), { opacity: 0, y: 14 }); },
    builds: [function (c) { var tl = c.tl(); tl.to($$('.big, .list', c.S.el), { opacity: 1, y: 0, stagger: 0.12 }); }]
  });
  slide('s-a1', 'A1 · Interactive architecture', {
    appendix: 'A1',
    notes: 'Live, interactive archify diagram in the paper colours. Hover and click inside it; the click does not advance the slide. After a click inside, the deck takes the keyboard back, so the clicker keeps working. If it ever does not, click outside the diagram once.',
    init: function (S) { var f = $('iframe', S.el); if (!f.getAttribute('src')) f.setAttribute('src', 'assets/deck/architecture-paper.html?theme=light&embed=1'); gsap.set(f, { opacity: 0 }); },
    builds: [function (c) { var tl = c.tl(); titleIn(tl, c.S); tl.to($('iframe', c.S.el), { opacity: 1, duration: 0.5 }, 0.1); }]
  });
  (function () {
    var built = false, wfs = D.n8n.slice();
    slide('s-a2', 'A2 · n8n workflows', {
      appendix: 'A2',
      notes: 'The four workflows as they look in n8n (credentials, URLs and code removed before rendering). One per click.',
      init: function (S) {
        var box = $('.full', S.el);
        if (!built) { built = true; wfs.forEach(function (w) { box.appendChild(el('img', '', null)).setAttribute('src', 'assets/n8n/' + w.file); }); $$('img', box).forEach(function (im, i) { im.alt = wfs[i].title || ''; }); }
        gsap.set($$('img', box), { opacity: 0 }); $('.full-cap', S.el).textContent = '';
      },
      builds: (wfs.length ? wfs : [null]).map(function (w, i) {
        return function (c) {
          var S = c.S, tl = c.tl(), imgs = $$('.full img', S.el);
          if (i === 0) titleIn(tl, S);
          if (!w) { $('.full-cap', S.el).textContent = 'n8n images missing'; return; }
          tl.to(imgs, { opacity: 0, duration: 0.25 }, 0).fromTo(imgs[i], { opacity: 0, scale: 1.02 }, { opacity: 1, scale: 1, duration: 0.6 }, 0.15);
          $('.full-cap', S.el).textContent = (w.title || '') + ' · ' + (w.node_count || '?') + ' nodes · real n8n canvas';
        };
      })
    });
  })();
  (function () {
    var G = [
      ['mobile-home-ru.png', 'Home, Russian'], ['mobile-home-ar.png', 'Home, Arabic, right to left'], ['mobile-provider-ru.png', 'Course page'],
      ['mobile-ask-ru.png', 'Call for me: speak'], ['mobile-result-card-ru.png', 'Result of the real test call (RUN-026)']
    ];
    var built = false;
    slide('s-a3', 'A3 · The app on a phone', {
      appendix: 'A3',
      notes: 'Mobile screenshots of the live app at 390 px width. The last one is the real end-to-end test call from 26 Sep (booked 14:00).',
      init: function (S) {
        var g = $('.gallery', S.el);
        if (!built) {
          built = true;
          G.filter(function (x) { return hasShot(x[0]); }).forEach(function (x) {
            g.appendChild(el('figure', '', '<div class="phone"><img alt="' + esc(x[1]) + '" src="assets/screens/' + x[0] + '"></div><figcaption class="cap">' + esc(x[1]) + '</figcaption>'));
          });
        }
        gsap.set($$('.h-slide', S.el), { opacity: 0 });
        gsap.set($$('figure', g), { opacity: 0, y: 30 });
      },
      builds: [function (c) { var tl = c.tl(); titleIn(tl, c.S); tl.to($$('figure', c.S.el), { opacity: 1, y: 0, stagger: 0.1, duration: 0.7 }, 0.1); }]
    });
  })();

  // =================================================================== boot
  function fit() {
    var w = window.innerWidth, h = window.innerHeight, s = Math.min(w / 1920, h / 1080);
    stage.style.transform = 'translate(' + ((w - 1920 * s) / 2) + 'px,' + ((h - 1080 * s) / 2) + 'px) scale(' + s + ')';
  }
  window.addEventListener('resize', fit); fit();

  function buildOverview() {
    var g = $('#overview .grid');
    SL.forEach(function (S, i) {
      var b = el('button', '', '<b>' + (i + 1) + (S.appendix && S.appendix !== '·' ? ' · ' + S.appendix : '') + '</b>' + esc(S.title));
      b.addEventListener('click', function (e) { e.stopPropagation(); toggle('#overview', false); go(i, 0, 'next'); });
      g.appendChild(b);
    });
  }

  var jumpBuf = '', jumpT = 0;
  function showJump() { $('#jump').textContent = jumpBuf ? 'Go to ' + jumpBuf : ''; }
  document.addEventListener('keydown', function (e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var k = e.key;
    if (/^[0-9]$/.test(k)) { jumpBuf += k; showJump(); clearTimeout(jumpT); jumpT = setTimeout(function () { jumpBuf = ''; showJump(); }, 3000); e.preventDefault(); return; }
    if (k === 'Enter') { if (jumpBuf) { var n = parseInt(jumpBuf, 10); jumpBuf = ''; showJump(); toggle('#overview', false); go(n - 1, 0, 'next'); } e.preventDefault(); return; }
    if ($('#black').classList.contains('on') && k !== 'b' && k !== 'B' && k !== '.') { toggle('#black', false); }
    switch (k) {
      case 'ArrowRight': case 'ArrowDown': case ' ': case 'PageDown': next(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': prev(); break;
      case 'Home': go(0, 0, 'next'); break;
      case 'End': go(MAIN_COUNT - 1, SL[MAIN_COUNT - 1].builds.length - 1, 'instant'); break;
      case 'f': case 'F': toggleFs(); break;
      case 'n': case 'N': toggle('#notes'); break;
      case 'o': case 'O': toggle('#overview'); break;
      case 'b': case 'B': case '.': AU.stop(); toggle('#black'); break;
      case 'a': case 'A': go(cur.s, cur.k, 'replay'); break;
      case 'm': case 'M': AU.setMuted(!AU.muted); if (video) video.muted = AU.muted; break;
      case 'v': case 'V': if ($('#video-ov').classList.contains('on')) closeVideo(); else openVideo(); break;
      case 'Escape': toggle('#overview', false); toggle('#notes', false); toggle('#black', false); closeVideo(); break;
      default: return;
    }
    e.preventDefault();
  });
  document.addEventListener('click', function (e) {
    if (e.button !== 0) return;
    if ($('#black').classList.contains('on')) { toggle('#black', false); return; }
    if (e.target.closest('a, button, iframe, video, #notes, #overview, input, label')) return;
    if ($('#video-ov').classList.contains('on')) return;
    next();
  });
  // A click inside the A1 iframe moves keyboard focus into it (another origin on file://), which would swallow
  // the clicker's PageDown/PageUp. Take focus back right after, so the deck keeps receiving keys.
  window.addEventListener('blur', function () {
    setTimeout(function () {
      var f = document.activeElement;
      if (f && f.tagName === 'IFRAME') { try { f.blur(); } catch (e) { } try { window.focus(); } catch (e) { } }
    }, 120);
  });
  window.addEventListener('hashchange', function () {
    var m = /^#(\d+)(?:\/(\d+))?/.exec(location.hash); if (!m) return;
    var s = (+m[1]) - 1, k = +(m[2] || 0);
    if (s !== cur.s || k !== cur.k) go(s, k, 'instant');
  });

  function start() {
    if (start.done) return; start.done = true;
    // preload every clip the deck plays (and expose data-audio elements for checks)
    ['ivr_de', EN_CLIP, 'lang_de', 'lang_ru', 'lang_uk', 'lang_ar', 'lang_tr', 'intake_full', 'call_full', 'result_ru'].forEach(function (id) { AU.get(id); });
    buildOverview();
    $('#cover').classList.add('gone');
    var m = /^#(\d+)(?:\/(\d+))?/.exec(location.hash);
    if (m) go((+m[1]) - 1, +(m[2] || 0), 'instant'); else go(0, 0, 'next');
  }
  var fontLoads = [
    '600 100px "Fraunces"', '400 40px "Fraunces"', '400 30px "Source Sans 3"', '600 30px "Source Sans 3"'
  ].map(function (f) { return document.fonts.load(f, 'Aa'); })
    .concat([document.fonts.load('600 30px "Source Serif 4"', 'Жж'), document.fonts.load('400 30px "Source Sans 3"', 'Жж'),
      document.fonts.load('600 30px "Noto Naskh Arabic"', 'عربي'), document.fonts.load('400 30px "Noto Sans Arabic"', 'عربي'),
      document.fonts.load('400 30px "Fraunces"', 'Früh')]);
  Promise.all(fontLoads).then(function () { return document.fonts.ready; }).then(start, start);
  setTimeout(start, 4000);

  window.deck = {
    go: go, next: next, prev: prev, state: function () { return { s: cur.s, k: cur.k }; },
    slides: function () { return SL.map(function (S) { return { id: S.id, title: S.title, steps: S.builds.length, appendix: S.appendix || null }; }); },
    audio: AU
  };
})();
