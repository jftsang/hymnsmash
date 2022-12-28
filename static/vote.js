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

document.getElementById('voteP1Btn').addEventListener('click', listener(1));
document.getElementById('voteP2Btn').addEventListener('click', listener(2));
document.getElementById('skipBtn').addEventListener('click', listener('skip'));
