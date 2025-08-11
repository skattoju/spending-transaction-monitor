import type { Preview } from "@storybook/react";
import React from 'react';
import '../src/styles/globals.css'
import { themes } from '@storybook/theming';
import { ThemeProvider } from '../src/components/theme-provider/theme-provider';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    darkMode: {
      dark: { 
        ...themes.dark, 
        appBg: '#0a0a0a',
        appContentBg: '#0a0a0a',
        appBorderColor: '#27272a',
        textColor: '#fafafa'
      },
      light: { 
        ...themes.normal, 
        appBg: '#ffffff',
        appContentBg: '#ffffff',
        appBorderColor: '#e4e4e7',
        textColor: '#09090b'
      },
      // Override the default theme with our theme
      stylePreview: true,
    },
    backgrounds: {
      disable: true, // Disable the default backgrounds addon since we're using dark-mode
    },
  },
  decorators: [
    (Story, context) => {
      // Get the current theme from the storybook-dark-mode addon
      const darkModeGlobal = context.globals?.darkMode;
      const isDark = darkModeGlobal === true || darkModeGlobal === 'dark';
      
      // Apply theme class to document root for proper Tailwind dark mode
      if (typeof document !== 'undefined') {
        document.documentElement.classList.toggle('dark', isDark);
        document.documentElement.classList.toggle('light', !isDark);
      }

      return React.createElement(
        ThemeProvider,
        { defaultTheme: isDark ? 'dark' : 'light' },
        React.createElement(
          'div',
          { className: 'bg-background text-foreground p-4' },
          React.createElement(Story)
        )
      );
    },
  ],
};

export default preview;