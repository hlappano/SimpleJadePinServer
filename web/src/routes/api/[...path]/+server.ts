import type { RequestHandler } from './$types';

const BACKEND_URL = 'http://127.0.0.1:4443';

async function proxyToBackend(
	method: string,
	path: string,
	url: URL,
	request: Request
): Promise<Response> {
	// /api/get_allowed_hosts_type -> params.path is "get_allowed_hosts_type"
	// targetUrl becomes "http://127.0.0.1:4443/get_allowed_hosts_type"
	const cleanPath = path.startsWith('/') ? path.substring(1) : path;
	const targetUrl = `${BACKEND_URL}/${cleanPath}${url.search}`;

	const headers = new Headers(request.headers);
	headers.delete('host');
	headers.delete('connection');
	headers.delete('content-length');

	const init: RequestInit = {
		method,
		headers
	};

	if (method !== 'GET' && method !== 'HEAD') {
		init.body = request.body;
		(init as RequestInit & { duplex?: 'half' }).duplex = 'half';
	}

	const upstreamResponse = await fetch(targetUrl, init);

	const responseHeaders = new Headers(upstreamResponse.headers);
	responseHeaders.delete('content-encoding');
	responseHeaders.delete('content-length');

	return new Response(upstreamResponse.body, {
		status: upstreamResponse.status,
		statusText: upstreamResponse.statusText,
		headers: responseHeaders
	});
}

export const GET: RequestHandler = ({ params, url, request }) =>
	proxyToBackend('GET', params.path, url, request);

export const POST: RequestHandler = ({ params, url, request }) =>
	proxyToBackend('POST', params.path, url, request);

export const PUT: RequestHandler = ({ params, url, request }) =>
	proxyToBackend('PUT', params.path, url, request);

export const PATCH: RequestHandler = ({ params, url, request }) =>
	proxyToBackend('PATCH', params.path, url, request);

export const DELETE: RequestHandler = ({ params, url, request }) =>
	proxyToBackend('DELETE', params.path, url, request);

export const OPTIONS: RequestHandler = ({ params, url, request }) =>
	proxyToBackend('OPTIONS', params.path, url, request);