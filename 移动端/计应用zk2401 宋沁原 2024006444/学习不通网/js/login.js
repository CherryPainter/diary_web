const unameAlert = document.querySelector('.uname')
const pwdAlert = document.querySelector('.pwd')

const uname = document.querySelector('[name="username"]')
uname.addEventListener('change', verifyName)

function verifyName() {
  if (!(uname.value == localStorage.getItem('username') || uname.value == localStorage.getItem('phone'))) {
    unameAlert.style.display = 'block'
    return false
  }
  unameAlert.style.display = 'none'
  return true
}

const password = document.querySelector('[name="password"]')
password.addEventListener('change', verifyPassword)

function verifyPassword() {
  if (!(password.value == localStorage.getItem('password'))) {
    pwdAlert.style.display = 'block'
    return false
  }
  pwdAlert.style.display = 'none'
  return true
}

document.querySelector('[name="login"]').addEventListener('submit', e => {
  const checked = document.querySelector('#my-checkbox')
  if (!checked.checked) {
    e.preventDefault()
    if (window.confirm('是否同意用户服务协议')) {
      checked.checked = true
    }
  }
  if (!verifyName()) e.preventDefault()
  if (!verifyPassword()) e.preventDefault()

  e.preventDefault()
  const time = document.querySelector('.time')
  document.querySelector('.ph').style.display = 'block'
  let num = 5
  let timeId = setInterval(() => {
    num--
    time.innerHTML = num
  }, 1000)
  setTimeout(() => {
    clearInterval(timeId)
    location.href = './index.html'
  }, 5000)
  localStorage.setItem('state', 'true')
})