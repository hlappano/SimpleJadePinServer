
<script lang="ts">

    /*************************************************
     * Imports
     * ***********************************************/
    // Icons
    import Icon from "#lib/components/Icon.svelte";
    import logo from "#lib/assets/logo.svg";

    // Carbon UI Svelte
    import {
        Grid,
        Row,
        Column,
        Tile,
        Stack,
        Button,
        Heading,
        Text,
        OutboundLink
        } from "carbon-components-svelte"
    
    // Svelte
    import { goto } from '$app/navigation';

</script>
<style>
    .home-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: calc(100vh - var(--cds-spacing-09, 3rem));
        box-sizing: border-box;
        @media (min-width: 768px) {
            margin: -2rem;
        }
    }

    
</style>

<div class ="home-container">
<Grid>
    <Row class="header-row">
         <Icon src={logo} width=339px height=126px/>
    </Row>
    <Row class="sub-row">
        <Heading class="page-icon-txt">Welcome to Your Personal Blockstream Jade Blind Oracle PIN Server</Heading>
        <Stack orientation="vertical" style="padding-top: 25px; display: flex; justify-content: flex" gap={3}>
            <div>
                <Text weight="light" type="body-long-02">
                    A simple reimplementation of the blind_pin_server for the Blockstream Jade hardware wallet, along with a web interface.
                    This implementation supports QR PIN Unlock, unlike Blockstream's version of the self-hosted blind oracle.
                    This makes it the only self-hosted implementation that allows the Jade hardware wallet to be used in an air-gapped way.
                </Text>
            </div>
            <div>
                <Text weight="semibold" type="body-long-02">
                    The intent for this software is to be your own personal blind oracle server. You are the admin.
                </Text>
            </div>
            <div>
                <Text weight="light" type="body-long-02">
                    Originally forked the SimpleJadePinServer from <OutboundLink inline href="http://github.com/Filiprogrammer/SimpleJadePinServer">Filioprogrammer</OutboundLink> and incorporated parts from <OutboundLink inline href="https://github.com/boltadvantage/SimpleJadePinServer">BoltAdvantages's</OutboundLink> fork.
                    Rewrote the server backend to be on a Gevent Flask and created a web front end using Svelte with Carbon UI.
                    The reasoning for the rearch was needing some custom configurations for UmbrelOS, including camera focus and zoom, as well as wanted to just have fun making it into a Svelte App.
                    Some added features include: Camera Zoom and Autofocus for supported devices, adding/removing custom acceptable ports and host names.
                    Not affiliated with or endorsed by Blockstream.
                </Text>
            </div>
        </Stack>
    </Row>
    <Row class="sub-row" style="display: flex; align-items: stretch; padding-top: 1rem; margin-bottom: 1rem;">
    <Column style="display: flex; flex-direction: column;">
        <Tile class="card" style="display: flex; flex-direction: column; flex: 1;">
            <Stack orientation="vertical" gap={3} style="display: flex; flex-direction: column; flex: 1;">
                <Text type="caption-02">First time admin, configure settings with proper port and host.</Text>
                <div style="margin-top: auto;">
                    <Button class="jade-button" size="small" style="max-width: 15rem" on:click={()=> goto('/settings')}>Settings →</Button>
                </div>
            </Stack>
        </Tile>
    </Column>
    <Column style="display: flex; flex-direction: column;">
        <Tile class="card" style="display: flex; flex-direction: column; flex: 1;">
            <Stack orientation="vertical" gap={3} style="display: flex; flex-direction: column; flex: 1;">
                <Text type="caption-02">To be able to use this Blind Oracle, you must point your Jade to this server.</Text>
                <div style="margin-top: auto;">
                    <Button class="jade-button" size="small" style="max-width: 15rem" on:click={()=> goto('/oracle')}>Register →</Button>
                </div>
            </Stack>
        </Tile>
    </Column>
    </Row>
</Grid>
</div>