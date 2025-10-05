// Toast Notification System
export class Toast {
  static instance = null;
  
  constructor() {
    this.container = null;
    this.toasts = new Map();
    this.nextId = 1;
  }

  static init() {
    if (!Toast.instance) {
      Toast.instance = new Toast();
      Toast.instance.createContainer();
    }
    return Toast.instance;
  }

  static success(message, options = {}) {
    return Toast.instance?.show(message, { ...options, type: 'success' });
  }

  static error(message, options = {}) {
    return Toast.instance?.show(message, { ...options, type: 'error' });
  }

  static warning(message, options = {}) {
    return Toast.instance?.show(message, { ...options, type: 'warning' });
  }

  static info(message, options = {}) {
    return Toast.instance?.show(message, { ...options, type: 'info' });
  }

  createContainer() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  }

  show(message, options = {}) {
    const {
      type = 'info',
      duration = 5000,
      persistent = false,
      html = false
    } = options;

    const id = this.nextId++;
    const toast = this.createToast(id, message, type, html);
    
    this.container.appendChild(toast);
    this.toasts.set(id, toast);

    // Trigger entrance animation
    requestAnimationFrame(() => {
      toast.classList.add('show');
    });

    // Auto-dismiss unless persistent
    if (!persistent && duration > 0) {
      setTimeout(() => {
        this.dismiss(id);
      }, duration);
    }

    return id;
  }

  createToast(id, message, type, html) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.dataset.toastId = id;

    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };

    const titles = {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info'
    };

    toast.innerHTML = `
      <div class="toast-header">
        <span class="toast-icon">${icons[type]}</span>
        <h4 class="toast-title">${titles[type]}</h4>
        <button class="toast-close" onclick="window.Toast?.dismiss(${id})" aria-label="Close">
          ×
        </button>
      </div>
      <div class="toast-message">
        ${html ? message : this.escapeHtml(message)}
      </div>
    `;

    return toast;
  }

  dismiss(id) {
    const toast = this.toasts.get(id);
    if (!toast) return;

    toast.classList.add('removing');
    
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
      this.toasts.delete(id);
    }, 300);
  }

  dismissAll() {
    this.toasts.forEach((_, id) => {
      this.dismiss(id);
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize automatically and make globally available
if (typeof window !== 'undefined') {
  Toast.init();
  window.Toast = Toast;
}