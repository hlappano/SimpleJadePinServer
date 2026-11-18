// src/env.js
import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	PUBLIC_JADE_SERVER_PROXY_PORT: {
		public: true,
		schema: (value) => value || '4443'
	}
});
