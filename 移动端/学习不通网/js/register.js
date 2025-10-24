// -------验证码模块---------
const vCode = document.querySelector('.vc')
let i = 8
let flag = true
vCode.addEventListener('click', e => {
  e.preventDefault()
  if (flag) {
    vCode.style.color = '#999'
    vCode.innerHTML = `0${i}秒后刷新`
    flag = false
    let timeId = setInterval(() => {
      i--
      vCode.innerHTML = `0${i}秒后刷新`
      if (i === 0) {
        clearInterval(timeId)
        vCode.style.color = '#1D85DA'
        vCode.innerHTML = `重新刷新`
        i = 5
        flag = true
      }
    }, 1000)
  }
})

// -------用户名模块---------
const uname = document.querySelector('[name="uname"]')
uname.addEventListener('change', verifyName)
function verifyName() {
  const reg = /^[a-zA-Z0-9_\u4e00-\u9fa5]{2,10}$/

  const span = uname.nextElementSibling
  const pass = span.nextElementSibling
  if (!reg.test(uname.value)) {
    pass.style.opacity = 0
    span.innerText = '输入不合法，请输入2-10位字符'
    return false
  }
  span.innerText = ''
  pass.style.opacity = 1
  return true
}

// -------手机号模块---------
const phone = document.querySelector('[name="phone"]')
phone.addEventListener('change', verifyPhone)
function verifyPhone() {
  const reg = /^1(3\d|4[5-9]|5[0-35-9]|6[567]|7[0-8]|8\d|9[0-35-9])\d{8}/

  const span = phone.nextElementSibling
  const pass = span.nextElementSibling
  if (!reg.test(phone.value)) {
    pass.style.opacity = 0
    span.innerText = '请确认电话号码是否正确'
    return false
  }
  span.innerText = ''
  pass.style.opacity = 1
  return true
}

// -------短信验证模块---------
const code = document.querySelector('[name="PVC"]')
code.addEventListener('change', verifyCode)
function verifyCode() {
  const reg = /^\d{6}$/
  const span = code.nextElementSibling
  const pass = span.nextElementSibling
  if (!reg.test(code.value)) {
    pass.style.opacity = 0
    span.innerText = '验证码错误！'
    return false
  }
  span.innerText = ''
  pass.style.opacity = 1
  return true
}

// --------------------密码模块-------------------
const password = document.querySelector('[name="pwd"]')
password.addEventListener('change', verifyPassword)
function verifyPassword() {
  const reg = /^[a-zA-Z0-9-_]{6,20}$/
  const span = password.nextElementSibling
  const pass = span.nextElementSibling
  if (!reg.test(password.value)) {
    pass.style.opacity = 0
    span.innerText = '设置6至20位字母、数字和符号组合'
    return false
  }
  span.innerText = ''
  pass.style.opacity = 1
  return true
}

// -------------密码再验证模块------------
const confirm = document.querySelector('[name="tpwd"]')
confirm.addEventListener('change', verfiryConfirm)
function verfiryConfirm() {
  const span = confirm.nextElementSibling
  const pass = span.nextElementSibling
  if (password.value != '') {
    console.log('pass');
    if (confirm.value != password.value) {
      pass.style.opacity = 0
      span.innerText = '密码不吻合'
      return false
    }
    span.innerText = ''
    pass.style.opacity = 1
    return true
  }
}

// ---------表单提交验证模块------------
const form = document.querySelector('[name="register"]')
form.addEventListener('submit', e => {
  const clause = document.querySelector('[name="confirmation"]')
  if (!clause.checked) {
    e.preventDefault()
    if (window.confirm('是否同意用户服务协议')) {
      clause.checked = true
    }
  }
  if (!verifyName()) e.preventDefault()
  if (!verifyPhone()) e.preventDefault()
  if (!verifyCode()) e.preventDefault()
  if (!verifyPassword()) e.preventDefault()
  if (!verfiryConfirm()) e.preventDefault()

  localStorage.setItem('username', uname.value)
  localStorage.setItem('password', password.value)
  localStorage.setItem('phone', phone.value)
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
})


