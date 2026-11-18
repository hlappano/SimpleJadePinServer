<script lang='ts'>

    /*************************************************
     * Imports
     * ***********************************************/
    // Icons
    import UnlockJade from '#lib/assets/jade_unlock_pin.png';
    import Encryption from "carbon-icons-svelte/lib/Encryption.svelte";

    // Custom Components
    import {
        PageHeaderRow,
        ColumnCard
    } from '#lib';

    // Svelte functions
    import {
        onMount,
        onDestroy
    } from 'svelte';

    // Carbon UI Components
    import {
        Grid,
        Row,
        InlineNotification,
        Box,
        Stack,
        Tag,
        OrderedList,
        ListItem,
        Button,
        Divider,
        TextArea,
        ProgressBar,
        Dropdown,
    } from 'carbon-components-svelte';

    // Javascript Camera Helpers
    import {
        registerAlertNotification,
        registerZoomAlertNotification,
        registerProgressBarState,
        registerPinState,
        listCameras,
        startCameraScanning,
        stopCameraScanning
    } from '#lib/utils/cam-helper.js';

    // Javascript Jade Proto Helpers
    import {
        set_pin,
        get_pin
    } from '#lib/utils/jade-proto.js';

    /*************************************************
     * Variables
     * ***********************************************/
    /**
     * Notification Type
     */
    type NotificationType = "error" | "info" | "info-square" | "success" | "warning" | "warning-alt";


     // Alert Notification State
     let alertState: {
        kind: NotificationType
        title: string,
        subtitle: string,
        open: boolean
     } = $state({
        'kind': "info",
        'title': "Initializing...",
        'subtitle': "Waiting for camera stream.",
        'open': true
    });

    // Zoom Alert notification state
    let zoomAlertState: {
        kind: NotificationType
        title: string,
        subtitle: string,
        open: boolean
     } = $state({
        'kind': "info",
        'title': "",
        'subtitle': "",
        'open': false
    });

    // Progress Bar State - during camera capture
    let progressBarState: {
        active: boolean,
        value: number,
        max: number,
        statusText: string
    } = $state({
        'active': false,
        'value': 1,
        'max': 1,
        'statusText': "1 out of 1"
    });

    // Camera Selection State
    let cameraSelectionState: {
        cameraList: Array<{id: string; text: string }>,
        selectedId: string
    } = $state({
        'cameraList': [],
        'selectedId': "0"
    });


    /**
     * Fill Type
     */
    type FillType = "background" | "layer-01" | "layer-02" | "layer-03" | "layer-accent" | "field" | "inverse" | "brand" | undefined
    
    // Cam Fill Value
    let camFillValue: FillType
        = $state(undefined);

    // QR Fill Value
    let qrFillValue: FillType
        = $state(undefined);

    // Pin State - includes the buttons, requests and replies.
    let pinState: {
        buttonScanStartDisabled: boolean,
        buttonScanStopDisabled: boolean,
        buttonReplyDisabled: boolean,
        qr_pin_request: string,
        qr_pin_reply: string,
        replyFunction: string,
        isReplyGenerating: boolean
    } = $state({
        'buttonScanStartDisabled': true,
        'buttonScanStopDisabled': true,
        'buttonReplyDisabled': true,
        'qr_pin_request': "?",
        'qr_pin_reply': "?",
        'replyFunction': "set/get",
        'isReplyGenerating': false
    })

    // True request Value
    let requestValue = 
        $derived(`${pinState.replyFunction}: ${pinState.qr_pin_request || ''}`);

    // True reply value
    let replyValue =
        $derived(`data: ${pinState.qr_pin_reply}`);

    /*************************************************
     * Functions
     * ***********************************************/
    
    /**
    * loads the cameras at startup
    */
    function loadCameras()
    {
        listCameras()
            .then((devices) => {
                cameraSelectionState.cameraList = devices.map((d, i) => ({
                    id: d.id,
                    text: d.label || ("Camera " + (i +1))
                }));

                if (cameraSelectionState.cameraList.length > 0)
                {
                    cameraSelectionState.selectedId = cameraSelectionState.cameraList[0].id;
                    pinState.buttonScanStartDisabled = false;
                }
                else {
                    pinState.buttonScanStartDisabled = true;
                }
            })
            .catch((err) => {
                console.error("Failed to list cameras: ", err);
            });
    }

    /**
     * Svelte's onMount
    */
    onMount(() => {
        // link progress bar
        registerProgressBarState(progressBarState);
        // link alert notificaiton
        registerAlertNotification(alertState);
        // link zoom alert notification
        registerZoomAlertNotification(zoomAlertState);
        // link buttons state
        registerPinState(pinState);

        loadCameras();
        
    });

    /**
     * Svelte's onDestroy - ensures we stop the camera when page transitions
    */
    onDestroy(() => {
        if (typeof window !== 'undefined')
            onCameraStop();
    })

    /**
     * onCameraStart event - activates the selected camera
     */
    function onCameraStart() {
        if (cameraSelectionState.cameraList.length > 0)
        {
            startCameraScanning(cameraSelectionState.selectedId);
        }

        camFillValue = "layer-accent";
    };

    /**
     * onCameraStop event
     */
    function onCameraStop() {
        stopCameraScanning();

        camFillValue = undefined;
    }

    /**
     * onReplyClick event
     */
    async function onReplyClick() {
        pinState.isReplyGenerating = true;
        try {
            if (pinState.replyFunction === "set_pin")
            {
                pinState.qr_pin_reply = await set_pin();
            }
            else if (pinState.replyFunction === "get_pin")
            {
                pinState.qr_pin_reply = await get_pin();
            }
        }
        finally {
            pinState.isReplyGenerating = false;
            qrFillValue = "layer-accent";
        }
    }
</script>


<Grid fullWidth>
    <PageHeaderRow icon={Encryption} title="QR PIN"/>
    <Row class="sub-row">
        <ColumnCard
            title="Enter your PIN on Jade to Unlock"
            stepNum=1
            subtitle="On Jade Wallet:"
            icon={UnlockJade}
            iconWidth="50%"
        >
            <div>
                <OrderedList class="steps">
                    <ListItem>
                        Select QR Mode.
                    </ListItem>
                    <ListItem>
                        Select QR PIN Unlock.
                    </ListItem>
                    <ListItem>
                        Click Continue.
                    </ListItem>
                    <ListItem>
                        Enter Jade PIN.
                    </ListItem>
                    <ListItem>
                        Go to next step.
                    </ListItem>
                </OrderedList>
            </div>
        </ColumnCard>
    </Row>
    <Row class="sub-row">
        <ColumnCard
            title="PIN request - Jade to Server"
            subtitle="Scan the QR code it displays"
            stepNum=2
        >
            <Dropdown
                labelText="Cameras"
                bind:selectedId={cameraSelectionState.selectedId}
                items={cameraSelectionState.cameraList}
            />

            <Stack inline  wrap="wrap" orientation="horizontal" gap={5} style="padding-top: 25px">
                <Button
                    class="jade-button"
                    size="small" 
                    disabled={pinState.buttonScanStartDisabled}
                    on:click={() => onCameraStart() } >Start Camera</Button>
                <Button
                    class="jade-button"
                    size="small"
                    disabled={pinState.buttonScanStopDisabled}
                    on:click={() => onCameraStop() }>Stop Camera</Button>
                <Button
                    class="jade-button"
                    size="small"
                    on:click={() => loadCameras() }>Recheck Cameras</Button>
            </Stack>

            <InlineNotification
                class="card-note"
                bind:open={alertState.open}
                hideCloseButton
                kind={alertState.kind}
                title={alertState.title}
                subtitle={alertState.subtitle}
                />
            <InlineNotification
                class="card-note"
                bind:open={zoomAlertState.open}
                hideCloseButton
                kind={zoomAlertState.kind}
                title={zoomAlertState.title}
                subtitle={zoomAlertState.subtitle}
                />
            
            {#if progressBarState.active }
            <div style="padding-top: 1rem; padding-bottom: 1rem;">
                <ProgressBar
                    value={progressBarState.value}
                    max={progressBarState.max}
                    labelText="Captured Progress"
                    helperText={progressBarState.statusText}
                />
                </div>
            {/if}
            
            <Box
                fill={camFillValue}
                padding="2rem"
            >
                <div id="qrreader1"></div>
            </Box>

            <!-- Add inline notifications -->
            <Divider/>
            
            <Stack wrap="wrap" inline  class="readout" orientation="horizontal" gap={2}>
                <Tag type="red" class="tag-label">Response</Tag>
                <TextArea
                    readonly
                    rows={1}
                    labelText=""
                    bind:value={requestValue}
                    />
            </Stack>
        </ColumnCard>
    </Row>
    <Row class="sub-row">
        <ColumnCard
            title="PIN Reply - Server to Jade"
            subtitle="Generate the reply, then scan it from Jade's screen."
            stepNum=3
        >
            <Button
                class="jade-button"
                size="small"
                style="max-width: 11rem"
                on:click={() => onReplyClick()}
                disabled={pinState.buttonReplyDisabled || pinState.isReplyGenerating}>Generate Reply QR</Button>
            <Divider/>
            
            <Box
                fill={qrFillValue}
                padding="2rem"
                fullWidth 
                style="display:flex; justify-content: center"
            >
                <div id="qrcode2"></div>
            </Box>
            <Stack inline wrap="wrap" class="readout" orientation="horizontal" gap={2}>
                <Tag type="red" class="tag-label">Response</Tag>
                <TextArea
                    readonly
                    rows={1}
                    labelText=""
                    bind:value={replyValue}
                    />
            </Stack>
        </ColumnCard>
        
    </Row>

    <Row class="sub-row">
        <!-- Leave blank for space -->
    </Row>
</Grid>
