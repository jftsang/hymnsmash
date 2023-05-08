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


/* https://javascript.info/task/sortable-table */

document.addEventListener("DOMContentLoaded",
  (e) => {
    const leaderboard = document.getElementById("leaderboard");

    function sortLeaderboard(evt) {
      if (evt.target.tagName !== "TH")
        return;

      const th = evt.target;

      function sortGrid(colNum, type) {
        const currentSort = Number(leaderboard.dataset.currentSort);
        let reverse = Boolean(leaderboard.dataset.reverse);
        if (colNum === currentSort) {
          reverse = !reverse;
          leaderboard.dataset.reverse = reverse ? "yes" : "";
        }
        leaderboard.dataset.currentSort = colNum;

        const tbody = leaderboard.querySelector("tbody");
        const rowsArray = Array.from(tbody.rows);

        function compare(rowA, rowB) {
          const a = rowA.cells[colNum].innerText;
          const b = rowB.cells[colNum].innerText;

          let r;
          if (type === "number")
            r = Number(b) - Number(a);  // sort descending
          else if (type === "percentage")
            r = Number(b.substring(0, b.length - 1))
              - Number(a.substring(0, a.length - 1));
          else if (type === "string")
            r = (a > b) ? 1 : (a === b) ? 0 : -1;  // sort ascending
          else
            throw DOMException;

          if (reverse)
            r *= -1;
          return r;
        }

        rowsArray.sort(compare);
        tbody.append(...rowsArray);
      }

      sortGrid(th.cellIndex, th.dataset.type);
    }

    leaderboard.addEventListener("click", sortLeaderboard);
  }
);
