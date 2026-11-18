<!-- Copyright (c) 2026, Harleen Lappano -->
<!-- All rights reserved. -->
<!--
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
-->
<script lang="ts">

    import {
        Column,
        Tile,
        Stack,
        Tag,
        Heading,
        Text
    } from 'carbon-components-svelte';

    import Icon from '#lib/components/Icon.svelte';
    import type { Snippet } from 'svelte';

    interface Props {
        title: string;
        subtitle?: string;
        icon?: null | string;
        iconWidth?: string;
        stepNum?: null|string
        children?: Snippet;
    }

    let {
        title="",
        subtitle="",
        icon=null,
        iconWidth="10rem",
        stepNum=null,
        children
    }: Props = $props();
</script>


<Column sm={4} md={7} lg={10} >
    <Tile class="card">
        <Stack inline wrap="wrap" orientation="vertical" gap={5}>
            <Stack inline wrap="wrap" orientation="horizontal" gap={5}>
                {#if stepNum != null}
                <Tag class="step-num" type="red">{stepNum}</Tag>
                {/if}
                 <Heading type="productive-heading-04">{title}</Heading>
            </Stack>
            {#if icon != null}
            <div  style="width: 100%">
                <Icon src={icon} width={iconWidth}/>
            </div>
            {/if}
            <Text type="caption-02" lines={10} wrap="break-word" style="width: 100%">{subtitle}</Text>
            {#if children}
            {@render children()}
            {/if}
        </Stack>
    </Tile>
</Column>