# SevDesk API Client

A modern, modular web application built with Vite for interacting with the SevDesk API. Features bulk invoice creation, responsive design, and a scalable architecture for future expansion.

## ✨ Features

- **🔐 Secure Authentication**: Persistent API key storage with connection validation
- **📄 Bulk Invoice Creation**: Create multiple invoices efficiently through:
  - Manual entry with dynamic form fields
  - CSV import for batch processing
- **📱 Modern UI/UX**: Responsive design with toast notifications and loading states
- **�️ Modular Architecture**: Component-based structure using ES6 modules
- **⚡ Fast Development**: Vite-powered with hot reload and optimized builds
- **🎯 Extensible**: Easy to add new SevDesk API features and modules

## 🚀 Quick Start

### Prerequisites

- **Node.js 16+** (for development)
- **SevDesk Account** with API access
- **Modern Browser** (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/florianschoffke/sevdesk-client.git
cd sevdesk-client
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

4. **Open your browser:**
   - Navigate to `http://localhost:3000`
   - Enter your SevDesk API key
   - Start creating invoices!

### Production Build

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview
```

## 📁 Project Structure

```
sevdesk-client/
├── src/
│   ├── js/
│   │   ├── components/          # View components (Auth, Dashboard, etc.)
│   │   ├── utils/              # Utilities (API, Auth, Router, etc.)
│   │   ├── app.js              # Main application class
│   │   └── main.js             # Application entry point
│   ├── css/
│   │   ├── base/               # Reset, variables, typography, layout
│   │   ├── components/         # Component styles (buttons, forms, etc.)
│   │   ├── views/              # View-specific styles
│   │   ├── utilities/          # Helper classes & responsive design
│   │   └── main.css            # CSS entry point
│   └── assets/                 # Static assets
├── public/                     # Public assets (favicon, etc.)
├── index.html                  # Main HTML file
├── vite.config.js             # Vite configuration
├── package.json               # Dependencies and scripts
└── README.md                  # This file
```

## 🛠️ Development

### Available Scripts

```bash
npm run dev      # Start development server with hot reload
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
npm run format   # Format code with Prettier
```

### Adding New Features

1. **New View Component:**
   - Create in `src/js/components/`
   - Register in `src/js/app.js`
   - Add route in router setup

2. **New Utility:**
   - Create in `src/js/utils/`
   - Import where needed

3. **New Styles:**
   - Add component styles to `src/css/components/`
   - Import in `src/css/main.css`

### Code Style

- **ES6+** modules with import/export
- **Class-based** components
- **Event-driven** architecture
- **Consistent naming** (camelCase for JS, kebab-case for CSS)
- **JSDoc comments** for complex functions

## 🎯 Usage Guide

### Initial Setup

1. **Launch the application**
2. **Enter API credentials:**
   - SevDesk API key (required)
   - API base URL (optional, defaults to SevDesk's endpoint)
3. **Connection test** runs automatically
4. **Navigate to dashboard** on successful authentication

### Creating Bulk Invoices

#### Method 1: Manual Entry

1. **Select "Create Bulk Invoices"** from dashboard
2. **Choose "Manual Entry"** tab
3. **Fill invoice details:**
   - Contact ID (SevDesk customer ID)
   - Invoice date
   - Invoice type (RE/AB/AN)
   - Currency (EUR/USD/GBP)

4. **Add positions:**
   - Description, quantity, price
   - Tax rate (19%/7%/0%)
   - Use "Add Position" for multiple items

5. **Process invoices:**
   - "Add to Batch" → Collect multiple invoices
   - "Create Single Invoice" → Process immediately
   - "Create All Invoices" → Process entire batch

#### Method 2: CSV Import

1. **Prepare CSV file** with columns:
   ```csv
   contactId,invoiceDate,description,quantity,price,taxRate
   123,2024-10-05,"Web Development",1,1500.00,19
   124,2024-10-05,"Consulting",8,120.00,19
   ```

2. **Upload file:**
   - Drag & drop or click to select
   - Preview shows first 5 rows
   - Click "Process CSV & Create Invoices"

### Finding Contact IDs

**In SevDesk dashboard:**
1. Go to Contacts section
2. Open any contact
3. ID is visible in URL or contact details

**Via API:**
- Use browser dev tools to inspect network requests
- Contact IDs are returned in API responses

## 🔧 Technical Details

### Architecture

- **Component-based**: Modular view components with lifecycle management
- **Event-driven**: Custom EventEmitter for inter-component communication
- **Router-based**: Client-side routing for SPA navigation
- **API abstraction**: Centralized SevDesk API client with rate limiting

### Key Classes

- **`App`**: Main application orchestrator
- **`AuthManager`**: Handles authentication and credential storage
- **`Router`**: Client-side routing system
- **`SevDeskAPI`**: API client with error handling
- **`Toast`**: Global notification system

### SevDesk API Integration

**Endpoints used:**
- `GET /Contact` - Authentication testing
- `POST /Invoice/Factory/saveInvoice` - Bulk invoice creation

**Data format:**
```javascript
{
  invoice: {
    invoiceType: "RE",
    contact: { id: 123, objectName: "Contact" },
    invoiceDate: "2024-10-05",
    status: 100,
    currency: "EUR"
  },
  invoicePosSave: [{
    objectName: "InvoicePos",
    quantity: 1,
    price: 1500.00,
    name: "Service Description",
    taxRate: 19
  }]
}
```

## 🌐 Browser Support

**Modern browsers with ES6+ support:**
- Chrome 80+ ✅
- Firefox 75+ ✅  
- Safari 13+ ✅
- Edge 80+ ✅

**Required features:**
- ES6 Modules, Fetch API, CSS Custom Properties
- Local Storage, History API

## 🔒 Security & Privacy

- **Client-side only**: No server-side storage or processing
- **Local storage**: API keys stored in browser localStorage
- **Direct API calls**: Communication directly with SevDesk servers
- **HTTPS recommended**: Use secure hosting for production deployments
- **No telemetry**: No usage tracking or analytics

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Invalid API key error** | • Verify key in SevDesk settings<br>• Remove extra spaces<br>• Ensure API access is enabled |
| **Contact ID not found** | • Check contact exists in SevDesk<br>• Verify ID is correct number<br>• Ensure contact is active |
| **CORS errors** | • Use development server (`npm run dev`)<br>• Don't open HTML file directly |
| **Network timeout** | • Check internet connection<br>• Try again in a few minutes<br>• Verify SevDesk server status |
| **Build errors** | • Run `npm install` to update dependencies<br>• Clear browser cache<br>• Check Node.js version (16+) |

### Development Issues

```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite node_modules/.vite

# Reset git (if needed)
git clean -fdx
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork and clone:**
```bash
git clone https://github.com/yourusername/sevdesk-client.git
cd sevdesk-client
npm install
```

2. **Create feature branch:**
```bash
git checkout -b feature/amazing-feature
```

3. **Make changes and test:**
```bash
npm run dev    # Test in development server
npm run build  # Test production build
npm run lint   # Check code style
```

4. **Submit pull request**

### Adding Features

**New API Module:**
```javascript
// src/js/utils/contacts-api.js
export class ContactsAPI {
  constructor(api) {
    this.api = api;
  }
  
  async getAll() {
    return this.api.get('/Contact');
  }
}
```

**New View Component:**
```javascript
// src/js/components/contacts.js
import { BaseView } from './base-view.js';

export class ContactsView extends BaseView {
  async init() {
    // Initialize view
  }
  
  async show() {
    // Render view
  }
}
```

## 📜 License

**MIT License** - Feel free to use this project for personal or commercial purposes.

See [SevDesk API Terms](https://api.sevdesk.de/) for API usage restrictions.

## 🆘 Support & Resources

### Documentation
- **[SevDesk API Docs](https://api.sevdesk.de/)** - Official API documentation
- **[Vite Guide](https://vitejs.dev/guide/)** - Build tool documentation
- **[MDN Web Docs](https://developer.mozilla.org/)** - Web standards reference

### Getting Help
1. **Check the troubleshooting section above**
2. **Search existing [GitHub issues](https://github.com/florianschoffke/sevdesk-client/issues)**
3. **Create a new issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Browser and Node.js versions
   - Console error messages

### SevDesk Support
- **[SevDesk Help Center](https://sevdesk.de/support/)**
- **[SevDesk Community](https://community.sevdesk.de/)**

---

**Made with ❤️ for better invoice management**
