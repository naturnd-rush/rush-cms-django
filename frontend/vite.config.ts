import { defineConfig } from 'vite'

export default defineConfig({
    root: '../frontend/', // root of vite project (frontend/)
    base: './', // relative paths in output
    build: {
        outDir: '../static/js/compiled', // or wherever you want the compiled output
        emptyOutDir: true,
        rollupOptions: {
            input: './index.html', // entry point for JS/CSS
        }
    }
})
