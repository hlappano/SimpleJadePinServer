// Copyright (c) 2026, Harleen Lappano
// All rights reserved.
//
// This source code is licensed under the MIT license found in the
// LICENSE file in the root directory of this source tree.

import { readable } from 'svelte/store';
import { PUBLIC_JADE_SERVER_PROXY_PORT } from '$app/env/public';

export const jade_proxy_port = readable(PUBLIC_JADE_SERVER_PROXY_PORT);
