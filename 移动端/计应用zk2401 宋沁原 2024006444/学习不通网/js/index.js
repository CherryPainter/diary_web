// 精品模块数据
const cardData = [
  {
    link: './media.html',
    herf: "./images/ins图片1s.png",
    title: "Node.js开发从Hello World到Hello Error",
    num: "1546346"
  },
  {
    link: '#',
    herf: "./images/ins图片1ss.png",
    title: "JavaScript从万能胶水到一团浆糊",
    num: "453434"
  },
  {
    link: '#',
    herf: "./images/ins图片2s.png",
    title: "服务器运维管理从网络异常到硬盘全红",
    num: "8763454"
  },
  {
    link: '#',
    herf: "./images/ins图片2ss.png",
    title: "Debug455个经典案例，让电脑开机蓝屏",
    num: "487634"
  },
  {
    link: '#',
    herf: "./images/ins图片3s.png",
    title: "Android开发大全——从开始到转行",
    num: "786453"
  },
  {
    link: '#',
    herf: "./images/ins图片3ss.png",
    title: "MySQL进阶：从表结构混乱到数据冗余",
    num: "35478786"
  },
  {
    link: '#',
    herf: "./images/ins图片2s.png",
    title: "网络安全：从WiFi蹭网到实名举报",
    num: "456786"
  },
  {
    link: '#',
    herf: "./images/ins图片1s.png",
    title: "运维基础：从定时重启到全时救火",
    num: "5467867"
  },
  {
    link: '#',
    herf: "./images/ins图片3s.png",
    title: "Tailwind从原子级别美感到视觉崩坏",
    num: "4378634"
  },
  {
    link: '#',
    herf: "./images/ins图片1ss.png",
    title: "React实战：从组件复用到情绪复用",
    num: "3743453"
  }
]
// 精品模块渲染函数
function render() {
  // 1.声明一个空字符串存储处理好的数据
  let str = ''
  // 2.遍历对应数据
  cardData.forEach(item => {
    // 解构赋值
    const { link, herf, title, num } = item
    // 返回处理后的数据给str
    return str += ` 
      <a href="${link}" title="${title}">
        <div class="col">
          <div class="card h-100">
            <img src="${herf}" class="card-img-top" alt="${title}">
            <div class="card-body">
              <p class="card-text text-truncate">${title}</p>
              <div class="info">
                <span>高级</span> • <span>${num}</span>人在学习
              </div>
            </div>
          </div>
        </div>
      </a>
      `
  })
  // 将str添加到精品模块中
  document.querySelector('.renderBox').innerHTML = str
}
render()

// 不同类别的数据
const classData = [
  {
    classlists: "hot",
    leftImg: "./images/卡片1.png",
    topImg: "./images/上图.png",
    card: [
      {
        link: '#',
        cl: '热门',
        url: "./images/合作2s.png",
        title: "Linux入门：从终端小白到sudo rm -rf /",
        num: "42181"
      },
      {
        link: '#',
        cl: '热门',
        url: "./images/合作3s.png",
        title: "服务器部署：从远程登录到远走高飞",
        num: "42618"
      },
      {
        link: '#',
        cl: '热门',
        url: "./images/合作4s.png",
        title: "MongoDB实战：从非关系到没关系",
        num: "452731"
      },
      {
        link: '#',
        cl: '热门',
        url: "./images/合作5s.png",
        title: "iOS性能优化从卡顿到原地重启",
        num: "84621"
      }]
  },
  {
    classlists: "Elementary",
    leftImg: "./images/卡片1.png",
    topImg: "./images/上图1.png",
    card: [
      {
        link: '#',
        cl: '初级',
        url: "./images/合作1s.png",
        title: "Linux入门：从终端小白到sudo rm -rf /",
        num: "42181"
      },
      {
        link: '#',
        cl: '初级',
        url: "./images/合作1ss.png",
        title: "服务器部署：从远程登录到远走高飞",
        num: "42618"
      },
      {
        link: '#',
        cl: '初级',
        url: "./images/合作2s.png",
        title: "MongoDB实战：从非关系到没关系",
        num: "452731"
      },
      {
        link: '#',
        cl: '初级',
        url: "./images/合作2ss.png",
        title: "iOS性能优化从卡顿到原地重启",
        num: "84621"
      }]
  },
  {
    classlists: "Intermediate",
    leftImg: "./images/合作5ssr.png",
    topImg: "./images/上图2.png",
    card: [
      {
        link: '#',
        cl: '中级',
        url: "./images/合作3s.png",
        title: "Vue从入门到怒删node_modules",
        num: "423451"
      },
      {
        link: '#',
        cl: '中级',
        url: "./images/合作3ss.png",
        title: "Python从爬虫到被反爬",
        num: "245181"
      },
      {
        link: '#',
        cl: '中级',
        url: "./images/合作4s.png",
        title: "HTML5从结构语义到失去意义",
        num: "243181"
      },
      {
        link: '#',
        cl: '中级',
        url: "./images/合作4ss.png",
        title: "零基础学c语言，学完负基础",
        num: "134549"
      }]
  }, {
    classlists: "Advanced",
    leftImg: "./images/合作5ssr.png",
    topImg: "./images/Python+人工智能.png",
    card: [{
      link: '#',
      cl: '高级',
      url: "./images/合作5s.png",
      title: "Mysql从删库到跑路",
      num: "34246"
    },
    {
      link: '#',
      cl: '高级',
      url: "./images/合作5ss.png",
      title: "Css从绘制框架到改行画画",
      num: "723164"
    },
    {
      link: '#',
      cl: '高级',
      url: "./images/合作3s.png",
      title: "服务器运维管理从网维到网管",
      num: "6731325"
    },
    {
      link: '#',
      cl: '高级',
      url: "./images/合作3ss.png",
      title: "PHP由初学至搬砖",
      num: "4242181"
    }]
  }
]
// 编程入门模块·绑定点击事件逻辑
// 利用事件委托，对每个a进行绑定事件
document.querySelector('.ty-nav ul').addEventListener('click', e => {
  // 阻止默认行为
  e.preventDefault()
  // 只有事件对象所指为a执行筛选
  if (e.target.tagName === 'A') {
    // .actives是点击后的样式绑定，主要为排他思想
    document.querySelector('.actives').classList.remove('actives')
    e.target.classList.add('actives')
    // 筛选后的数据缓存处
    let arr = []
    // 利用自定义属性得知需要渲染的数据类
    if (e.target.dataset.id === 'hot') {
      arr = classData.filter(item => item.classlists === 'hot')
    }
    if (e.target.dataset.id === 'Elementary') {
      arr = classData.filter(item => item.classlists === 'Elementary')
    }
    if (e.target.dataset.id === 'Intermediate') {
      arr = classData.filter(item => item.classlists === 'Intermediate')
    }
    if (e.target.dataset.id === 'Advanced') {
      arr = classData.filter(item => item.classlists === 'Advanced')
    }
    // 因为A类楼层用的同一套渲染函数，为了避免bug用index索引数据该渲染的位置 index=1 对应的是.ty-main
    let index = 1
    filterRender(arr, index)
  }
})
// 模拟点击·默认为hot模块
document.querySelector('[data-id=hot]').click()

// 数据分析师模块·绑定点击事件逻辑
// 逻辑同上，但类名有所区别
document.querySelector('.uu').addEventListener('click', e => {
  e.preventDefault()
  if (e.target.tagName === 'A') {
    document.querySelector('.uu .actives').classList.remove('actives')
    e.target.classList.add('actives')
    let arr = []
    if (e.target.dataset.id === 'hot2') {
      arr = classData.filter(item => item.classlists === 'hot')
    }
    if (e.target.dataset.id === 'Elementary2') {
      arr = classData.filter(item => item.classlists === 'Elementary')
    }
    if (e.target.dataset.id === 'Intermediate2') {
      arr = classData.filter(item => item.classlists === 'Intermediate')
    }
    if (e.target.dataset.id === 'Advanced2') {
      arr = classData.filter(item => item.classlists === 'Advanced')
    }
    let index = 2
    filterRender(arr, index)
  }
})
document.querySelector('[data-id=hot2]').click()

// A类楼层渲染函数
function filterRender(arr, index) {
  // 处理后的数据缓存区
  let str = ''
  // 处理整个楼层的数据
  arr.forEach(item => {
    // 解构赋值
    const { leftImg, topImg, card } = item
    // 卡片区数据缓存区
    let cards = ''
    // 处理卡片模块
    card.forEach((item) => {
      // 解构赋值
      const { cl, url, title, num } = item
      // 返回处理后的卡片
      return cards += `
        <a href="#" title="${title}">
          <div class="col">
            <div class="card h-100">
              <img src=${url} class="card-img-top" alt="...">
              <div class="card-body">
                <p class="card-text text-truncate">${title}</p>
                <div class="info">
                  <span>${cl}</span> • <span>${num}</span>人在学习
                </div>
              </div>
            </div>
          </div>
        </a>
      `
    })
    // 返回整个楼层给str
    return str += `
      <div class="ty-main">
        <div class="ty-left"><img src=${leftImg} alt=""></div>
        <div class="ty-right"><img src=${topImg} alt=""></div>
        <div class="main mt-4">
          <div class="row row-cols-2 row-cols-md-4 row-cols-lg-4 row-cols-sm-3 g-3 renderBox2">
            ${cards}
          </div>
        </div>
      </div>
    `
  })
  // 判断索引，进而找到数据数据该渲染在哪
  if (index === 1) document.querySelector('.ty-main').innerHTML = str
  if (index === 2) document.querySelector('.render-ty').innerHTML = str
}

// B类楼层数据
const otherData = [
  {
    classlists: "hot",
    card: [
      {
        link: '#',
        cl: '热门',
        url: "./images/ins图片1s.png",
        title: "Linux入门：从终端小白到sudo rm -rf /",
        num: "42181"
      },
      {
        link: '#',
        cl: '热门',
        url: "./images/ins图片3s.png",
        title: "服务器部署：从远程登录到远走高飞",
        num: "42618"
      },
      {
        link: '#',
        cl: '热门',
        url: "./images/ins图片2s.png",
        title: "MongoDB实战：从非关系到没关系",
        num: "452731"
      },
      {
        link: '#',
        cl: '热门',
        url: "./images/ins图片1ss.png",
        title: "iOS性能优化从卡顿到原地重启",
        num: "84621"
      },
      {
        link: '#',
        cl: '热门',
        url: "./images/ins图片2ss.png",
        title: "iOS性能优化从卡顿到原地重启",
        num: "84621"
      }
    ]
  }, {
    classlists: "Elementary",
    card: [
      {
        link: '#',
        cl: '初级',
        url: "./images/合作1s.png",
        title: "Linux入门：从终端小白到sudo rm -rf /",
        num: "42181"
      },
      {
        link: '#',
        cl: '初级',
        url: "./images/合作1ss.png",
        title: "服务器部署：从远程登录到远走高飞",
        num: "42618"
      },
      {
        link: '#',
        cl: '初级',
        url: "./images/合作2s.png",
        title: "MongoDB实战：从非关系到没关系",
        num: "452731"
      },
      {
        link: '#',
        cl: '初级',
        url: "./images/合作2ss.png",
        title: "iOS性能优化从卡顿到原地重启",
        num: "84621"
      },
      {
        link: '#',
        cl: '初级',
        url: "./images/合作2ss.png",
        title: "iOS性能优化从卡顿到原地重启",
        num: "84621"
      }
    ]
  }, {
    classlists: "Intermediate",
    card: [
      {
        link: '#',
        cl: '中级',
        url: "./images/合作3s.png",
        title: "Vue从入门到怒删node_modules",
        num: "423451"
      },
      {
        link: '#',
        cl: '中级',
        url: "./images/合作3ss.png",
        title: "Python从爬虫到被反爬",
        num: "245181"
      },
      {
        link: '#',
        cl: '中级',
        url: "./images/合作4s.png",
        title: "HTML5从结构语义到失去意义",
        num: "243181"
      },
      {
        link: '#',
        cl: '中级',
        url: "./images/合作4ss.png",
        title: "零基础学c语言，学完负基础",
        num: "134549"
      },
      {
        link: '#',
        cl: '中级',
        url: "./images/合作4ss.png",
        title: "零基础学c语言，学完负基础",
        num: "134549"
      }
    ]
  }, {
    classlists: "Advanced",
    card: [{
      link: '#',
      cl: '高级',
      url: "./images/合作5s.png",
      title: "Mysql从删库到跑路",
      num: "34246"
    },
    {
      link: '#',
      cl: '高级',
      url: "./images/合作5ss.png",
      title: "Css从绘制框架到改行画画",
      num: "723164"
    },
    {
      link: '#',
      cl: '高级',
      url: "./images/合作3s.png",
      title: "服务器运维管理从网维到网管",
      num: "6731325"
    }, {
      link: '#',
      cl: '高级',
      url: "./images/合作3ss.png",
      title: "PHP由初学至搬砖",
      num: "4242181"
    },
    {
      link: '#',
      cl: '高级',
      url: "./images/合作3ss.png",
      title: "PHP由初学至搬砖",
      num: "4242181"
    }]
  }
]

// 机器学习工程师模块·绑定点击事件逻辑
// 逻辑同上
document.querySelector('.uul').addEventListener('click', (e) => {
  e.preventDefault()
  if (e.target.tagName === 'A') {
    document.querySelector('.uul .actives').classList.remove('actives')
    e.target.classList.add('actives')
    let arr = []
    if (e.target.dataset.id === 'hot3') {
      arr = otherData.filter((item) => item.classlists === 'hot')
    }
    if (e.target.dataset.id === 'Elementary3') {
      arr = otherData.filter((item) => item.classlists === 'Elementary')
    }
    if (e.target.dataset.id === 'Intermediate3') {
      arr = otherData.filter((item) => item.classlists === 'Intermediate')
    }
    if (e.target.dataset.id === 'Advanced3') {
      arr = otherData.filter((item) => item.classlists === 'Advanced')
    }
    let index = 3
    floorRender(arr, index)
  }
})
document.querySelector('[data-id=hot3]').click()

// 前端开发工程师模块·绑定点击事件逻辑
// 逻辑同上
document.querySelector('.uull').addEventListener('click', (e) => {
  e.preventDefault()
  if (e.target.tagName === 'A') {
    document.querySelector('.uull .actives').classList.remove('actives')
    e.target.classList.add('actives')
    let arr = []
    if (e.target.dataset.id === 'hot4') {
      arr = otherData.filter((item) => item.classlists === 'hot')
    }
    if (e.target.dataset.id === 'Elementary4') {
      arr = otherData.filter((item) => item.classlists === 'Elementary')
    }
    if (e.target.dataset.id === 'Intermediate4') {
      arr = otherData.filter((item) => item.classlists === 'Intermediate')
    }
    if (e.target.dataset.id === 'Advanced4') {
      arr = otherData.filter((item) => item.classlists === 'Advanced')
    }
    let index = 4
    floorRender(arr, index)
  }
})
document.querySelector('[data-id=hot4]').click()

// B类楼层渲染函数-逻辑同精品模块渲染函数
function floorRender(arr, index) {
  let str = ''
  arr.forEach(item => {
    item.card.forEach(item => {
      const { cl, url, title, num } = item
      return str += ` 
      <a href="#" title="${title}">
        <div class="col">
          <div class="card h-100">
            <img src="${url}" class="card-img-top" alt="${title}">
            <div class="card-body">
              <p class="card-text text-truncate">${title}</p>
              <div class="info">
                <span>${cl}</span> • <span>${num}</span>人在学习
              </div>
            </div>
          </div>
        </div>
      </a>
      `
    })
  })
  if (index === 3) document.querySelector('.renderBox3').innerHTML = str
  if (index === 4) document.querySelector('.renderBox4').innerHTML = str
}