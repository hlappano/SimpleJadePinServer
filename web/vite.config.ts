import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	server: {
    	allowedHosts: true // Disables host checking (use with caution)
  	},
	plugins: [
		sveltekit({
			compilerOptions: {
				runes: ({ filename }) => {
					// Normalize path slashes for cross-platform matching
					const normalizedPath = filename.replace(/\\/g, '/');
					
					// If it's a library or your copied Carbon folder, let Svelte figure out the mode automatically
					if (
						normalizedPath.includes('node_modules')
						// Add Others includes here ||
					) {
						return undefined; 
					}
					
					// Force runes for your actual local application files
					return true;
				}
			},

			// adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
			// If your environment is not supported, or you settled on a specific environment, switch out the adapter.
			// See https://svelte.dev/docs/kit/adapters for more information about adapters.
			adapter: adapter()
		})
	]
});


