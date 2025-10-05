// Loading Manager for global loading states
export class LoadingManager {
  constructor() {
    this.overlay = null;
    this.messageElement = null;
    this.isVisible = false;
    this.loadingCount = 0;
  }

  init() {
    this.overlay = document.getElementById('global-loading');
    this.messageElement = document.getElementById('loading-message');
    
    if (!this.overlay) {
      console.warn('Global loading overlay not found');
    }
  }

  show(message = 'Loading...') {
    this.loadingCount++;
    
    if (!this.overlay) return;
    
    if (this.messageElement) {
      this.messageElement.textContent = message;
    }
    
    this.overlay.classList.add('active');
    this.isVisible = true;
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
  }

  hide() {
    this.loadingCount = Math.max(0, this.loadingCount - 1);
    
    if (this.loadingCount > 0) return; // Still loading other things
    
    if (!this.overlay) return;
    
    this.overlay.classList.remove('active');
    this.isVisible = false;
    
    // Restore body scroll
    document.body.style.overflow = '';
  }

  isLoading() {
    return this.isVisible;
  }

  setMessage(message) {
    if (this.messageElement) {
      this.messageElement.textContent = message;
    }
  }

  forceHide() {
    this.loadingCount = 0;
    this.hide();
  }
}