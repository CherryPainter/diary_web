const button = document.querySelector('.enzh');
for (let i = 1; i <= 9; i++) {
  const ul = document.createElement('ul');
  for (let j = 1; j <= i; j++) {
    const li = document.createElement('li');
    li.textContent = `${j} × ${i} = ${i * j}`;
    ul.appendChild(li);
  }
  document.querySelector('main').appendChild(ul);
}
function changeLang() {
  const chars = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
  if (button.textContent === '中文口诀') {
    document.querySelector('main').innerHTML = '';
    button.textContent = '还原数字口诀'
    for (let i = 1; i <= 9; i++) {
      const ul = document.createElement('ul');
      for (let j = 1; j <= i; j++) {
        const li = document.createElement('li');
        sum = j * i;
        if (sum >= 10) {
          li.textContent = `${chars[j]} ${chars[i]} 得 ${chars[Math.floor(sum / 10)]}十${chars[sum % 10]}`;
        } else {
          li.textContent = `${chars[j]} ${chars[i]} 得 ${chars[i * j]}`;
        }
        ul.appendChild(li);
      }
      document.querySelector('main').appendChild(ul);
    }
  } else if (button.textContent === '还原数字口诀') {
    document.querySelector('main').innerHTML = '';
    button.textContent = '中文口诀';
    for (let i = 1; i <= 9; i++) {
      const ul = document.createElement('ul');
      for (let j = 1; j <= i; j++) {
        const li = document.createElement('li');
        li.textContent = `${j} × ${i} = ${i * j}`;
        ul.appendChild(li);
      }
      document.querySelector('main').appendChild(ul);
    }
  }
}
button.addEventListener('click', changeLang);