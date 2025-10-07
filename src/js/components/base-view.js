// Base View Class - Foundation for all view components
export class BaseView {
  constructor() {
    this.container = null;
    this.isVisible = false;
    this.hasUnsavedChanges = false;
    this.eventListeners = [];
  }

  async init(data = {}) {
    // Override in subclasses
    this.data = data;
    await this.render();
    this.bindEvents();
  }

  async render() {
    // Override in subclasses
    console.warn('BaseView.render() should be overridden');
  }

  bindEvents() {
    // Override in subclasses to bind event listeners
  }

  async show() {
    const appContainer = document.getElementById('app-container');
    if (appContainer && this.container) {
      appContainer.innerHTML = '';
      appContainer.appendChild(this.container);
      this.isVisible = true;
      await this.onShow();
    }
  }

  async hide() {
    this.isVisible = false;
    this.cleanup();
    await this.onHide();
  }

  async onShow() {
    // Override in subclasses
  }

  async onHide() {
    // Override in subclasses
  }

  cleanup() {
    // Remove event listeners
    this.eventListeners.forEach(({ element, event, handler }) => {
      element.removeEventListener(event, handler);
    });
    this.eventListeners = [];
  }

  addEventListener(element, event, handler) {
    element.addEventListener(event, handler);
    this.eventListeners.push({ element, event, handler });
  }

  createElement(tag, className = '', innerHTML = '') {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (innerHTML) element.innerHTML = innerHTML;
    return element;
  }

  destroy() {
    this.cleanup();
    if (this.container && this.container.parentNode) {
      this.container.parentNode.removeChild(this.container);
    }
  }
}