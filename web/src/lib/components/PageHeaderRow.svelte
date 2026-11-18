<!-- Copyright (c) 2026, Harleen Lappano -->
<!-- All rights reserved. -->
<!--
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
-->
<script lang="ts">

   import {
    Row,
    Heading
   } from 'carbon-components-svelte';

   let {
    icon = null,
    title = ""
    } = $props();

</script>

{#if icon != null}
<Row class="header-row">
    {@const Icon = icon}
    <Icon style="width: 4rem; height: 4rem"/>
</Row>
{/if}
<Row class="header-row" style="Padding-top: 1rem">
     <Heading class="page-icon-txt" type="productive-heading-03">{title}</Heading>
</Row>
