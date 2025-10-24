// auth.js - 认证页面公共脚本（密码切换、提交防重复、密码匹配、密码强度指示器）
document.addEventListener('DOMContentLoaded', function () {
  // 密码显示/隐藏切换
  function initPasswordToggle(toggleId, inputId) {
    const toggleBtn = document.getElementById(toggleId);
    const passwordInput = document.getElementById(inputId);
    if (!toggleBtn || !passwordInput) return;

    toggleBtn.addEventListener('click', function (e) {
      e.preventDefault();

      // 切换密码可见性
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);

      // 切换图标
      const icon = this.querySelector('i');
      if (icon) {
        icon.classList.toggle('bi-eye');
        icon.classList.toggle('bi-eye-slash');
      }

      // 添加微小的反馈动画
      this.classList.add('active');
      setTimeout(() => this.classList.remove('active'), 200);
    });
  }

  // 表单提交状态管理
  function initFormSubmission(formSelector, buttonId, loadingText) {
    const form = document.querySelector(formSelector);
    const submitBtn = document.getElementById(buttonId);
    if (!form || !submitBtn) return;

    form.addEventListener('submit', function (e) {
      // 表单验证
      if (!form.checkValidity()) {
        e.preventDefault();
        form.reportValidity();
        return;
      }

      // 显示加载状态
      submitBtn.disabled = true;
      const textElement = submitBtn.querySelector('span[id$="-text"]');
      const spinnerElement = submitBtn.querySelector('span[id$="-spinner"]');

      if (textElement && spinnerElement) {
        textElement.textContent = loadingText || '处理中...';
        spinnerElement.style.display = 'inline-block';
      }
    });
  }

  // 密码匹配检查
  function initPasswordMatch(passwordId, confirmPasswordId, errorSelector, successSelector) {
    const passwordInput = document.getElementById(passwordId);
    const confirmPasswordInput = document.getElementById(confirmPasswordId);
    const errorElement = document.getElementById(errorSelector);
    const successElement = document.getElementById(successSelector);

    if (!passwordInput || !confirmPasswordInput || !errorElement || !successElement) return;

    function checkMatch() {
      if (!confirmPasswordInput.value) {
        // 确认密码为空时隐藏提示
        errorElement.style.display = 'none';
        successElement.style.display = 'none';
        return;
      }

      if (passwordInput.value !== confirmPasswordInput.value) {
        // 密码不匹配
        errorElement.style.display = 'block';
        successElement.style.display = 'none';
        confirmPasswordInput.setCustomValidity('密码不一致');
      } else {
        // 密码匹配
        errorElement.style.display = 'none';
        successElement.style.display = 'block';
        confirmPasswordInput.setCustomValidity('');
      }
    }

    // 监听输入事件
    confirmPasswordInput.addEventListener('input', checkMatch);
    passwordInput.addEventListener('input', checkMatch);
  }

  // 高级密码强度检测
  function initPasswordStrength(passwordId) {
    const passwordInput = document.getElementById(passwordId);
    if (!passwordInput) return;

    const strengthTexts = ['非常弱', '弱', '中等', '强', '非常强'];
    const strengthColors = ['', 'weak', 'medium', 'medium', 'strong'];

    function updateStrengthIndicator() {
      const password = passwordInput.value;
      const strengthText = document.getElementById('password-strength-text');
      const bar1 = document.getElementById('strength-bar-1');
      const bar2 = document.getElementById('strength-bar-2');
      const bar3 = document.getElementById('strength-bar-3');
      const bar4 = document.getElementById('strength-bar-4');

      if (!strengthText || !bar1 || !bar2 || !bar3 || !bar4) return;

      // 重置所有条
      [bar1, bar2, bar3, bar4].forEach(bar => {
        bar.className = 'strength-bar';
      });

      if (!password) {
        strengthText.textContent = '密码强度';
        return;
      }

      // 计算密码强度分数
      let score = 0;

      // 长度检查
      if (password.length >= 6) score += 0.5;
      if (password.length >= 8) score += 0.5;
      if (password.length >= 12) score += 0.5;
      if (password.length >= 16) score += 0.5;

      // 字符类型检查
      if (/[a-z]/.test(password)) score += 1;
      if (/[A-Z]/.test(password)) score += 1;
      if (/[0-9]/.test(password)) score += 1;
      if (/[^A-Za-z0-9]/.test(password)) score += 1;

      // 复杂度检查
      if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 0.5;
      if (/[0-9]/.test(password) && /[^A-Za-z0-9]/.test(password)) score += 0.5;

      // 计算最终等级（1-5）
      const level = Math.min(4, Math.max(0, Math.floor(score)));

      // 更新UI
      strengthText.textContent = strengthTexts[level];

      // 更新强度条
      for (let i = 0; i <= level; i++) {
        if (i === 0) bar1.className = `strength-bar ${strengthColors[level]}`;
        if (i === 1) bar2.className = `strength-bar ${strengthColors[level]}`;
        if (i === 2) bar3.className = `strength-bar ${strengthColors[level]}`;
        if (i === 3) bar4.className = `strength-bar ${strengthColors[level]}`;
      }
    }

    // 监听输入事件
    passwordInput.addEventListener('input', updateStrengthIndicator);
  }

  // 添加表单元素动画效果
  function initFormAnimations() {
    const formInputs = document.querySelectorAll('.form-floating input');

    formInputs.forEach(input => {
      // 输入框获得焦点时的动画
      input.addEventListener('focus', function () {
        this.parentElement.classList.add('focused');
      });

      // 输入框失去焦点时的动画
      input.addEventListener('blur', function () {
        this.parentElement.classList.remove('focused');
      });

      // 页面加载时检查已填充的输入框
      if (input.value) {
        input.setAttribute('placeholder', '');
      }
    });
  }

  // 初始化所有功能
  initPasswordToggle('togglePassword', 'password');
  initPasswordToggle('toggleConfirmPassword', 'confirmPassword');
  initFormSubmission('#login-form', 'login-submit', '登录中...');
  initFormSubmission('#register-form', 'register-submit', '创建中...');
  initFormSubmission('#unlock-form', 'unlock-submit', '验证中...');
  initPasswordMatch('password', 'confirmPassword', 'password-match-error', 'password-match-success');
  initPasswordStrength('password');
  initFormAnimations();
});
