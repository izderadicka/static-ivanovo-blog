/* Progressive enhancements: content and navigation remain available without JS. */
const menu = document.querySelector('.menu-toggle');
if (menu) {
  menu.hidden = false;
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    document.querySelector('#mobile-menu').hidden = !open;
  });
}
for (const table of document.querySelectorAll('.entry-content table')) {
  if (table.closest('.gist, .table-scroll')) continue;
  const wrapper = document.createElement('div');
  wrapper.className = 'table-scroll';
  wrapper.tabIndex = 0;
  wrapper.setAttribute('role', 'region');
  wrapper.setAttribute('aria-label', table.caption?.textContent || 'Reference table');
  table.before(wrapper);
  wrapper.append(table);
}
for (const tabs of document.querySelectorAll('[data-tabs]')) {
  const panels = [...tabs.querySelectorAll(':scope > .tab-panel')];
  if (panels.length < 2) continue;
  const controls = document.createElement('div');
  controls.className = 'tab-controls';
  controls.setAttribute('role', 'tablist');
  controls.setAttribute('aria-label', 'Page sections');
  const activate = (index, focus = false) => {
    panels.forEach((panel, i) => {
      panel.hidden = i !== index;
      buttons[i].setAttribute('aria-selected', String(i === index));
      buttons[i].tabIndex = i === index ? 0 : -1;
    });
    if (focus) buttons[index].focus();
  };
  const buttons = panels.map((panel, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.id = panel.id + '-button';
    button.textContent = panel.querySelector('h2')?.textContent || `Section ${index + 1}`;
    button.setAttribute('role', 'tab');
    button.setAttribute('aria-controls', panel.id);
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', button.id);
    panel.tabIndex = 0;
    button.addEventListener('click', () => activate(index));
    button.addEventListener('keydown', (event) => {
      const keys = {ArrowRight: (index + 1) % panels.length, ArrowLeft: (index + panels.length - 1) % panels.length, Home: 0, End: panels.length - 1};
      if (event.key in keys) { event.preventDefault(); activate(keys[event.key], true); }
    });
    controls.append(button);
    return button;
  });
  tabs.prepend(controls);
  tabs.classList.add('is-enhanced');
  const followFragment = () => {
    let target;
    try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch { return; }
    const index = panels.findIndex(panel => panel === target || panel.contains(target));
    if (index >= 0) activate(index);
  };
  activate(0);
  followFragment();
  addEventListener('hashchange', followFragment);
}
for (const gallery of document.querySelectorAll('[data-gallery]')) {
  const slides = [...gallery.querySelectorAll(':scope > figure')];
  if (slides.length < 2) continue;
  const controls = document.createElement('div');
  controls.className = 'gallery-controls';
  const previous = document.createElement('button');
  const next = document.createElement('button');
  const status = document.createElement('span');
  previous.type = next.type = 'button';
  previous.textContent = '← Previous';
  next.textContent = 'Next →';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  let active = 0;
  const show = (index) => {
    active = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== active; });
    status.textContent = `${active + 1} / ${slides.length}`;
  };
  previous.addEventListener('click', () => show(active - 1));
  next.addEventListener('click', () => show(active + 1));
  controls.append(previous, status, next);
  gallery.append(controls);
  gallery.classList.add('is-enhanced');
  show(0);
}
const search = document.querySelector('#search');
if (search) {
  const stylesheet = document.createElement('link');
  stylesheet.rel = 'stylesheet';
  stylesheet.href = '/pagefind/pagefind-ui.css';
  document.head.append(stylesheet);
  const script = document.createElement('script');
  script.src = '/pagefind/pagefind-ui.js';
  script.onload = () => {
    search.replaceChildren();
    const ui = new PagefindUI({element: '#search', showSubResults: true, showImages: false});
    const query = new URLSearchParams(location.search).get('q');
    if (query) ui.triggerSearch(query);
  };
  script.onerror = () => {
    const status = search.querySelector('.search-status');
    status.textContent = 'Search is temporarily unavailable. ';
    const archiveLink = document.createElement('a');
    archiveLink.href = '/archives/';
    archiveLink.textContent = 'Browse the archives';
    status.append(archiveLink);
  };
  document.head.append(script);
}
// Old WordPress search links remain useful on static previews as well.
const oldSearch = new URLSearchParams(location.search).get('s');
if (oldSearch && location.pathname === '/') location.replace('/search/?q=' + encodeURIComponent(oldSearch));
