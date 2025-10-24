// 获取元素
const uname = document.querySelector('.uname')
const age = document.querySelector('.age')
const gender = document.querySelector('.gender')
const salary = document.querySelector('.salary')
const city = document.querySelector('.city')
const tbody = document.querySelector('tbody')
// 获取所有带有name属性的 元素
const items = document.querySelectorAll('[name]')
// 声明一个空的数组， 增加和删除都是对这个数组进行操作
const arr = []

// 1. 录入模块
// 1.1 表单提交事件
const info = document.querySelector('.info')
info.addEventListener('submit', function (e) {
  // 阻止默认行为  不跳转
  e.preventDefault()
  // console.log(11)

  // 这里进行表单验证  如果不通过，直接中断，不需要添加数据
  // 先遍历循环
  for (let i = 0; i < items.length; i++) {
    if (items[i].value === '') {
      return alert('输入内容不能为空')
    }
  }
  // 创建新的对象
  const obj = {
    stuId: arr.length + 1,
    uname: uname.value,
    age: age.value,
    gender: gender.value,
    salary: salary.value,
    city: city.value
  }
  // console.log(obj)
  // 追加给数组里面
  arr.push(obj)
  // console.log(arr)
  // 清空表单  重置 
  this.reset()
  // 调用渲染函数
  render()
})


// 2. 渲染函数 因为增加和删除都需要渲染
function render() {
  // 先清空tbody 以前的行 ，把最新数组里面的数据渲染完毕 
  tbody.innerHTML = ''
  // 遍历arr数组
  for (let i = 0; i < arr.length; i++) {
    // 生成 tr 
    const tr = document.createElement('tr')
    tr.innerHTML = `
      <td>${arr[i].stuId}</td>
      <td>${arr[i].uname}</td>
      <td>${arr[i].age}</td>
      <td>${arr[i].gender}</td>
      <td>${arr[i].salary}</td>
      <td>${arr[i].city}</td>
      <td>
        <a href="javascript:" data-id=${i}>删除</a>
      </td>
    `
    // 追加元素  父元素.appendChild(子元素)
    tbody.appendChild(tr)
  }
}


// 3. 删除操作
// 3.1 事件委托 tbody
tbody.addEventListener('click', function (e) {
  if (e.target.tagName === 'A') {
    // 得到当前元素的自定义属性 data-id
    // console.log(e.target.dataset.id)
    // 删除arr 数组里面对应的数据
    arr.splice(e.target.dataset.id, 1)
    console.log(arr)
    // 从新渲染一次
    render()
  }
})