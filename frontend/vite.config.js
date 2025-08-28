import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    fs: {
      // Allow serving files from outside the project root (needed for symlinks)
      allow: ['..', '../..']
    }
  },
  // Ensure symlinks are resolved correctly
  resolve: {
    preserveSymlinks: false
  }
})