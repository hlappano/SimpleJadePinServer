<!-- Copyright (c) 2026, Harleen Lappano -->
<!-- All rights reserved. -->
<!--
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
-->
<script lang="ts">
  import type { Snippet } from "svelte";

  interface Props {
    src: string;
    alt?: string;
    width?: string;
    height?: string;
    slotRight?: boolean;
    gap?: string;
    children?: Snippet;
  }

  let { 
        src,
        alt = "icon",
        width="45px",
        height="45px",
        slotRight = true,
        gap="8px",
        children = (() => {}) as Snippet
    }: Props = $props();
  
    // Check if width is a percentage
    let isPercentage = $derived(width.endsWith('%'));
    let numericValue = $derived(isPercentage ? parseFloat(width.replace('%', '')) : 0);
    let mobileWidth = $derived(isPercentage ? `${numericValue * 1.5}%` : width);
</script>

<style>

   .cs-icon-wrapper img {
      width: var(--desktop-width);
      height: var(--height);
   }

   @media (max-width: 768px) {
    .cs-icon-wrapper img {
      width: var(--mobile-width);
    }
  }
</style>

<div class = "cs-icon-wrapper"
  style="gap: {gap};  --desktop-width: {width}; --mobile-width: {mobileWidth}; -height: {height};">
  {#if ! slotRight && children}
    {@render children()}
  {/if}
  <!-- <img src={src} alt={alt} style="width: {width}; height: {height}};" /> -->
  <img src={src} alt={alt}/>
  {#if slotRight && children}
    {@render children()}
  {/if}
</div>