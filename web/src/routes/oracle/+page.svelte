
<script lang="ts">

    /*************************************************
     * Imports
     * ***********************************************/
    // Icons
    import Icon from "#lib/components/Icon.svelte";
    import ScanQRImage from "#lib/assets/jade_blind_oracle_scan_qr.png";
    import BlindOracleMenuImage from '#lib/assets/jade_boot_menu_blind_oracle.png';
    import ConfirmImage from '#lib/assets/jade_confirm_pin_server.png';
    import QrCode from "carbon-icons-svelte/lib/QrCode.svelte";

    // Custom
    import {
        PageHeaderRow,
        ColumnCard
    } from '#lib';

    // Svelte
    import {
        onMount,
    } from 'svelte';

    // Svelte nav
    import { goto } from '$app/navigation';

    // Carbon UI Components
    import {
        Grid,
        Row,
        InlineNotification,
        Stack,
        OrderedList,
        ListItem,
        Button,
        TextInput,
        TextArea,
        Text
    } from 'carbon-components-svelte';

    // Javascript jade helpers
    import {
        getApiUrl,
        getBackendUrls
    } from '#lib/utils/jade-proto.js';
    import {
        generate
    } from '#lib/utils/qr-helpers.js';


    /*************************************************
     * Data Members
     * ***********************************************/
    // Props definition
    interface Props {
        urlA?: string;
        urlB?: string;
        pubkey?: string;
        qrDiv?: any;
    }
    // Props
    let {
        urlA="http://127.0.0.1:4443",
        urlB="",
        pubkey="N/A",
        qrDiv = $bindable()
    }: Props = $props();

    // State of has QR Code
    let hasQrCode = $state(false);

    // State of in loading process
    let loading = $state(true);

    /*************************************************
     * Functions
     * ***********************************************/

     /**
      * Get the Public Key from Server
      */
    async function getPubKey() {
        const xhttp = new XMLHttpRequest();
        const targetUrl = getApiUrl('/get_pub');
        xhttp.open("GET", targetUrl, true);

        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    const response = JSON.parse(this.responseText);
                    // Match the Flask return key: data.data
                    pubkey = response.data;
                } else {
                    console.error("Failed to fetch public key, status:", this.status);
                }
            }
        };
        
        // Don't forget to actually send the request!
        xhttp.send();
    }

    /**
     * Svelte's onMount
    */
    onMount(async () => {
        await getPubKey();

        var urls = getBackendUrls();
        if (urls.length > 0) {
            urlA = urls[0];
            if (urls.length > 1) {
                urlB = urls[1];
            }
        }
        loading = false;
    });

    /**
     * onGenerate Event
     * Generating the QR Code for the Oracle Server
     */
    function onGenerate() {
        generate(urlA, urlB, pubkey, qrDiv);
        hasQrCode = true;
    }
</script>

{#if !loading }
<Grid fullWidth>
    <PageHeaderRow
        title="Oracle QR Code Register"
        icon={QrCode}
    />
    <Row class="sub-row">
        <ColumnCard
            title="Prepare Jade"
            stepNum=1
        >
            <Stack inline wrap="wrap" orientation="vertical" gap={3}>
                <InlineNotification
                    class="card-note"
                    hideCloseButton
                    kind="warning-alt"
                    title="Warning: Your funds will be lost if you do not have the correct backup materials."
                    subtitle="Jade will need to be uninitialized in order to set a new blind oracle. If your Jade is already set up, you will need to perform a factory reset and restore using your recovery phrase. Your funds will be lost if you do not have the correct backup materials."
                ></InlineNotification>
                <OrderedList class="steps">
                    <ListItem>
                        Required an uninitialized Jade Wallet. Backup seed and factory reset before proceeding.
                    </ListItem>
                    <ListItem>
                        Turn on Jade and access the boot menu by clicking (not holding) the center button once while the logo screen is showing.
                    </ListItem>
                    <ListItem>
                        Select Blind Oracle.
                        <Icon src={BlindOracleMenuImage} width="24rem"/>
                    </ListItem>
                    <ListItem>
                        Select Scan Oracle QR.
                        <Icon src={ScanQRImage} width="24rem"/>
                    </ListItem>
                    <ListItem>
                        Proceed to next step.
                    </ListItem>
                </OrderedList>
            </Stack>
        </ColumnCard>
    </Row>
    <Row class="sub-row">
        <ColumnCard
            title="Generate and Scan QR Code"
            subtitle="Server Details"
            stepNum=2
        >
            <Stack wrap="wrap" orientation="vertical" gap={3}>
                <InlineNotification
                    class="card-note"
                    kind="info"
                    hideCloseButton
                    title="Info"
                    subtitle="
                    These are the URLs that the Blockstream app reads from the Jade Wallet to make the pin requests.
                    You can edit the URLs and add add a fallback URL if needed before generating QR Code.
                    If using the Airgap method, these can be left alone to defaults.
                    "
                />
                <InlineNotification
                    class="card-note"
                    kind="warning"
                    hideCloseButton
                    title="Warning"
                    subtitle="If you are not using the Airgap method, make sure these urls are accessible before continuing. If not, check the settings."
                />

                <TextInput
                    labelText="Primary URL"
                    bind:value={urlA}/>
                <TextInput
                    labelText="2nd URL [optional]"
                    placeholder="http://fallback"
                    bind:value={urlB}/>
                <TextArea
                    readonly
                    rows={1}
                    labelText="Server Public Key (hex)"
                    bind:value={pubkey}/>

                <Stack wrap="wrap" orientation="vertical" gap={3}>
                    <div style="padding-top: .5rem">
                        <Button class="jade-button" size="small" style="max-width: 15rem" on:click={() => onGenerate() }>Generate QR Code</Button>
                    </div>
                    {#if hasQrCode}
                    <InlineNotification
                        class="card-note"
                        hideCloseButton
                        kind="success"
                        title="QR Code Generated!"
                        subtitle="Scan the QR code with your jade device"
                        />
                    {/if}
                    <div bind:this={qrDiv} style="text-align: center"></div>
                </Stack>
            </Stack>
        </ColumnCard>
    </Row>
    <Row class="sub-row">
        <ColumnCard
            title="Confirm"
            stepNum=3
            icon={ConfirmImage}
            iconWidth="24rem"
            subtitle="Confirm the On-Screen Details and Continue Setting Up Jade with PIN on Your Preferred Companion App."
        >
            <Stack wrap="wrap" orientation="vertical" gap={3}>
                <InlineNotification
                    class="card-note"
                    hideCloseButton
                    kind="info"
                    title="Note"
                    subtitle="If the Jade is used only in QR mode, it does not matter where the URL points to, making the public key of the pin server the only important parameter.
However, firmware upgrades on an initialized Jade require the wallet to be unlocked over USB or Bluetooth, so the URL must be correct and reachable during that process. This requirement does not apply to the Jade Plus, since it supports air-gapped firmware upgrades via external USB storage.
Alternatively, one can always factory-reset the Jade, apply the firmware upgrade, and then re-initialize it afterwards."
                />
                <OrderedList class="steps">
                <ListItem>
                    Confirm Primary URL is correct on device
                    <Text type="label-02" color="secondary" italic>"{urlA}"</Text>
                </ListItem>
                <ListItem>
                    Confirm 2nd URL is correct on device (if available)
                    <Text type="label-02" color="secondary" italic>"{urlB}"</Text>
                </ListItem>
                <ListItem>
                    Confirm public key matches on device
                    <Text type="label-02" color="secondary" italic>"{pubkey}"</Text>
                </ListItem>
                <ListItem>
                    Select and Click Check or Confirm Option on the Jade.
                </ListItem>
                <ListItem>
                    Continue to the QR PIN to setup PIN
                    
                </ListItem>
                
            </OrderedList>
            <Button class="jade-button" size="small" style="max-width: 13rem" on:click={()=> goto('/qr_pin')}>
                    Open Oracle QR PIN →
                    </Button>
            </Stack>
            
            
        </ColumnCard>
    </Row>
    <Row class="sub-row">
        <!-- Leave blank for space -->
    </Row>
</Grid>
{/if}