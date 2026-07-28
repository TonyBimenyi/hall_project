import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.laberthavilla.app',
  appName: 'Labertha Villa',
  webDir: 'dist',
  android: {
    allowMixedContent: true,
    backgroundColor: '#061b49'
  },
  server: {
    androidScheme: 'https'
  }
};

export default config;
