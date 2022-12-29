const form = document.getElementById('competitionForm');

form['submitter'].value = localStorage.getItem('submitter');

form['submitter'].onchange = () => {
  localStorage.setItem('submitter', form['submitter'].value);
}


function listener(winner) {
  return () => {
    if (form['submitter'].value === '') {
      alert('You must provide your name first.')
      return;
    }
    form['winner'].value = winner;
    form.submit();
  }
}

const voteP1Btn = document.getElementById('voteP1Btn');
voteP1Btn.addEventListener('click', listener(1));
const voteP2Btn = document.getElementById('voteP2Btn');
voteP2Btn.addEventListener('click', listener(2));
const skipBtn = document.getElementById('skipBtn');
skipBtn.addEventListener('click', listener('skip'));

document.addEventListener('keypress', (event) => {
  if (event.key === 'f') {
    voteP1Btn.click();
  } else if (event.key === 'j') {
    voteP2Btn.click();
  } else if (event.key === 'q') {
    skipBtn.click();
  }
})
