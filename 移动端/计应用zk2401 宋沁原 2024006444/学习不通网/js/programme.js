const routeData = [
  {
    id: '新媒体',
    contain: [
      {
        title: '新媒体运营',
        content: '内容策划与编辑,短视频运营技巧,社交媒体投放,数据分析与热点追踪,平台规则与品牌打造'
      },
      {
        title: '项目管理',
        content: '敏捷开发Scrum,Jira任务管理,版本发布计划制定,团队协作技巧,风险控制'
      },
      {
        title: '用户增长',
        content: 'A/B测试,用户画像构建,留存分析,裂变活动设计,推广转化率提升'
      },
      {
        title: '内容创作',
        content: '文案撰写技巧,热点内容挖掘,视觉内容设计,多平台适配,创作流程管理'
      },
      {
        title: '数据分析',
        content: 'Excel透视表,用户行为分析,数据可视化,数据清洗,内容热度分析'
      },
      {
        title: '品牌管理',
        content: '品牌定位,传播策略,口碑维护,KOL合作,危机公关处理'
      }
    ]
  },
  {
    id: '前端开发',
    contain: [
      {
        title: 'HTML/CSS',
        content: '语义化标签,响应式设计,FLEX布局,媒体查询,网页兼容性'
      },
      {
        title: 'JavaScript',
        content: 'DOM操作,事件机制,异步编程,模块化开发,ES6新特性'
      },
      {
        title: '前端框架',
        content: 'React组件化,Vue响应式,生命周期管理,状态管理,双向绑定'
      },
      {
        title: '构建工具',
        content: 'Webpack配置,Vite打包,Gulp任务流,NPM包管理,代码压缩优化'
      },
      {
        title: '性能优化',
        content: '懒加载,资源压缩,代码分割,缓存策略,页面渲染优化'
      },
      {
        title: '跨端开发',
        content: '小程序开发,React Native,Flutter基础,H5与APP混合开发,适配方案'
      }
    ]
  },
  {
    id: '后端开发',
    contain: [
      {
        title: '编程语言',
        content: 'Java基础,Python语法,Node.js入门,C#使用,Go语言结构'
      },
      {
        title: 'Web服务',
        content: 'HTTP协议,RESTful接口设计,Session与Token,状态码解析,CORS跨域'
      },
      {
        title: '数据库',
        content: 'MySQL语句优化,MongoDB使用,数据建模,索引设计,主从复制'
      },
      {
        title: '接口开发',
        content: 'API路由管理,参数校验,数据响应格式,文档编写,异常处理'
      },
      {
        title: '安全加固',
        content: 'JWT身份认证,SQL注入防护,XSS攻击防护,密码加密存储,访问权限控制'
      },
      {
        title: '部署运维',
        content: 'Docker容器化,Nginx配置,CI/CD流程,Linux基本操作,日志监控'
      }
    ]
  },
  {
    id: '人工智能',
    contain: [
      {
        title: '基础算法',
        content: '线性回归,决策树,K近邻,朴素贝叶斯,支持向量机'
      },
      {
        title: '深度学习',
        content: '神经网络,卷积网络CNN,循环网络RNN,优化算法,损失函数'
      },
      {
        title: '数据处理',
        content: '特征提取,数据归一化,缺失值处理,数据增强,降维技术'
      },
      {
        title: '自然语言处理',
        content: '分词技术,词向量,情感分析,BERT模型,命名实体识别'
      },
      {
        title: '计算机视觉',
        content: '图像分类,目标检测,图像分割,姿态识别,图像增强'
      },
      {
        title: 'AI工程化',
        content: '模型部署,TensorFlow使用,PyTorch框架,API封装,推理优化'
      }
    ]
  },
  {
    id: '大数据',
    contain: [
      {
        title: '数据采集',
        content: '爬虫技术,日志收集,实时流处理,数据清洗,数据格式转换'
      },
      {
        title: '数据存储',
        content: 'HDFS架构,Hive数据仓库,HBase分布式,Parquet文件格式,数据湖'
      },
      {
        title: '数据处理',
        content: 'MapReduce基础,Spark计算框架,Flume数据传输,Kafka消息队列,批处理与流处理'
      },
      {
        title: '数据可视化',
        content: 'Tableau分析,Echarts图表,BI报表工具,D3.js绘图,交互式仪表盘'
      },
      {
        title: '数据建模',
        content: '数据聚类,关联规则,回归分析,预测建模,时间序列'
      },
      {
        title: '数据安全',
        content: '隐私保护,访问控制,脱敏处理,数据审计,权限管理'
      }
    ]
  },
  {
    id: '网络安全',
    contain: [
      {
        title: '信息安全基础',
        content: '加密算法,身份验证,访问控制,安全策略,网络协议'
      },
      {
        title: '漏洞分析',
        content: 'SQL注入,XSS攻击,CSRF漏洞,文件上传漏洞,缓冲区溢出'
      },
      {
        title: '攻防技术',
        content: '渗透测试,端口扫描,漏洞利用,社会工程学,反制技术'
      },
      {
        title: '网络防护',
        content: '防火墙配置,入侵检测,蜜罐技术,VPN架设,IP封禁'
      },
      {
        title: '安全合规',
        content: '等保2.0,GDPR法规,审计记录,日志留存,风险评估'
      },
      {
        title: '应急响应',
        content: '事件调查,日志分析,溯源技术,修复流程,恢复机制'
      }
    ]
  },
  {
    id: '软件工程',
    contain: [
      {
        title: '开发流程',
        content: '需求分析,系统设计,编码实现,测试验证,项目交付'
      },
      {
        title: '项目管理',
        content: '敏捷开发,版本控制,迭代计划,工时评估,团队沟通'
      },
      {
        title: '软件测试',
        content: '单元测试,集成测试,自动化测试,性能测试,测试报告'
      },
      {
        title: '文档管理',
        content: '接口文档,需求说明书,用户手册,代码注释,维护日志'
      },
      {
        title: '开发工具',
        content: 'Git版本管理,IDE使用,Jenkins持续集成,Sonar代码扫描,自动化构建'
      },
      {
        title: '架构设计',
        content: 'MVC模式,微服务架构,中间件使用,模块解耦,高并发设计'
      }
    ]
  },
  {
    id: '物联网',
    contain: [
      {
        title: '嵌入式开发',
        content: '单片机编程,传感器接入,C语言基础,串口通信,驱动开发'
      },
      {
        title: '无线通信',
        content: '蓝牙协议,Zigbee通信,LoRa网络,NFC近场,WiFi模块'
      },
      {
        title: '智能硬件',
        content: '开发板选型,原型设计,电源管理,模块调试,接口规范'
      },
      {
        title: '平台接入',
        content: 'MQTT协议,云平台对接,数据上传,远程控制,边缘计算'
      },
      {
        title: '设备管理',
        content: '设备绑定,远程升级,状态监控,日志收集,命令下发'
      },
      {
        title: '安全体系',
        content: '身份认证,通信加密,固件加签,物理防护,OTA升级验证'
      }
    ]
  }
]


function routeDataRender() {
  let str = ''
  routeData.forEach(item => {
    const { id, contain, contain: [{ title }] } = item
    let data = ''
    contain.forEach((item, index) => {
      const { content } = item
      let strs = ''
      content.split(',').forEach(ele => {
        return strs += `
      <a href="#"><span class="list-contain">${ele}</span></a>
      `
      })
      return data += `
        <div class="box-list col mt-4">
          <div class="left">
            <h5 class="list-title">${title}</h5>
            ${strs}
          </div>
          <div class="right">
            <div class="num">${index + 1}</div>
          </div>
        </div>
      `
    })
    str += `
    <div class="navbars-contain mt-5 container-fluid">
        <h4>${id}</h4>
        <div class=" row g-2 row-cols-1 row-cols-md-2 row-cols-lg-3 renderList pb-5">
          ${data}
        </div>
      </div>
  `
  })
  document.querySelector('.mc').innerHTML = str
}

routeDataRender()