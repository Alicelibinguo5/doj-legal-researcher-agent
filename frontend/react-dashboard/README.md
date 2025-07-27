#import re

import setuptools
 DOJ Research Agent - React Dashboard

A modern, responsive React dashboard for the DOJ Research Agent that provides a beautiful interface for analyzing DOJ press releases and detecting fraud cases.

## Features

- 🎨 **Modern UI**: Clean, professional interface built with Tailwind CSS
- 📊 **Interactive Charts**: Visual representation of charge distributions using Recharts
- 🔍 **Advanced Filtering**: Filter cases by fraud type, sort by various criteria
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- ⚡ **Real-time Updates**: Live progress tracking during analysis
- 📋 **Detailed Results**: Expandable table with comprehensive case information
- 🎯 **Smart Statistics**: Summary cards with key metrics

## Quick Start

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the dashboard directory:
   ```bash
   cd frontend/react-dashboard
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

## Usage

### Configuration

1. **Fraud Type**: Select the type of fraud to analyze (or "Any Type" for all)
2. **Max Pages**: Set the number of DOJ pages to scrape (1-50)
3. **Max Cases**: Set the maximum number of cases to analyze (1-100)

### Analysis Process

1. Configure your analysis parameters using the form
2. Click "Start Analysis" to begin processing
3. Monitor progress in real-time
4. View results in the interactive dashboard

### Results Dashboard

The dashboard displays:

- **Summary Statistics**: Total cases, fraud cases, money laundering cases
- **Charges Chart**: Visual distribution of top charges
- **Cases Table**: Detailed results with filtering and sorting
- **Expandable Details**: Click on any case to view full analysis

## API Integration

The dashboard connects to the same backend API endpoints as the Streamlit version:

- `POST /analyze/` - Start analysis
- `GET /job/{job_id}` - Get job status and results

## Customization

### Styling

The dashboard uses Tailwind CSS for styling. Customize colors and components in:
- `tailwind.config.js` - Theme configuration
- `src/index.css` - Custom CSS classes

### Components

All components are modular and can be easily modified:
- `Header.js` - Navigation and branding
- `AnalysisForm.js` - Configuration form
- `StatsCards.js` - Summary statistics
- `ChargesChart.js` - Chart visualization
- `CasesTable.js` - Results table
- `ProgressIndicator.js` - Status tracking

## Development

### Project Structure

```
src/
├── components/          # React components
│   ├── Header.js
│   ├── AnalysisForm.js
│   ├── StatsCards.js
│   ├── ChargesChart.js
│   ├── CasesTable.js
│   └── ProgressIndicator.js
├── utils/              # Utility functions
│   └── api.js          # API integration
├── App.js              # Main application
├── index.js            # Entry point
└── index.css           # Global styles
```

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Deployment

### Production Build

1. Build the application:
   ```bash
   npm run build
   ```

2. Serve the `build` directory with your preferred web server

### Environment Variables

Set the backend URL if different from default:
```bash
REACT_APP_BACKEND_URL=http://your-backend-url:8000
```

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. 