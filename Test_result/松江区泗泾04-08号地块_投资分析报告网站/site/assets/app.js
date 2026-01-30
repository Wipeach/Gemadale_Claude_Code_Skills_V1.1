/**
 * 金地集团投资部 - 交互脚本
 * 功能：scrollspy、smooth scroll、lightbox、mobile nav、accordions
 */

(function() {
  'use strict';

  // ===== 工具函数 =====
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => document.querySelectorAll(selector);

  // ===== 全局状态 =====
  const state = {
    currentPart: 'home',
    currentSection: null,
    isMobileMenuOpen: false,
    isLightboxOpen: false
  };

  // ===== 初始化 =====
  function init() {
    initScrollSpy();
    initSmoothScroll();
    initLightbox();
    initMobileNav();
    initAccordions();
    initTabs();
  }

  // ===== ScrollSpy 双高亮 =====
  function initScrollSpy() {
    const parts = document.querySelectorAll('.part');
    const navTabs = document.querySelectorAll('.nav-tab');
    const sidebarLinks = document.querySelectorAll('.sidebar-link');

    if (!parts.length) return;

    // 创建观察者
    const observerOptions = {
      root: null,
      rootMargin: '-100px 0px -70% 0px',
      threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const partId = entry.target.id;
          if (partId && partId !== state.currentPart) {
            state.currentPart = partId;
            updateActiveStates();
          }
        }
      });
    }, observerOptions);

    // 观察所有 Part
    parts.forEach(part => observer.observe(part));

    // 监听 section 级别滚动
    window.addEventListener('scroll', debounce(updateActiveSection, 100));
  }

  function updateActiveStates() {
    // 更新顶部导航
    $$('.nav-tab').forEach(tab => {
      const targetPart = tab.getAttribute('data-part');
      if (targetPart === state.currentPart) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    // 更新侧边导航
    $$('.sidebar-link').forEach(link => {
      const targetSection = link.getAttribute('data-section');
      if (targetSection === state.currentSection) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  function updateActiveSection() {
    const sections = document.querySelectorAll('.section');
    let currentSection = null;
    let minDistance = Infinity;

    sections.forEach(section => {
      const rect = section.getBoundingClientRect();
      const distance = Math.abs(rect.top);

      if (distance < minDistance && rect.top <= 200) {
        minDistance = distance;
        currentSection = section.id;
      }
    });

    if (currentSection && currentSection !== state.currentSection) {
      state.currentSection = currentSection;
      updateActiveStates();
    }
  }

  // ===== Smooth Scroll 平滑滚动 =====
  function initSmoothScroll() {
    // 顶部导航点击
    $$('.nav-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        e.preventDefault();
        const targetPart = tab.getAttribute('data-part');
        const targetElement = document.getElementById(targetPart);

        if (targetElement) {
          const offset = 80; // header height + padding
          const targetPosition = targetElement.offsetTop - offset;
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });
        }
      });
    });

    // 侧边导航点击
    $$('.sidebar-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetSection = link.getAttribute('data-section');
        const targetElement = document.getElementById(targetSection);

        if (targetElement) {
          const offset = 100;
          const targetPosition = targetElement.offsetTop - offset;
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });

          // 移动端点击后关闭侧边栏
          if (window.innerWidth <= 1024) {
            closeMobileDrawer();
          }
        }
      });
    });
  }

  // ===== Lightbox 图片弹窗 =====
  function initLightbox() {
    const lightbox = $('#lightbox');
    const lightboxImg = $('#lightbox-img');
    const lightboxClose = $('#lightbox-close');
    const figures = document.querySelectorAll('.figure');

    if (!lightbox) return;

    // 点击图片打开
    figures.forEach((figure, index) => {
      const img = figure.querySelector('img');
      if (!img) return;

      figure.addEventListener('click', () => {
        const src = img.getAttribute('src');
        const caption = figure.querySelector('.figure-caption');

        lightboxImg.setAttribute('src', src);

        // 添加图片说明
        let captionText = '';
        if (caption) {
          const captionDiv = document.createElement('div');
          captionDiv.style.cssText = 'position: absolute; bottom: 20px; left: 0; right: 0; text-align: center; color: white; padding: 10px; background: rgba(0,0,0,0.5);';
          captionDiv.textContent = caption.textContent;
          lightbox.appendChild(captionDiv);
        }

        lightbox.classList.add('active');
        state.isLightboxOpen = true;
        document.body.style.overflow = 'hidden';

        // 保存当前图片索引用于切换
        lightbox.setAttribute('data-current-index', index);
      });
    });

    // 关闭按钮
    if (lightboxClose) {
      lightboxClose.addEventListener('click', closeLightbox);
    }

    // 点击背景关闭
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) {
        closeLightbox();
      }
    });

    // ESC 键关闭
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && state.isLightboxOpen) {
        closeLightbox();
      }

      // 左右箭头切换
      if (state.isLightboxOpen) {
        const currentIndex = parseInt(lightbox.getAttribute('data-current-index'));
        const allFigures = Array.from(document.querySelectorAll('.figure'));

        if (e.key === 'ArrowLeft' && currentIndex > 0) {
          showImageAtIndex(currentIndex - 1);
        } else if (e.key === 'ArrowRight' && currentIndex < allFigures.length - 1) {
          showImageAtIndex(currentIndex + 1);
        }
      }
    });
  }

  function showImageAtIndex(index) {
    const figures = Array.from(document.querySelectorAll('.figure'));
    const lightbox = $('#lightbox');
    const lightboxImg = $('#lightbox-img');

    if (index >= 0 && index < figures.length) {
      const figure = figures[index];
      const img = figure.querySelector('img');

      if (img) {
        lightboxImg.setAttribute('src', img.getAttribute('src'));
        lightbox.setAttribute('data-current-index', index);

        // 更新说明
        const existingCaption = lightbox.querySelector('div[style*="position: absolute"]');
        if (existingCaption) {
          existingCaption.remove();
        }

        const caption = figure.querySelector('.figure-caption');
        if (caption) {
          const captionDiv = document.createElement('div');
          captionDiv.style.cssText = 'position: absolute; bottom: 20px; left: 0; right: 0; text-align: center; color: white; padding: 10px; background: rgba(0,0,0,0.5);';
          captionDiv.textContent = caption.textContent;
          lightbox.appendChild(captionDiv);
        }
      }
    }
  }

  function closeLightbox() {
    const lightbox = $('#lightbox');
    if (lightbox) {
      lightbox.classList.remove('active');
      state.isLightboxOpen = false;
      document.body.style.overflow = '';

      // 移除说明
      const existingCaption = lightbox.querySelector('div[style*="position: absolute"]');
      if (existingCaption) {
        existingCaption.remove();
      }
    }
  }

  // ===== Mobile Nav 移动端导航 =====
  function initMobileNav() {
    const menuBtn = $('.mobile-menu-btn');
    const drawer = $('.mobile-drawer');
    const backdrop = $('.mobile-drawer-backdrop');

    if (!menuBtn || !drawer) return;

    menuBtn.addEventListener('click', toggleMobileDrawer);
    if (backdrop) {
      backdrop.addEventListener('click', closeMobileDrawer);
    }
  }

  function toggleMobileDrawer() {
    const drawer = $('.mobile-drawer');
    const backdrop = $('.mobile-drawer-backdrop');
    const sidebar = $('.sidebar');

    if (state.isMobileMenuOpen) {
      closeMobileDrawer();
    } else {
      state.isMobileMenuOpen = true;
      if (drawer) drawer.classList.add('active');
      if (backdrop) backdrop.classList.add('active');
      if (sidebar) sidebar.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeMobileDrawer() {
    state.isMobileMenuOpen = false;
    const drawer = $('.mobile-drawer');
    const backdrop = $('.mobile-drawer-backdrop');
    const sidebar = $('.sidebar');

    if (drawer) drawer.classList.remove('active');
    if (backdrop) backdrop.classList.remove('active');
    if (sidebar) sidebar.classList.remove('active');
    document.body.style.overflow = '';
  }

  // ===== Accordion 折叠面板 =====
  function initAccordions() {
    $$('.accordion').forEach(accordion => {
      const header = accordion.querySelector('.accordion-header');
      if (!header) return;

      header.addEventListener('click', () => {
        const isActive = accordion.classList.contains('active');

        // 关闭同一组中的其他 accordion
        const parent = accordion.parentElement;
        const siblings = parent.querySelectorAll('.accordion');
        siblings.forEach(sibling => {
          if (sibling !== accordion) {
            sibling.classList.remove('active');
          }
        });

        // 切换当前状态
        if (isActive) {
          accordion.classList.remove('active');
        } else {
          accordion.classList.add('active');
        }
      });
    });
  }

  // ===== Tabs 标签页切换 =====
  function initTabs() {
    $$('.tabs').forEach(tabContainer => {
      const tabButtons = tabContainer.querySelectorAll('.tab-button');
      const tabPanels = tabContainer.querySelectorAll('.tab-panel');

      tabButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
          // 移除所有激活状态
          tabButtons.forEach(btn => btn.classList.remove('active'));
          tabPanels.forEach(panel => panel.classList.remove('active'));

          // 激活当前
          button.classList.add('active');
          const targetPanel = tabPanels[index];
          if (targetPanel) {
            targetPanel.classList.add('active');
          }
        });
      });
    });
  }

  // ===== 防抖函数 =====
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // ===== 节流函数 =====
  function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  // ===== DOMContentLoaded 启动 =====
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
