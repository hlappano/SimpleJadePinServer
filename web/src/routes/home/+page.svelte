
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
        Tile,
        Stack,
        Button,
        Heading,
        Text
        } from "carbon-components-svelte"
    
    // Svelte
    import { goto } from '$app/navigation';

</script>

<Grid>
    <Row class="header-row">
         <Icon src={logo} width=339px height=126px/>
    </Row>
    <Row class="sub-row">
        <Heading class="page-icon-txt">Welcome to Blockstream Jade Blind Oracle PIN Server</Heading>
        <Stack orientation="vertical" style="padding-top: 25px; display: flex; justify-content: flex" gap={3}>
            <div>
                <Text weight="light" type="body-long-02">
                    A simple reimplementation of the blind_pin_server for the Blockstream Jade hardware wallet, along with a web interface.
                    This implementation supports QR PIN Unlock, unlike Blockstream's version of the self-hosted blind oracle.
                    This makes it the only self-hosted implementation that allows the Jade hardware wallet to be used in an air-gapped way.
                </Text>
            </div>
            <div>
                <Text weight="light" type="body-long-02">
                    Originally forked from SimpleJadePinServer by Filioprogrammer and incorporated parts from BoltAdvantages's fork.
                    Rewrote the server backend to be on a Gevent Flask and created a web front end using Svelte with Carbon UI.
                    Added some features to help improve user experience for deployed servers like UmbrelOS.
                    Not affiliated with or endorsed by Blockstream.
                </Text>
            </div>
        </Stack>
    </Row>
    
    <Row class="sub-row" style="padding-bottom: 0; padding-top: 1rem">
        <Tile class="card">
            <Stack orientation="vertical" gap={3}>
                <Text type="caption-02">To be able to use this Blind Oracle, you must point your Jade to this server.</Text>
                <Button class="jade-button" size="small" style="max-width: 15rem" on:click={()=> goto('/oracle')}>Open Oracle QR generator →</Button>
            </Stack>
        </Tile>
    </Row>

    <Row class="sub-row">
        <!-- Intentionally blank for gap -->
    </Row>
</Grid>
