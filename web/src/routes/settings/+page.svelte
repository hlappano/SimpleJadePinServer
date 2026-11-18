<script lang='ts'>

    /*************************************************
     * Imports
     * ***********************************************/
    //Icons
    import {
        Settings,
        TrashCan,
        ServerProxy,
        ServerDns,
        IbmCloudDedicatedHost
    } from "carbon-icons-svelte";

    // Custom Components
    import {
        PageHeaderRow,
        ColumnCard
    } from '#lib'

    // Carbon UI Components
    import {
        Grid,
        Row,
        Stack,
        Tag,
        Divider,
        TextInput,
        TextArea,
        InlineNotification,
        Button,
        DataTable,
        TooltipDefinition,
        Modal
    } from 'carbon-components-svelte';

    // Svelte
    import {
        onMount
    } from 'svelte';

    // Javascript API
    import {
        getApiUrl
    } from '#lib/utils/jade-proto.js';

    /*************************************************
     * Data Members
     * ***********************************************/

    // Host Header
    const hostsHeader = [
        { key: "host", value: "Allowed Hosts" },
        { key: "type", value: "Type" },
        { key: "actions", empty: true, value: "Actions" }
    ];

    // Port Header
    const portsHeader = [
        { key: "port", value: "Allowed Ports" },
        { key: "type", value: "Type" },
        { key: "actions", empty: true, value: "Actions" }
    ];

    // Host Rows State
    let hostsRows = $state([]);

    // Port Rows State
    let portsRows = $state([]);

    // Current State of settings
    let currentState: {
        data_dir: string,
        keys_created_this_run: boolean,
        migrated_from: string | null,
        pin_records: number,
        pins_dir: string,
        public_key: string,
        server_keys_dir: string
    } = $state({
        'data_dir': "",
        'keys_created_this_run': false,
        'migrated_from': null,
        'pin_records': 0,
        'pins_dir' : "",
        'public_key': "",
        'server_keys_dir': ""
    });

    // Host Alert Notification State
    let hostAlertState: {
        active: boolean,
        kind: "error" | "info" | "info-square" | "success" | "warning" |"warning-alt"
        title: string,
        subtitle: string,
        hostName: string,
    } = $state({
        'active': false,
        'kind': "info",
        'title': "",
        'subtitle': "",
        'hostName': ""
    });

    // Port Alert Notification State
    let portAlertState: {
        active: boolean,
        kind: "error" | "info" | "info-square" | "success" | "warning" |"warning-alt"
        title: string,
        subtitle: string,
        portNumber: number | null
    } = $state({
        'active': false,
        'kind': "info",
        'title': "",
        'subtitle': "",
        'portNumber': null
    });

    // Modal Pop-up State
    let modalState: {
        active: boolean,
        isHost: boolean,
        portOrHost: string,
        alert: string
    } = $state({
        'active': false,
        'isHost': false,
        'portOrHost': "",
        'alert': ""
    });

    // Loading state - ensures the proper fetches take place before loading page
    let loading = $state(true);

    /**
     * Notification Type
     */
    type NotificationType = "error" | "info" | "info-square" | "success" | "warning" | "warning-alt";


    /*************************************************
     * Functions
     * ***********************************************/

    /**
     * Shows an alert notification on the host.
     */
    function hostAlertNotification(kind:NotificationType, title:string, subtitle:string)
    {
        hostAlertState.active = true;
        hostAlertState.kind = kind;
        hostAlertState.title = title;
        hostAlertState.subtitle = subtitle;
    }
    
    /**
     * Shows an alert notification on the port.
     */
    function portAlertNotification(kind:NotificationType, title:string, subtitle:string)
    {
        portAlertState.active = true;
        portAlertState.kind = kind;
        portAlertState.title = title;
        portAlertState.subtitle = subtitle;
    }

    /**
     * Fetches Allowed Hosts with Type
     */
    async function fetchAllowedHosts_type() {
        const targetUrl = getApiUrl('/get_allowed_hosts_type');
        try {
            const response = await fetch(targetUrl);
            if (response.ok) {
                const data = await response.json();
                hostsRows = data.allowed_hosts;
            }
        }
        catch (error) {
            console.error("Feaild to fetch allowed hosts:", error);
        }
    }

    /**
     * Fetches Allowed Ports with Type
     */
    async function fetchAllowedPorts_type() {
        const targetUrl = getApiUrl('/get_allowed_ports_type');
        try {
            const response = await fetch(targetUrl);
            if (response.ok) {
                const data = await response.json();
                portsRows = data.allowed_ports;
            }
        }
        catch (error) {
            console.error("Feaild to fetch allowed hosts:", error);
        }
    }

    /**
     * Fetches current state of settings
     */
    async function fetchCurrentState() {
        const targetUrl = getApiUrl('/get_current_state');
        try {
            const response = await fetch(targetUrl);
            if (response.ok) {
                const data = await response.json();
                currentState = data.data;
            }
        }
        catch(error)
        {
            console.error("Failed to fetch current state:" , error);
        }
    }

    /**
     * Check Host Name as valid
     * @param hostname - string of the hostname
     */
    function checkHostName(hostname:string)
    {
        const hostnameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        
        if (!hostname || !hostnameRegex.test(hostname))
            return false;

        return true;
    }

    /**
     * Check Port Number as valid
     * @param port
     */
    function checkPortNumber(port:string)
    {
        const num = Number(port);
        // Check if it's an integer, not NaN, and falls within the valid port range (1 - 65535)
        if (!Number.isInteger(num) || num < 1 || num > 65535)
            return false;

        return true;
    }

    /**
     * Add New Host Event
     */
    async function onAddNewHost()
    {
        var HostName = hostAlertState.hostName;
        
        if (! checkHostName(HostName)) {
            // Handle invalid hostname (e.g., show an error toast or notification)
            hostAlertNotification(
                "error",
                "Error: Hostname is Invalid.",
                "Please enter a valid hostname."
            );
            return;
        }

        const targetUrl = getApiUrl('/add_host');
        try {
            var payload = { host: HostName };
            const response = await fetch(targetUrl, 
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                }
            );

            const data = await response.json();
            if (response.ok) {

                await fetchAllowedHosts_type();
                hostAlertNotification(
                    "success",
                    "Successfully Added: You must restart the system for it to take full effect.",
                    ""
                );

                hostAlertState.hostName = "";
            }
            else {
                hostAlertNotification(
                    "error",
                    data.error,
                    ""
                );
            }
        } catch (error: unknown)
        {
            const message = error instanceof Error ? error.message : "An unknown error occurred";
            hostAlertNotification(
                "error",
                "Failed to update host",
                message
            );
        }
    }

    /**
     * Remove Host Event
     * @param HostName
     */
    async function onRemoveHost(HostName:string = "")
    {
        if (HostName === "" ) {
            HostName = hostAlertState.hostName;
        }
        if (! checkHostName(HostName)) {
            // Handle invalid hostname (e.g., show an error toast or notification)
            hostAlertNotification(
                "error",
                "Error: Hostname is Invalid.",
                "Please enter a valid hostname."
            );
            return;
        }

        const targetUrl = getApiUrl('/remove_host');
        try {
            var payload = { host: HostName };
            const response = await fetch(targetUrl, 
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                }
            );

            var data = await response.json();
            if (response.ok) {

                await fetchAllowedHosts_type();
                hostAlertNotification(
                    "success",
                    "Successfully Removed: You must restart the system for it to take full effect.",
                    ""
                );

                hostAlertState.hostName = "";
            }
            else {
                hostAlertNotification(
                    "error",
                    data.error,
                    ""
                );
            }
        } catch (error: unknown)
        {
            const message = error instanceof Error ? error.message : "An unknown error occurred";
            hostAlertNotification(
                "error",
                "Failed to update host",
                message
            );
        }
    }

    /**
     * Add New Port Event
     */
    async function onAddNewPort()
    {
        var PortNumber = portAlertState.portNumber;
        
        if (! checkPortNumber(PortNumber)) {
            // Handle invalid hostname (e.g., show an error toast or notification)
            portAlertNotification(
                "error",
                "Error: Port Number is Invalid.",
                "Please enter a valid port number."
            );
            return;
        }

        const targetUrl = getApiUrl('/add_port');
        try {
            var payload = { port: PortNumber };
            const response = await fetch(targetUrl, 
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                }
            );

            const data = await response.json();
            if (response.ok) {

                await fetchAllowedPorts_type();
                portAlertNotification(
                    "success",
                    "Successfully Added: You must restart the system for it to take full effect.",
                    ""
                );
                portAlertState.portNumber = null;
            }
            else {
                portAlertNotification(
                    "error",
                    data.error,
                    ""
                );
            }
        } catch (error: unknown)
        {
            const message = error instanceof Error ? error.message : "An unknown error occurred";
            portAlertNotification(
                "error",
                "Failed to update port",
                message
            );
        }
    }

    /**
     * Remove Port event
     * @param PortNumberStr
     */
    async function onRemovePort(PortNumberStr:string = "")
    {
        var PortNumber = portAlertState.portNumber;
        if (PortNumberStr.trim() !== "") {
            PortNumber = PortNumberStr;
        }

        if (! checkPortNumber(PortNumber)) {
            // Handle invalid hostname (e.g., show an error toast or notification)
            portAlertNotification(
                "error",
                "Error: Port Number is Invalid.",
                "Please enter a valid port number."
            );
            return;
        }

        const targetUrl = getApiUrl('/remove_port');
        try {
            var payload = { port: PortNumber };
            const response = await fetch(targetUrl, 
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                }
            );

            var data = await response.json();
            if (response.ok) {

                await fetchAllowedPorts_type();
                portAlertNotification(
                    "success",
                    "Successfully Removed: You must restart the system for it to take full effect.",
                    ""
                );
                portAlertState.portNumber = null;
            }
            else {
                portAlertNotification(
                    "error",
                    data.error,
                    ""
                );
            }
        } catch (error: unknown)
        {
            const message = error instanceof Error ? error.message : "An unknown error occurred";
            portAlertNotification(
                "error",
                "Failed to update port",
                message
            );
        }
    }

    /**
     * Get Host/Port's tooltip
     * @param value - type of value ('local', 'proxy', or 'custom')
     * @param type - host or port
     */
    function getHostPortTooltip(value: string, type: string) : string {

        if (value === "local") return `Local ${type} (Can not change)`;
        if (value === "proxy") return `Proxy ${type} (Env Variable)`;
        return `Custom ${type}`;
    }

    /**
     * Trash Button Clicked Event
     * Remove the Host/Port name that is linked to this button
     * @param isHost - is host or port
     * @param portOrHost - string of the port or host
     */
    function onTrashButtonClicked(isHost: boolean, portOrHost: string)
    {
        modalState.isHost = isHost
        modalState.portOrHost = portOrHost;
        modalState.active = true
    };

    /**
     * Modal Delete Clicked Event
     * Finalizes and calls the remove host/port
     */
    function onModalDeleteClicked()
    {
        modalState.active = false;
        if (modalState.isHost) {
            onRemoveHost(modalState.portOrHost);
        }
        else {
            onRemovePort(modalState.portOrHost);
        }
    }

    /**
     * Svelte's onMount override
    */
    onMount(async () => {

        // Get allowed hosts list
        await fetchAllowedHosts_type();

        // Get allowed ports list
        await fetchAllowedPorts_type();

        // Fetch the Current State
        await fetchCurrentState();

        loading = false;
    });

</script>
<style>
    .trash-btn {
        display: flex;
        position: relative;
        left: 1rem;
    }

    .flex-label {
        display: flex;
        align-items: center;
        gap: 20px;
    }
</style>

<Modal
    danger
    bind:open={modalState.active}
    modalHeading={ modalState.isHost ? "Delete Host" : "Delete Port" }
    primaryButtonText="Delete"
    secondaryButtonText="Cancel"
    on:open
    on:close
    on:submit={() => onModalDeleteClicked() }
    on:click:button--secondary={() => modalState.active = false }
>
    <p>WARNING: This is a permanent action.</p>
    <br/>
    <p>Removing '{modalState.portOrHost}' from allowed list. </p>
</Modal>

{#if !loading }
<Grid fullWidth>
    <PageHeaderRow
        title="Settings"
        icon={Settings}
    />
    <Row class="sub-row">
        <ColumnCard
            title="Hosts Allowed"
            subtitle="Allowed for CORS and Security Layer"
        >
        <Stack orientation="vertical" gap={5}>
            <InlineNotification
                class="card-note"
                hideCloseButton
                kind="warning"
                title="WARNING: Security Change"
                subtitle="Adding a new host means it will allow this host under CORS and the Backend Server's Auth Guard."
                />
            <DataTable 
                headers={hostsHeader}
                rows={hostsRows}
                zebra
                >
                <svelte:fragment slot="cell" let:row let:cell>
                    {#if cell.key === "type"}
                        {#if cell.value === "proxy"}
                            <TooltipDefinition
                                tooltipText={getHostPortTooltip(cell.value, "Host")}
                                portalTooltip={true}
                                >
                                <div class="flex-label">
                                    <span>Proxy</span>
                                    <ServerProxy/>
                                </div>
                            </TooltipDefinition>
                        {:else if cell.value === "local"}
                            <TooltipDefinition
                                tooltipText={getHostPortTooltip(cell.value, "Host")}
                                portalTooltip={true}
                            >
                                <div class="flex-label">
                                    <span>Local</span>
                                    <IbmCloudDedicatedHost/>
                                </div>
                            </TooltipDefinition>
                        {:else if cell.value === "custom"}
                            <TooltipDefinition
                                tooltipText={getHostPortTooltip(cell.value, "Host")}
                                portalTooltip={true}
                            >
                                <div class="flex-label" style="gap: 8px">
                                    <span>Custom</span>
                                    <ServerDns/>
                                </div>
                            </TooltipDefinition>
                        {:else}
                            <TooltipDefinition
                                tooltipText={getHostPortTooltip(cell.value, "Host")}
                                portalTooltip={true}
                                >
                            {cell.value}
                            </TooltipDefinition>
                        {/if}
                    {:else if cell.key === "actions" && row.type == "custom"}
                        
                        <span class="trash-btn">
                            <Button
                                size="small"
                                kind="danger-tertiary"
                                iconDescription="Delete"
                                icon={TrashCan}
                                tooltipPosition="top"
                                on:click={() => onTrashButtonClicked(true, row.host)}
                            /></span>
                        
                    {:else}
                        {cell.value}
                    {/if}
                </svelte:fragment>
            </DataTable>
            <Divider/>
            {#if hostAlertState.active }
            <InlineNotification
                class="card-note"
                bind:open={hostAlertState.active}
                kind={hostAlertState.kind}
                title={hostAlertState.title}
                subtitle={hostAlertState.subtitle}
                />
            {/if}
            <Stack wrap="wrap" inline orientation="horizontal" gap={3}>
                <TextInput
                    labelText="Host Name:"
                    bind:value={hostAlertState.hostName}
                />
                <Button
                    class="jade-button"
                    size="small"
                    on:click={() => onAddNewHost() }
                    >Add New Host</Button>

            </Stack>
        </Stack>
        </ColumnCard>
    </Row>
    <Row class="sub-row">
        <ColumnCard
            title="Ports Allowed"
            subtitle="Allowed for CORS and Security Layer"
        >
            <Stack orientation="vertical" gap={5}>
                <InlineNotification
                        class="card-note"
                        hideCloseButton
                        kind="warning"
                        title="WARNING: Security Change"
                        subtitle="Adding a new port number means it will allow this port under CORS and the Backend Server's Auth Guard."
                        />
                <DataTable
                    headers={portsHeader}
                    rows={portsRows}
                    zebra
                    >
                    <svelte:fragment slot="cell" let:row let:cell>
                        {#if cell.key === "type"}
                            {#if cell.value === "proxy"}
                                <TooltipDefinition
                                    tooltipText={getHostPortTooltip(cell.value, "Port")}
                                    portalTooltip={true}
                                    >
                                    <div class="flex-label">
                                        <span>Proxy</span>
                                        <ServerProxy/>
                                    </div>
                                </TooltipDefinition>
                            {:else if cell.value === "local"}
                                <TooltipDefinition
                                    tooltipText={getHostPortTooltip(cell.value, "Port")}
                                    portalTooltip={true}
                                >
                                    <div class="flex-label">
                                        <span>Local</span>
                                        <IbmCloudDedicatedHost/>
                                    </div>
                                </TooltipDefinition>
                            {:else if cell.value === "custom"}
                                <TooltipDefinition
                                    tooltipText={getHostPortTooltip(cell.value, "Port")}
                                    portalTooltip={true}
                                >
                                    <div class="flex-label" style="gap: 8px">
                                        <span>Custom</span>
                                        <ServerDns/>
                                    </div>
                                </TooltipDefinition>
                            {:else}
                                <TooltipDefinition
                                    tooltipText={getHostPortTooltip(cell.value, "Port")}
                                    portalTooltip={true}
                                    >
                                {cell.value}
                                </TooltipDefinition>
                            {/if}
                        {:else if cell.key === "actions" && row.type == "custom"}
                            <span class="trash-btn">
                                <Button
                                    size="small"
                                    kind="danger-tertiary"
                                    iconDescription="Delete"
                                    icon={TrashCan}
                                    tooltipPosition="top"
                                    on:click={() => { onTrashButtonClicked(false, row.port)}}
                                />
                            </span>
                        {:else}
                            {cell.value}
                        {/if}
                    </svelte:fragment>
                </DataTable>
                <Divider/>
                {#if portAlertState.active }
                <InlineNotification
                    class="card-note"
                    kind={portAlertState.kind}
                    title={portAlertState.title}
                    subtitle={portAlertState.subtitle}
                    />
                {/if}
                <Stack wrap="wrap" inline orientation="horizontal" gap={3}>
                    <TextInput
                        labelText="Port Number:"
                        bind:value={portAlertState.portNumber}
                    />
                    <Button
                        class="jade-button"
                        size="small"
                        on:click={() => onAddNewPort() }
                        >Add New Port</Button>
                </Stack>
            </Stack>
        </ColumnCard>
    </Row>
    <Row class="sub-row">
        <ColumnCard
            title="Readonly Settings"
        >
            <Stack orientation="vertical" gap={3}>
            <InlineNotification
                        class="card-note"
                        hideCloseButton
                        kind="info-square"
                        role="alert"
                        title="INFO:"
                        subtitle="Ensure you have a proper backup of your data directory and keep it safe. Unauthorized access could allow unlimited PIN attempts. Note that while Linux data directories are protected with root permissions, Windows may require extra precautions."
                        />
                <Stack wrap="wrap" inline class="readout" orientation="horizontal" gap={2}>
                    <TooltipDefinition
                        tooltipText="The protected data directory with all settings. Ensure a cold storage backup."
                        portalTooltip={true}
                    >
                        <Tag type="red" class="tag-label">
                            Data Dir:
                        </Tag>
                    </TooltipDefinition>
                    <TextArea
                        readonly
                        rows={1}
                        labelText=""
                        bind:value={currentState.data_dir}
                        />
                </Stack>
                <Stack wrap="wrap" inline class="readout" orientation="horizontal" gap={2}>
                    <TooltipDefinition
                        tooltipText="Public Hex Key for encryption Jade PIN."
                        portalTooltip={true}
                    >
                        <Tag type="red" class="tag-label">Server Public Key:</Tag>
                    </TooltipDefinition>
                    <TextArea
                        readonly
                        rows={1}
                        labelText=""
                        bind:value={currentState.public_key}
                        />
                </Stack>
                <Stack wrap="wrap" inline class="readout" orientation="horizontal" gap={2}>
                    <TooltipDefinition
                        tooltipText="Number of stored PIN records. One per wallet."
                        portalTooltip={true}
                    >
                        <Tag type="red" class="tag-label">Stored PIN Records:</Tag>
                    </TooltipDefinition>
                    <TextInput
                        readonly
                        labelText=""
                        bind:value={currentState.pin_records}
                        />
                </Stack>
                
            </Stack>
        </ColumnCard>
    </Row>
    <Row class="sub-row">
        <!-- Leave blank for space -->
    </Row>
</Grid>
{/if}