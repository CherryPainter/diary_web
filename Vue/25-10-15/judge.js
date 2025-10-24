// 页面元素引用（用于填充与显示/隐藏控制）
const select = document.querySelector('.select');
const result = document.querySelector('.result');

const codeInput = document.getElementById('code');
const searchBtn = document.querySelector('.search');
const codeID = document.querySelector('#result-code');
const gender = document.querySelector('#result-gender');
const birthday = document.querySelector('#result-birthdate');
const nativePlace = document.querySelector('#result-region');
const ages = document.querySelector('#result-age');

// 点击查询按钮处理：做基础合理性校验（年/月/日边界），再显示结果区并处理数据
searchBtn.addEventListener('click', () => {
  const code = codeInput.value;
  if (judgeData(code)) {
    alert('请输入正确的身份证号码');
    codeInput.value = '';
    codeInput.focus();
  }
  else {
    select.style.display = 'none';
    result.style.display = 'block';
    getcodeInfo(code);
  }
});

/**
 * 从身份证号提取信息并在页面显示
 * 输入: code - 18位身份证号码字符串
 * 输出: 在页面上显示身份证号、性别、出生日期、籍贯（通过 data.json 映射）、年龄
 * 限制/假设: data.json 在同目录，包含 {code, name} 的行政区映射；年龄按365天近似计算
 */
function getcodeInfo(code) {
  // 省、市、区编码：补齐到6位以匹配 data.json 中的行政编码格式
  const province = code.slice(0, 2).padEnd(6, '0');
  const city = code.slice(0, 4).padEnd(6, '0');
  const area = code.slice(0, 6);

  // 填充基本字段
  codeID.textContent = code;
  gender.textContent = code.slice(16, 17) % 2 === 0 ? '女' : '男';
  birthday.textContent = code.slice(6, 10) + '年' + code.slice(10, 12) + '月' + code.slice(12, 14) + '日';

  // 加载本地 data.json，然后匹配省/市/区名称
  fetch('./data.json').then(res => res.json()).then(data => {
    let Native_place = {
      province,
      city,
      area
    };
    // 使用标志位保证首次匹配时写入，避免后续覆盖为 ''（实现与原逻辑保持一致）
    let p = true, c = true, a = true;
    data.forEach(ele => {
      const { code, name } = ele;
      if (p) {
        if (code === province) {
          Native_place.province = name;
          p = false;
        } else {
          Native_place.province = '';
        }
      }
      if (c) {
        if (code === city) {
          Native_place.city = name;
          c = false;
        } else {
          Native_place.city = '';
        }
      }
      if (a) {
        if (code === area) {
          Native_place.area = name;
          a = false;
        } else {
          Native_place.area = '';
        }
      }
    });

    // 直辖市等场景：省与市名称相同时合并显示，避免重复
    if (Native_place.province === Native_place.city) {
      nativePlace.textContent = Native_place.province + Native_place.area;
    }
    else {
      nativePlace.textContent = Native_place.province + Native_place.city + Native_place.area;
    }

  }).catch(() => {
    alert('地区数据加载失败，请检查 data.json 是否存在');
  });
  // 计算年龄（近似，按365天每年计算）
  const date = new Date();
  let age = date.getTime() - new Date(birthday.textContent.replace('年', '-').replace('月', '-').replace('日', '')).getTime();
  age = Math.floor(age / (1000 * 60 * 60 * 24 * 365));
  ages.textContent = age + '岁';
}

function judgeData(code) {
  // 判定函数：返回 true 表示身份证中出生日期相关字段不合法
  // 1) 年份边界检查（1900年-当前年）
  const year = code.slice(6, 10);
  const currentYear = new Date().getFullYear();
  if (year < 1900 || year > currentYear) {
    console.log('yerror'); // 年份错误
    return true; // 标记数据非法
  }
  // 2) 月份边界检查（1-12）
  const month = code.slice(10, 12);
  if (month < 1 || month > 12) {
    console.log('merror'); // 月份错误
    return true;
  }
  // 3) 日数边界检查（1-当月最大天数）
  const day = code.slice(12, 14);

  if (day < 1 || day > getDaysInMonth(year, month)) {
    console.log('derror'); // 日份错误
    return true;
  }
}

function getDaysInMonth(year, month) {
  if (year % 4 === 0 && year % 100 !== 0 || year % 400 === 0) {
    // 闰年
    return [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1];
  } else {
    return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1];
  }
}