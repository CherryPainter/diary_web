if (localStorage.getItem('state') == 'true') {
  const lr = document.querySelector('.login')
  const user = document.querySelector('.user')
  const uname = document.querySelector('.uname')
  uname.innerHTML = localStorage.getItem('username')
  lr.style.display = 'none'
  user.style.display = 'block'
}
// else {
//   if (window.confirm('账号数据丢失请重新注册')) {
//     location.href = './register.html'
//   }
// }
