const COMPETITOR_LIST = '/competitor';
(async function () {
  const hymns = await fetch(COMPETITOR_LIST);
  console.log(await hymns.json())
})()
