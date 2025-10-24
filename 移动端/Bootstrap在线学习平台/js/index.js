let timerId = setInterval(function () {
  document.querySelector('.carousel-control-next-icon').click()
},2000)
document.querySelector('.diagram .times').addEventListener('mouseenter', () => {
  clearInterval(timerId)
})
document.querySelector('.diagram .times').addEventListener('mouseleave', () => {
  clearInterval(timerId)
  timerId = setInterval(function () {
  document.querySelector('.carousel-control-next-icon').click()
},2000)
})
document.querySelector('.carousel-control-next-icon').click()

const cardData = [
  {
    herf: "./images/course01.png",
    title: "JavaScript数据看板项目实战",
    num: "1126"
  },
  {
    herf: "./images/course02.png",
    title: "Vue.js实战——面经全端项目",
    num: "2726"
  },
  {
    herf: "./images/course03.png",
    title: "Vue.js实战——IHRM人资项目",
    num: "7192"
  },
  {
    herf: "./images/course04.png",
    title: "Vue.js实战——优医问诊项目",
    num: "8192"
  },
  {
    herf: "./images/course05.png",
    title: "小兔鲜电商小程序项目",
    num: "2703"
  },
  {
    herf: "./images/course06.png",
    title: "前端框架Flutter开发实战",
    num: "2841"
  },
  {
    herf: "./images/course07.png",
    title: "React.js项目实战——极客园H5(用户端)",
    num: "95682"
  },
  {
    herf: "./images/course08.png",
    title: "React.js项目实战——极客园PC端",
    num: "904"
  },
  {
    herf: "./images/course09.png",
    title: "Fetch API 实战",
    num: "1516"
  },
  {
    herf: "./images/course10.png",
    title: "Node.js零基础入门教程",
    num: "2766"
  }
]
function render() {
  let str = ''
  cardData.forEach(item => {
    const { herf, title, num } = item
    return str +=` <div class="col">
          <div class="card h-100">
            <img src="${herf}" class="card-img-top" alt="...">
            <div class="card-body">
              <p class="card-text text-truncate">${title}</p>
              <div class="info">
                <span>高级</span> • <span>${num}</span>人在学习
              </div>
            </div>
          </div>
        </div>
      `
  })
  document.querySelector('.renderBox').innerHTML= str
}
render()

const routeData = [
  {
    id: 'JavaEE',
    title: 'Java基础',
    contain:'Java基本用法,Java面向对象,集合技术&l/O技术,JDK的新特性&基础加强,XML配置解析技术'
  },
  {
    id: 'JavaEE',
    title: 'Java Web',
    contain:'数据库MySQL,数据库连接技术,网页开发技术,样式表技术,异步交互技术'
  },
  {
    id: 'JavaEE',
    title: 'Java开发框架',
    contain:'SpringMVC框架,MVcMyBatis框架,MyBatis Plus框架,Spring Boot技术,Gi版本控制'
  },
  {
    id: 'JavaEE',
    title: '中间件&服务框架',
    contain:'微服务注册中心,微服务调用,客户端负载均很,消息中间件,分布式缓存'
  },
  {
  id: '前端开发',
  title: '前端技术体系',
  contain: 'HTML5与CSS3,JavaScript基础,Vue框架,React框架,前端工程化工具Webpack'
  },
  {
    id: '前端开发',
    title: '网页开发基础',
    contain: 'HTML标签结构,CSS样式控制,JavaScript基本语法'
  },
  {
    id: '前端开发',
    title: '前端框架应用',
    contain: 'Vue组件开发,React状态管理,前端路由实现'
  },
  {
    id: '前端开发',
    title: '前端工程化',
    contain: 'Webpack打包工具,模块化开发,Babel语法转换'
  },
  {
    id: '大数据',
    title: '大数据开发',
    contain: 'Hadoop生态系统,Spark大数据处理,Hive数据仓库,HBase非关系型数据库,数据采集与可视化'
  },
  {
  id: '大数据',
  title: '大数据基础',
  contain: 'Hadoop框架原理,HDFS分布式文件系统,YARN资源调度'
  },
  {
    id: '大数据',
    title: '实时计算与处理',
    contain: 'Spark核心原理,流式处理Spark Streaming,Flink实时分析'
  },
  {
    id: '大数据',
    title: '数据仓库与分析',
    contain: 'Hive数据仓库,HBase列式数据库,数据可视化工具使用'
  },
  {
    id: '人工智能',
    title: 'AI与机器学习',
    contain: 'Python编程基础,机器学习算法,神经网络与深度学习,TensorFlow框架,计算机视觉&自然语言处理'
  },
  {
  id: '人工智能',
  title: '机器学习基础',
  contain: '监督学习&无监督学习,常用算法KNN/决策树/线性回归,Sklearn工具应用'
  },
  {
    id: '人工智能',
    title: '深度学习',
    contain: '神经网络结构,CNN卷积网络,RNN循环神经网络'
  },
  {
    id: '人工智能',
    title: 'AI项目实战',
    contain: '图像识别项目,NLP文本分类,语音识别与合成技术'
  },
  {
    id: 'UI设计',
    title: 'UI/UX设计',
    contain: '设计基础理论,色彩与排版规范,Adobe XD与Figma操作,用户体验研究,界面交互设计'
  },
  {
  id: 'UI设计',
  title: '界面设计基础',
  contain: 'UI设计规范,色彩搭配与字体选择,图标与界面组件设计'
  },
  {
    id: 'UI设计',
    title: '用户体验设计',
    contain: '用户行为分析,信息架构设计,可用性测试方法'
  },
  {
    id: 'UI设计',
    title: '工具与软件',
    contain: 'Figma协作设计,Photoshop界面设计,Adobe XD原型制作'
  },
  {
    id: '软件测试',
    title: '软件测试技术',
    contain: '测试基础理论,功能测试与性能测试,自动化测试Selenium,测试用例设计,缺陷管理工具Jira'
  },
  {
  id: '软件测试',
  title: '测试基础与流程',
  contain: '测试分类,测试流程模型,测试计划编写'
  },
  {
    id: '软件测试',
    title: '自动化测试',
    contain: 'Selenium自动化脚本,JUnit单元测试,接口自动化测试Postman'
  },
  {
    id: '软件测试',
    title: '性能与安全测试',
    contain: 'LoadRunner性能测试工具,安全测试方法,渗透测试基础'
  },
  {
    id: '产品经理',
    title: '产品经理技能',
    contain: '需求分析与原型设计,Axure原型工具,项目管理流程,用户调研方法,PRD文档撰写'
  },
  {
  id: '产品经理',
  title: '需求分析',
  contain: '竞品分析,用户画像绘制,用户访谈技巧'
  },
  {
    id: '产品经理',
    title: '产品设计',
    contain: '产品功能拆解,流程图与原型图设计,PRD文档撰写'
  },
  {
    id: '产品经理',
    title: '项目管理',
    contain: '敏捷开发Scrum,Jira任务管理,版本发布计划制定'
  },
  {
    id: '新媒体',
    title: '新媒体运营',
    contain: '内容策划与编辑,短视频运营技巧,社交媒体投放,数据分析与热点追踪,平台规则与品牌打造'
  },
  {
  id: '新媒体',
  title: '内容创作',
  contain: '爆款选题策划,图文编辑技巧,内容排版与美化'
  },
  {
    id: '新媒体',
    title: '平台运营',
    contain: '小红书种草运营,抖音短视频推广,微信公众号维护'
  },
  {
    id: '新媒体',
    title: '数据分析与转化',
    contain: '用户增长模型,数据后台使用,投放转化率优化'
  }
]

function routeDataRender(arr) {
  let str = ''
  let num = 0
  arr.forEach(item => {
    num++
    const { title, contain } = item
    let strs = ''
    contain.split(',').forEach(ele => {
      return strs +=`
      <span class="list-contain">${ele}</span>
      `
    })
    str +=`
    <div class="box-list col mt-4">
      <div class="left pb-2">
        <h5 class="list-title">${title}</h5>
          ${strs}
      </div>
      <div class="right">
        <div class="num">0${num}</div>
      </div>
    </div>
  `
  })
  document.querySelector('.renderList').innerHTML = str
}

document.querySelector('.navbars').addEventListener('click', function (e) {
  if (e.target.tagName === 'A' || e.target.tagName === 'SPAN') {
    e.preventDefault()
    document.querySelector('.actives').classList.remove('actives')
    e.target.parentNode.classList.add('actives')
    let arr = []
    if (e.target.dataset.id == 'JavaEE') {
      arr = routeData.filter(item=> item.id === 'JavaEE')
    }
    if (e.target.dataset.id == '前端开发') {
      arr = routeData.filter(item=> item.id === '前端开发')
    }
    if (e.target.dataset.id == '大数据') {
      arr = routeData.filter(item=> item.id === '大数据')
    }
    if (e.target.dataset.id == '人工智能') {
      arr = routeData.filter(item=> item.id === '人工智能')
    }
    if (e.target.dataset.id == 'UI设计') {
      arr = routeData.filter(item=> item.id === 'UI设计')
    }
    if (e.target.dataset.id == '软件测试') {
      arr = routeData.filter(item=> item.id === '软件测试')
    }
    if (e.target.dataset.id == '产品经理') {
      arr = routeData.filter(item=> item.id === '产品经理')
    }
    if (e.target.dataset.id == '新媒体') {
      arr = routeData.filter(item=> item.id === '新媒体')
    }
    routeDataRender(arr)
  }
})
document.querySelector('.navbars-item [data-id="JavaEE"]').click()

const hotTools = [
  {
    src: "./images/tools1.jpg",
    title: "JDK",
    content:
      "JDK是针对Java开发人员的软件开发工具包。自从Java推出以来，JDK已经成为使用最广泛的Java SDK。",
    downLink: "#",
    Classification: "JavaEE",
    download: "3000"
  },
  {
    src: "./images/tools2.jpg",
    title: "MySQL",
    content:
      "数据库是按照数据结构来组织、存储和管理数据的仓库。每个数据库都有一个或多个不同的API用于创建、访问、管理、搜索和复制所保存的数据。",
    downLink: "#",
    Classification: "JavaEE",
    download: "3400"
  },
  {
    src: "./images/tools3.jpg",
    title: "MyEclipse",
    content:
      "MyEclipse企业级工作平台(MyEclipse Enterprise Workbench,简称MyEnlipse)是对Eclipse IDE的扩展，利用它我们可以在数据库和Java EE的开发、发布以及应用程序服务器的整合方面极大地提高工作效率。",
    downLink: "#",
    Classification: "JavaEE",
    download: "3050"
  }
]

function toolRender() {
  let str = ''
  hotTools.forEach(item => {
    const { src, title, content,Classification,download} = item
    return str +=` 
      <div class="tools mt-4">
        <div class="imgs">
          <img src=${src} alt="">
        </div>
        <div class="about ms-3">
          <h5>${title}</h5>
          <p>${content}</p>
          <button type="button" class="btn btn-warning">立即下载</button>
          <button ype="button" class="btn btn-light btn-sm mx-1 text-secondary">${Classification}</button>
          <button ype="button" class="btn btn-light btn-sm text-secondary">${download}人已下载</button>
        </div>
      </div>
      `
  })
  document.querySelector('.containTools').innerHTML= str
}
toolRender()