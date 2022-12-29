/* Sidebar */
'use strict';

const COMPETITOR_LIST = '/competitor';

function setAttributes(el, attrs) {
  for (const key in attrs) {
    el.setAttribute(key, attrs[key]);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('span.hymnary-link').forEach((el) => {
    const a = document.createElement('a');
    setAttributes(a, {
      dataBsToggle: 'tooltip',
      title: 'View on Hymnary.org',
      target: '_blank',
      href: el.dataset.hurl,
    });
    a.className = 'btn p-0 m-0 fs-6';
    a.innerText = '📗';
    el.appendChild(a);

    new bootstrap.Tooltip(a);
  });
});
