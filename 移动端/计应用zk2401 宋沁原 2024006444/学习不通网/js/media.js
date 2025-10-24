// document.querySelector('#comments').addEventListener('focus', e => {

// })
const comment = document.querySelector('#comments')
const list = document.querySelector('.list')
let comments = [
  {
    avatar: './images/图像.png',
    uname: '花环',
    comment: '大家都辛苦啦，感谢各位大大的努力，能圆满完成真是太好了[笑哭][支持]',
    date: '2022-10-10 20:29:21'
  },
  {
    avatar: './images/图像.png',
    uname: '花环',
    comment: '这个课程真的很全的啦~',
    date: '2022-10-10 20:29:21'
  },
  {
    avatar: './images/图像.png',
    uname: '花环',
    comment: '愿大家都是巧克力，乖巧刻苦又努力！',
    date: '2022-10-10 20:29:21'
  }
]

// --------渲染业务---------
function render() {
  let newArr = comments.map((ele, index) => {
    const { avatar, uname, comment, date } = ele
    return `
      <div class="item">
        <i class="avatar">
          <img src="${avatar}" alt="">
        </i>
        <div class="info">
          <p class="name">${uname}</p>
          <p class="text">${comment}</p>
          <p class="time">${date}</p>
          <a href="javascript:;" data-id=${index} class="del">删除</a>
        </div>
      </div>
    `
  })
  list.innerHTML = newArr.join('')
}
render()

// ---------获取评论--------
comment.addEventListener('focus', () => {

})