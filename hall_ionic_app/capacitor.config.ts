import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.laberthavilla.app',
  appName: 'Labertha Villa',
  webDir: 'dist',
  android: {
    allowMixedContent: true,
    backgroundColor: '#fbf7f2'
  },
  server: {
    androidScheme: 'https'
  }
};

export default config;
