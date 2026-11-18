<!-- Copyright (c) 2026, Harleen Lappano -->
<!-- All rights reserved. -->
<!--
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
-->

<!-- Landing page -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    // Reroute onMount
    onMount(async () => {
        goto('/home');
	});
</script>
