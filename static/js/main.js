// ===========================
// IDRISI MART - ENHANCED MAIN.JS
// v4.0 - Theme Toggle + Country Selector + Badges
// ===========================

;(function () {
  'use strict'

  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init)
  } else {
    init()
  }

  function init() {
    console.log('🚀 Idrisi Mart Initializing...')

    // Ensure visibility
    document.body.style.opacity = '1'
    document.body.style.visibility = 'visible'

    // Core Systems
    const gsapReady = initGSAP()
    initThemeToggle()
    initMobileMenu()
    initEnhancedCountrySelector()
    initEnhancedBadges()
    initLanguageSwitcher()
    initSmoothScroll()
    initBackToTop()
    initMobileMenu()
    initCounters()
    initYojadHeader()
    initCategoriesSwiper()
    if (gsapReady) initAnimations()
    initPageLoad()
    initPreloader()

    console.log('%c✅ All systems ready!', 'color:#4B315E;font-weight:bold;')
  }

  // ===========================
  // UTILITIES
  // ===========================
  function getCookie(name) {
    return document.cookie.split(';').reduce((acc, cookie) => {
      const [key, val] = cookie.trim().split('=')
      return key === name ? decodeURIComponent(val) : acc
    }, null)
  }

  window.debounce = function (fn, wait) {
    let timeout
    return (...args) => {
      clearTimeout(timeout)
      timeout = setTimeout(() => fn(...args), wait)
    }
  }

  window.showNotification = function (message, type = 'success') {
    const colors = {
      success: 'linear-gradient(135deg, #4B315E 0%, #6B4C7A 100%)',
      error: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
      info: 'linear-gradient(135deg, #3498db 0%, #2980b9 100%)',
      warning: 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)',
    }
    const icons = { success: '✓', error: '✗', info: 'ℹ', warning: '⚠' }

    const box = document.createElement('div')
    box.className = 'custom-notification'
    box.style.cssText = `
            position: fixed; top: 90px; right: 20px; z-index: 9999;
            background: ${colors[type]}; color: white; padding: 14px 22px;
            border-radius: 12px; font-weight: 600; box-shadow: 0 6px 20px rgba(0,0,0,0.2);
            display: flex; align-items: center; gap: 8px; max-width: 340px;
        `
    box.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`
    document.body.appendChild(box)

    if (window.gsap) {
      gsap.from(box, { x: 200, opacity: 0, duration: 0.4, ease: 'back.out(1.7)' })
      setTimeout(() => {
        gsap.to(box, { x: 200, opacity: 0, duration: 0.3, onComplete: () => box.remove() })
      }, 3000)
    } else {
      setTimeout(() => box.remove(), 3000)
    }
  }

  // ===========================
  // GSAP INIT
  // ===========================
  function initGSAP() {
    if (window.gsap && window.ScrollTrigger) {
      gsap.registerPlugin(ScrollTrigger)
      console.log('✓ GSAP + ScrollTrigger ready')
      return true
    }
    console.warn('⚠️ GSAP not found. Animations disabled.')
    return false
  }

  // ===========================
  // ENHANCED THEME TOGGLE
  // ===========================
  function initThemeToggle() {
    const html = document.documentElement
    html.setAttribute('data-theme', localStorage.getItem('theme') || 'light')

    // Select all toggle elements (desktop and mobile)
    const buttons = document.querySelectorAll('#themeToggle, .theme-switcher, #headerThemeToggle, #mobileThemeToggle')

    buttons.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        if (btn.tagName.toLowerCase() === 'a') e.preventDefault()

        const nextTheme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light'

        html.setAttribute('data-theme', nextTheme)
        localStorage.setItem('theme', nextTheme)

        // Animate icons with a single class toggle or direct style
        btn.querySelectorAll('.theme-icon-light, .theme-icon-dark').forEach(icon => {
          icon.style.transition = 'transform 0.4s ease'
          icon.style.transform = 'rotate(360deg)'
          setTimeout(() => icon.style.transform = 'rotate(0deg)', 400)
        });

        // Show notification
        const modeText = nextTheme === 'dark' ? 'الوضع الليلي' : 'الوضع النهاري'
        if (typeof showNotification === 'function') {
          showNotification(`تم التبديل إلى ${modeText}`, 'info')
        }
      })
    })

    if (buttons.length) console.log('✓ Enhanced theme toggle initialized for all buttons')
  }

  // ===========================
  // MOBILE MENU
  // ===========================
  function initMobileMenu() {
    const menu = {
      hamburger: document.getElementById('hamburgerBtn'),
      nav: document.getElementById('mobileNav'),
      closeBtn: document.getElementById('mobileNavClose'),
      backdrop: document.getElementById('mobileBackdrop'),

      init() {
        if (!this.hamburger || !this.nav || !this.backdrop) {
          console.warn('⚠️ Mobile menu elements not found. Skipping initialization.')
          return
        }

        this.hamburger.addEventListener('click', this.open.bind(this))
        this.closeBtn?.addEventListener('click', this.close.bind(this))
        this.backdrop.addEventListener('click', this.close.bind(this))

        this.nav.querySelectorAll('.mobile-nav-link').forEach((link) => {
          link.addEventListener('click', (e) => {
            if (!link.closest('.mobile-dropdown')) {
              const href = link.getAttribute('href')
              if (href && href !== '#') {
                this.close()
              }
            }
          })
        })

        console.log('✓ Mobile menu initialized (modular)')
      },

      open() {
        this.nav.classList.add('active')
        this.backdrop.classList.add('active')
        this.hamburger.classList.add('active')
        document.body.style.overflow = 'hidden'
      },

      close() {
        this.nav.classList.remove('active')
        this.backdrop.classList.remove('active')
        this.hamburger.classList.remove('active')
        document.body.style.overflow = ''
      },
    }

    menu.init()
  }
  // ===========================
  // STATS COUNTERS
  // ===========================
  function initCounters() {
    if (!window.gsap || !window.ScrollTrigger) {
      console.warn('⚠️ GSAP or ScrollTrigger not found. Counters disabled.')
      return
    }

    gsap.utils.toArray('.stat-number').forEach((counter) => {
      const target = +counter.dataset.target || 0

      // Animate from 0 → target
      gsap.fromTo(
        counter,
        { innerText: 0 },
        {
          innerText: target,
          duration: 2,
          ease: 'power1.out',
          snap: { innerText: 1 },
          scrollTrigger: {
            trigger: counter,
            start: 'top 90%', // start when counter is in viewport
          },
          onUpdate: function () {
            counter.innerText = Math.floor(counter.innerText)
          },
        }
      )
    })

    console.log('✓ Stats counters initialized')
  }

  // ===========================
  // ENHANCED COUNTRY SELECTOR
  // ===========================
  // ===========================
  // ENHANCED COUNTRY SELECTOR (FIXED)
  // ===========================
  function initEnhancedCountrySelector() {
    const countryFlags = {
      SA: '🇸🇦',
      AE: '🇦🇪',
      EG: '🇪🇬',
      KW: '🇰🇼',
      QA: '🇶🇦',
      BH: '🇧🇭',
      OM: '🇴🇲',
      JO: '🇯🇴',
    }

    const countryNames = {
      SA: 'السعودية',
      AE: 'الإمارات',
      EG: 'مصر',
      KW: 'الكويت',
      QA: 'قطر',
      BH: 'البحرين',
      OM: 'عُمان',
      JO: 'الأردن',
    }

    function updateUI(code) {
      // Update desktop dropdown current country
      const currentCountrySpan = document.querySelector('.current-country')
      if (currentCountrySpan) {
        currentCountrySpan.textContent = countryFlags[code] || '🌍'
        currentCountrySpan.setAttribute('data-country-code', code)
      }

      // Update mobile country display
      const flagLarge = document.querySelector('.country-flag-large')
      if (flagLarge) flagLarge.textContent = countryFlags[code] || '🌍'

      const nameLarge = document.querySelector('.country-name-large')
      if (nameLarge) nameLarge.textContent = countryNames[code] || code

      // Update active states for both desktop and mobile
      document.querySelectorAll('.country-item, .mobile-country-item').forEach((el) => {
        el.classList.remove('active')
        // Remove any existing check icons
        const checkIcon = el.querySelector('.country-check, .check-icon')
        if (checkIcon) checkIcon.remove()
      })

      // Add active class and check icon to the selected items
      const desktopItem = document.querySelector(`.country-item[data-country="${code}"]`)
      if (desktopItem) {
        desktopItem.classList.add('active')
        desktopItem.insertAdjacentHTML('beforeend', '<i class="fas fa-check country-check"></i>')
      }
      const mobileItem = document.querySelector(`.mobile-country-item[data-country="${code}"]`)
      if (mobileItem) {
        mobileItem.classList.add('active')
        mobileItem.insertAdjacentHTML('beforeend', '<i class="fas fa-check-circle check-icon"></i>')
      }
    }

    async function handleCountryChange(e) {
      e.preventDefault()
      const item = this
      const code = item.dataset.country

      // Prevent double-click
      if (item.classList.contains('loading')) return

      const originalContent = item.innerHTML
      item.classList.add('loading')
      item.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'

      try {
        const response = await fetch('/api/set-country/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: `country_code=${code}`,
        })

        const data = await response.json()

        if (data.success) {
          // Store in localStorage for persistence
          localStorage.setItem('selectedCountry', code)

          updateUI(code)

          showNotification(data.message || 'تم تغيير البلد بنجاح', 'success')

          // Close mobile dropdown if open
          const collapseEl = document.getElementById('mobileCountryList')
          if (collapseEl && window.bootstrap) {
            const collapse = bootstrap.Collapse.getInstance(collapseEl)
            if (collapse) collapse.hide()
          }

          // Reload page after short delay to update content
          setTimeout(() => window.location.reload(), 1200)
        } else {
          showNotification(data.message || 'حدث خطأ', 'error')
          item.classList.remove('loading')
          item.innerHTML = originalContent
        }
      } catch (error) {
        console.error('Country change error:', error)
        showNotification('فشل الاتصال بالخادم', 'error')
        item.classList.remove('loading')
        item.innerHTML = originalContent
      }
    }

    // Attach to all country items (desktop and mobile)
    document.querySelectorAll('.mobile-country-item, .country-item').forEach((item) => {
      item.addEventListener('click', handleCountryChange)
    })

    console.log('✓ Enhanced country selector initialized')
  }

  // ===========================
  // ENHANCED BADGES
  // ===========================
  function initEnhancedBadges() {
    // Animate badges on hover
    document.querySelectorAll('.icon-link').forEach((link) => {
      link.addEventListener('mouseenter', () => {
        const badge = link.querySelector('.enhanced-badge')
        if (badge && window.gsap) {
          gsap.to(badge, {
            scale: 1.2,
            rotation: 5,
            duration: 0.3,
            ease: 'back.out(2)',
          })
        }
      })

      link.addEventListener('mouseleave', () => {
        const badge = link.querySelector('.enhanced-badge')
        if (badge && window.gsap) {
          gsap.to(badge, {
            scale: 1,
            rotation: 0,
            duration: 0.3,
            ease: 'back.out(2)',
          })
        }
      })

      // Click handling
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href')
        if (!href || href === '#') {
          e.preventDefault()
          const badge = link.querySelector('.enhanced-badge')
          if (badge) {
            // Pulse animation
            badge.style.animation = 'none'
            setTimeout(() => {
              badge.style.animation = 'badgePulse 0.5s ease'
            }, 10)
          }

          const isCart = link.classList.contains('cart-link')
          const message = isCart ? 'فتح السلة' : 'فتح المفضلة'
          showNotification(message, 'info')
        }
      })
    })

    // Mobile badges
    document.querySelectorAll('.mobile-nav-link .mobile-badge').forEach((badge) => {
      const link = badge.closest('.mobile-nav-link')
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href')
        if (!href || href === '#') {
          e.preventDefault()
          badge.style.animation = 'none'
          setTimeout(() => {
            badge.style.animation = 'badgePulse 0.5s ease'
          }, 10)
        }
      })
    })

    console.log('✓ Enhanced badges initialized')
  }

  // ===========================
  // LANGUAGE SWITCHER
  // ===========================
  function initLanguageSwitcher() {
    document.querySelectorAll('[data-lang]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault()
        const lang = btn.dataset.lang
        const html = document.documentElement
        localStorage.setItem('language', lang)
        html.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr')
        html.setAttribute('lang', lang)
        const langName = lang === 'ar' ? 'العربية' : 'English'
        showNotification(`Language changed to ${langName}`, 'success')
      })
    })
    console.log('✓ Language switcher initialized')
  }

  // ===========================
  // NAVBAR EFFECTS
  // ===========================
  function initNavbarEffects() {
    const navbar = document.getElementById('mainNav')
    if (!navbar) return

    window.addEventListener(
      'scroll',
      debounce(() => {
        const current = window.scrollY
        navbar.style.boxShadow = current > 50 ? '0 6px 25px rgba(0,0,0,0.25)' : 'none'
        navbar.style.padding = current > 50 ? '0.6rem 0' : '1.2rem 0'

        // Add or remove scrolled class to handle logo swapping
        if (current > 50) {
          navbar.classList.add('scrolled')
        } else {
          navbar.classList.remove('scrolled')
        }

        // Keep navbar always visible - no hiding on scroll
        navbar.style.transform = 'translateY(0)'
      }, 10)
    )
    console.log('✓ Navbar effects initialized - sticky mode (always visible)')
  }

  // ===========================
  // SMOOTH SCROLL
  // ===========================
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', (e) => {
        const href = anchor.getAttribute('href')
        if (href === '#') return
        const target = document.querySelector(href)
        if (target) {
          e.preventDefault()
          window.scrollTo({ top: target.offsetTop - 80, behavior: 'smooth' })
        }
      })
    })
    console.log('✓ Smooth scroll initialized')
  }

  // ===========================
  // BACK TO TOP
  // ===========================
  function initBackToTop() {
    const btn = document.querySelector('.back-to-top')
    if (!btn) return

    window.addEventListener('scroll', () => {
      btn.classList.toggle('show', window.scrollY > 300)
    })
    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    })
    console.log('✓ Back to top initialized')
  }

  // ===========================
  // GSAP ANIMATIONS
  // ===========================

  // GSAP ANIMATIONS
  // ===========================
  function initAnimations() {
    if (!window.gsap || !window.ScrollTrigger) return

    // Hero animations
    if (document.querySelector('.hero-title')) {
      gsap.from('.hero-title', { y: 40, opacity: 0, duration: 0.8 })
      gsap.from('.hero-subtitle', { y: 20, opacity: 0, duration: 0.8, delay: 0.2 })
    }

    // Section titles
    gsap.utils.toArray('.section-title').forEach((title) => {
      gsap.from(title, {
        scrollTrigger: { trigger: title, start: 'top 85%' },
        y: 30,
        opacity: 0,
        duration: 0.8,
      })
    })

    // Badge entrance animation
    gsap.from('.enhanced-badge', {
      scale: 0,
      rotation: -180,
      duration: 0.6,
      delay: 0.5,
      stagger: 0.1,
      ease: 'back.out(2)',
    })

    // Initialize stats counters
    initCounters()

    console.log('✓ GSAP animations initialized (including counters)')
  }

  // ===========================
  // PAGE LOAD
  // ===========================
  function initPageLoad() {
    window.addEventListener('load', () => {
      document.body.style.opacity = '1'
      console.log('✓ Page fully loaded')
    })
  }

  // ===========================
  // YOJAD HEADER FUNCTIONALITY
  // ===========================
  function initYojadHeader() {
    const header = document.querySelector('.yojad-header')
    if (!header) return

    // Scroll behavior for header
    let lastScroll = 0
    window.addEventListener(
      'scroll',
      debounce(() => {
        const currentScroll = window.pageYOffset || document.documentElement.scrollTop
        if (currentScroll > 50) {
          header.classList.add('scrolled')
        } else {
          header.classList.remove('scrolled')
        }
        lastScroll = currentScroll <= 0 ? 0 : currentScroll
      }, 10)
    )

    console.log('✓ Yojad header initialized')
  }

  // ===========================
  // PRELOADER
  // ===========================
  function initPreloader() {
    const preloader = document.getElementById('preloader');
    if (!preloader) return;
    const startTime = Date.now();

    window.addEventListener('load', () => {
      const elapsedTime = Date.now() - startTime;
      // Ensure the loader is visible for at least 1000ms (1 second)
      const remainingTime = Math.max(0, 1000 - elapsedTime);

      setTimeout(() => {
        preloader.classList.add('loader-hidden');
      }, remainingTime);
    });

    console.log('✓ Preloader initialized');
  }

  // ===========================
  // CATEGORIES SWIPER
  // ===========================
  function initCategoriesSwiper() {
    const categoriesSwiper = document.querySelector('.categories-swiper')
    if (!categoriesSwiper) {
      console.log('⚠️ Categories Swiper: Element not found')
      return
    }

    try {
      new Swiper('.categories-swiper', {
        slidesPerView: 1,
        spaceBetween: 8,
        freeMode: true,
        loop: true,
        autoplay: {
          delay: 3000,
          disableOnInteraction: false,
          pauseOnMouseEnter: true,
        },
        navigation: {
          nextEl: '.categories-swiper-next',
          prevEl: '.categories-swiper-prev',
        },
        speed: 800,
        breakpoints: {
          320: {
            slidesPerView: 1,
            spaceBetween: 8,
          },
          768: {
            slidesPerView: 2,
            spaceBetween: 12,
          },
          1024: {
            slidesPerView: 3,
            spaceBetween: 15,
          },
          1200: {
            slidesPerView: 3,
            spaceBetween: 20,
          }
        }
      })
      console.log('✅ Categories Swiper: Initialized with navigation arrows')
    } catch (error) {
      console.error('❌ Categories Swiper: Error', error)
    }
  }

  // ===========================
  // SUBCATEGORIES FUNCTIONALITY
  // ===========================

  // Global variables for subcategories
  let subcategoriesTimeout
  let subcategoriesSwiper
  let isSubcategoriesVisible = false

  // Initialize subcategories swiper
  function initSubcategoriesSwiper() {
    try {
      if (subcategoriesSwiper) {
        subcategoriesSwiper.destroy(true, true)
      }

      subcategoriesSwiper = new Swiper('.subcategories-swiper', {
        slidesPerView: 1,
        spaceBetween: 12,
        freeMode: true,
        navigation: {
          nextEl: '.subcategories-swiper .swiper-button-next',
          prevEl: '.subcategories-swiper .swiper-button-prev',
        },
        speed: 400,
        breakpoints: {
          320: {
            slidesPerView: 1,
            spaceBetween: 8,
          },
          480: {
            slidesPerView: 2,
            spaceBetween: 10,
          },
          768: {
            slidesPerView: 2,
            spaceBetween: 12,
          },
          1024: {
            slidesPerView: 3,
            spaceBetween: 15,
          },
          1200: {
            slidesPerView: 3,
            spaceBetween: 20,
          }
        }
      })
      console.log('✅ Subcategories Swiper: Initialized')
    } catch (error) {
      console.error('❌ Subcategories Swiper: Error', error)
    }
  }

  // Show subcategories for a given category
  window.showSubcategories = function(categoryId) {
    if (subcategoriesTimeout) {
      clearTimeout(subcategoriesTimeout)
    }

    const dropdown = document.getElementById('subcategoriesDropdown')
    if (!dropdown) return

    // Show loading state
    const subcategoriesList = document.getElementById('subcategoriesList')
    const parentCategoryName = document.getElementById('parentCategoryName')
    const viewAllLink = document.getElementById('viewAllSubcategories')

    if (subcategoriesList) {
      subcategoriesList.innerHTML = '<div class="loading-subcategories"><i class="fas fa-spinner fa-spin"></i> جارٍ التحميل...</div>'
    }

    // Show dropdown immediately
    dropdown.style.display = 'block'
    setTimeout(() => {
      dropdown.classList.add('show')
      isSubcategoriesVisible = true
    }, 10)

    // Fetch subcategories
    fetch(`/ajax/subcategories/${categoryId}/`)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          throw new Error(data.error)
        }

        // Update parent category name
        if (parentCategoryName && data.parent_category) {
          parentCategoryName.textContent = data.parent_category.name_ar || data.parent_category.name
        }

        // Update view all link
        if (viewAllLink && data.parent_category) {
          viewAllLink.href = `/category/${data.parent_category.slug}/`
        }

        // Populate subcategories
        if (subcategoriesList && data.subcategories) {
          if (data.subcategories.length === 0) {
            subcategoriesList.innerHTML = '<div class="no-subcategories">لا توجد فئات فرعية</div>'
          } else {
            subcategoriesList.innerHTML = data.subcategories.map(subcat => `
              <div class="swiper-slide">
                <a href="${subcat.url}" class="subcategory-item">
                  <div class="subcategory-icon">
                    ${subcat.icon ? `<i class="${subcat.icon}"></i>` : '<i class="fas fa-folder"></i>'}
                  </div>
                  <span class="subcategory-name">${subcat.name_ar || subcat.name}</span>
                  ${subcat.has_children ? '<i class="fas fa-angle-left subcategory-arrow"></i>' : ''}
                </a>
              </div>
            `).join('')

            // Reinitialize swiper
            setTimeout(() => {
              initSubcategoriesSwiper()
            }, 100)
          }
        }
      })
      .catch(error => {
        console.error('❌ Error fetching subcategories:', error)
        if (subcategoriesList) {
          subcategoriesList.innerHTML = '<div class="error-subcategories">حدث خطأ في التحميل</div>'
        }
      })
  }

  // Hide subcategories with delay
  window.hideSubcategories = function() {
    subcategoriesTimeout = setTimeout(() => {
      const dropdown = document.getElementById('subcategoriesDropdown')
      if (dropdown && isSubcategoriesVisible) {
        dropdown.classList.remove('show')
        setTimeout(() => {
          dropdown.style.display = 'none'
          isSubcategoriesVisible = false
        }, 300)
      }
    }, 200)
  }

  // Keep subcategories visible when hovering over them
  window.keepSubcategoriesVisible = function() {
    if (subcategoriesTimeout) {
      clearTimeout(subcategoriesTimeout)
    }
  }

})()
