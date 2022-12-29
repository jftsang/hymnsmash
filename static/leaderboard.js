document.addEventListener('DOMContentLoaded', () => {
    [].slice.call(document.querySelectorAll('span.leaderboard-competitor'))
      .map(function (span) {
          const cid = span.dataset['cid'];
          span.addEventListener('mouseenter', async () => {
            const r = await fetch('/competitor/' + cid);
            const j = await r.json();
            console.log(j);

            span.setAttribute('data-bs-toggle', 'tooltip');
            span.setAttribute('data-bs-html', 'true');
            span.setAttribute('title', j.weight);
          })
        }
      );
  }
);
