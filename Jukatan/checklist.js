(function () {
  var boxes = document.querySelectorAll('input.ck[data-k]');
  if (!boxes.length) return;
  var key = 'checklist:' + location.pathname;
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch (e) { saved = {}; }

  var bar = document.getElementById('ck-bar');
  var txt = document.getElementById('ck-txt');

  function update() {
    var n = 0;
    boxes.forEach(function (b) { if (b.checked) n++; });
    if (bar) bar.style.width = (n / boxes.length * 100) + '%';
    if (txt) txt.textContent = n + ' / ' + boxes.length + ' zrobione';
  }

  boxes.forEach(function (b) {
    var k = b.getAttribute('data-k');
    if (saved[k]) b.checked = true;
    b.addEventListener('change', function () {
      saved[k] = b.checked;
      try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
      update();
    });
  });

  var reset = document.getElementById('ck-reset');
  if (reset) reset.addEventListener('click', function () {
    boxes.forEach(function (b) { b.checked = false; });
    saved = {};
    try { localStorage.removeItem(key); } catch (e) {}
    update();
  });

  update();
})();
