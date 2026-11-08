import { fileURLToPath } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vitest/config'

const testsDir = fileURLToPath(new URL('../tests/frontend', import.meta.url)).replaceAll('\\', '/')
const frontendEntry = fileURLToPath(new URL('./index.html', import.meta.url))

// Tests live in the root tests/ folder (AGENTS.md section 2), outside this project.
// Resolve their package imports (react, vitest, ...) from frontend/node_modules.
const resolveTestImports: Plugin = {
  name: 'resolve-test-imports',
  enforce: 'pre',
  resolveId(source, importer, options) {
    const isPackage = !source.startsWith('.') && !source.startsWith('/') && !source.includes(':')
    if (isPackage && importer?.replaceAll('\\', '/').startsWith(testsDir)) {
      return this.resolve(source, frontendEntry, { ...options, skipSelf: true })
    }
  },
}

export default defineConfig({
  plugins: [react(), tailwindcss(), resolveTestImports],
  server: { fs: { allow: ['..'] } },
  test: {
    dir: '../tests/frontend',
    environment: 'jsdom',
  },
})
