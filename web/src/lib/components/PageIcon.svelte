<!-- Copyright (c) 2026, Harleen Lappano -->
<!-- All rights reserved. -->
<!--
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
-->
<script lang="ts">
    import { Grid, Row } from "carbon-components-svelte";
    import Icon from "./Icon.svelte";

    interface Props {
        name: string,
        icon: string
    }

    let {
        name = "name",
        icon
    }: Props = $props(); 
    
</script>

<Grid>
    <Row style="display: flex; justify-content: center;">
        <p class="page-icon-txt">{name}</p>
    </Row>
    <Row style="display: flex; justify-content: center;">
        <Icon src={icon} width=100px height=100px slotRight={false}/>
    </Row>
</Grid>

