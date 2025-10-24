// 创建一个空数组
const data = []
data.push (JSON.parse(localStorage.getItem('data')) || [])
// function getId() {
//   if (data.length == false) {
//     return 1
//   } else {
//     return data.length + 1
//   }
// }
// let n = 0
// if (data.length == false) {
//   n = 1
// } else {
//   n = data.length + 1
// }
// 获取DOM对象
const info = document.querySelector('.info')
const uname = document.querySelector('.uname')
const age = document.querySelector('.age')
const gender = document.querySelector('.gender')
const salary = document.querySelector('.salary')
const city = document.querySelector('.city')
const table = document.querySelector('tbody')
// 1.渲染业务
// 1.1提交事件
info.addEventListener('submit', function (e) {
  // 1.1.1阻止浏览器默认行为
  e.preventDefault()
  // console.log('事件成功创建');
  // 1.1.2创建数组对象
  const obj = {
    stuId: data.length == null ? 1 : data.length + 1,
    uname: uname.value,
    age: age.value,
    gender: gender.value,
    salary: salary.value,
    city: city.value,
  }
  localStorage.setItem('data', JSON.stringify(obj))
  // console.log(JSON.stringify(obj));
  data.push(JSON.parse(localStorage.getItem('data')))
  render()
})
function render() {
  table.innerHTML = ''
  for (let i = 0; i < data.length; i++) {
    const tr = document.createElement('tr')
    table.appendChild(tr)
    tr.innerHTML = `
    <td>${data[i].stuId}</td>
      <td>${data[i].uname}</td>
      <td>${data[i].age}</td>
      <td>${data[i].gender}</td>
      <td>${data[i].salary}</td>
      <td>${data[i].city}</td>
      <td>
        <a href="javascript:">删除</a>
      </td>
    `
  }
}
render()