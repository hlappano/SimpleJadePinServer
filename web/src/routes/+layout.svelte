<script lang="ts">
	import favicon from '#lib/assets/favicon.jpeg';
	import "carbon-components-svelte/css/g100.css";
	import type { LayoutProps } from './$types';
	// Carbon Components
	import {
		Header,
		SideNav,
		SideNavItems,
		SideNavLink,
		Content,
		Grid,
		Row,
		Column,
		Heading,
		Stack,
		Divider,
	} from "carbon-components-svelte";
	// Icons
	import Icon from '#lib/components/Icon.svelte';
	import logo from '#lib/assets/logo.svg';

	let isSideNavOpen = $state(false);
	let { children }: LayoutProps = $props();

	let finishedCheck = $state(true);

</script>

<style>

	:root {
	--crimson: #C41E3A;
	--crimson-lt: #E8687E;
	--crimson-dk: #9B1530;
	--jade-dk: #061310;
	--jade-ldk: #0f241e;
	--jade-md: #44a78c;
	--ink: #f8fafc;
	--muted: rgba(255, 255, 255, 0.55);
	--faint: rgba(255, 255, 255, 0.38);
	--line: rgba(255, 255, 255, 0.08);
	--ok: #2ecc71;
	--warn: #f0a020;
	--sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
		"Helvetica Neue", Arial, sans-serif;
	--serif: "Playfair Display", Georgia, "Times New Roman", serif;
	--mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas,
		"Liberation Mono", monospace;
	}

	footer {
		display: flex;
		position:fixed;
		bottom: 0;
		width: 100%;
		z-index: 100;
		justify-content: center;
		padding: 1rem;
		background: var(--jade-dk);
		color: #fff;
		text-align: center;
	}

	:global(.maind) {
		background-image: url('/background.svg');
		z-index: -1;
		margin: 0;
		font-family: var(--sans);
		font-size: 15px;
		line-height: 1.6;
		-webkit-font-smoothing: antialiased;
		display: flex;
		flex-direction: column;
	}

	:global(.bx--header) {
		background-color: var(--jade-dk)
	}

	:global(body) {
		margin: 0;
		background: var(--jade-ldk);
		background-image: url("/background.svg");
		background-size: cover;
		background-attachment: fixed;
		color: var(--ink);
		font-family: var(--sans);
		font-size: 15px;
		line-height: 1.6;
		-webkit-font-smoothing: antialiased;
		display: flex;
		flex-direction: column;
	}

	:global(.page-icon-txt) {
		font-family: "rigid-square", sans-serif;;
		font-size: 1.6rem;
	}

	:global(.jade-button) {
		font-family: inherit;
		font-size: 14px;
		font-weight: 600;
		color: #fff;
		background-color: var(--jade-md);
		border: none;
		border-radius: 8px;
		padding: 11px 20px;
		cursor: pointer;
		transition: background 0.15s ease, opacity 0.15s ease;
	}

	:global(.danger-button) {
		background-color: red;
	}

	:global(.jade-button:hover:not(:disabled)) { background: var(--jade-ldk);}

	:global(.jade-button:disabled) {
	background: var(--crimson-dk);
	color: var(--faint);
	cursor: not-allowed;
	}

	:global(.jade-button.ghost) {
	background: transparent;
	border: 1px solid var(--line);
	color: var(--muted);
	font-weight: 500;
	padding: 9px 16px;
	}

	:global(.jade-button.ghost:hover:not(:disabled)) {
	background: var(--jade-md);
	color: var(--ink);
	}

	:global(.bx--tile) {
		background-color: var(--jade-dk);
	}

	:global(.header-row)
	{
		display: flex;
		justify-content: center;
	}
	

	:global(.sub-row)
	{
		display: flex;
		justify-content: center;
		padding-top: 50px;
		padding-bottom: 25px;
	}

	:global(.steps)
	{
		padding-left: 2.5rem;
		padding: 2rem;
		padding-top: 0;
		/* display: flex;
		width: 100%;
		flex-wrap: wrap; */
	}

	:global(.step-num)
	{
		height: 1rem;
	}

	:global(.readout) {
		font-family: var(--mono);
		font-size: 12px;
		color: var(--muted);
		background: var(--jade-ldk);
		border: 1px solid var(--line);
		border-radius: 8px;
		padding: 12px 14px;
		margin-top: 16px;
		word-break: break-all;
		max-height: 130px;
		overflow-y: auto;
		}

	:global(.readout .tag ){
		display: inline-block;
		font-family: var(--sans);
		font-weight: 700;
		font-size: 11px;
		letter-spacing: 0.5px;
		text-transform: uppercase;
		color: var(--crimson-lt);
		margin-bottom: 4px;
		}

	:global(.bx--progress-bar__bar) {
		color: var(--jade-md);
	}

	:global(.card-note)
	{
		max-width: 100%;
		width: auto !important;
		display: flex !important;
	}

	:global(.bx--box-fill-layer-accent)
	{
		background-color: var(--jade-ldk);
	}
	
	:global(.tag-label) {
		width: 10rem;
		height: 2rem;
	}

	:global(.bx--stack-wrap) {
		display: flex;
		width: 100%;
		flex-wrap: wrap;
	}

	:global(.bx--list__item) {
		overflow-wrap: anywhere;
	}

	
</style>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<Header bind:isSideNavOpen  platformName="" persistentHamburgerMenu={true} expansionBreakpoint={Number.POSITIVE_INFINITY} >
	<Stack orientation="horizontal" gap={3}>
		<Icon src={logo} width="5rem"/>
		<Divider orientation="vertical" />
		<Heading type="heading-02">Jade PIN Server</Heading>
	</Stack>
</Header>

<SideNav bind:isOpen={isSideNavOpen} class="side-nav"  expansionBreakpoint={Number.POSITIVE_INFINITY} style="background-color: var(--jade-dk)">

	<SideNavItems>
		<SideNavLink href="/home" text="Home" on:click={() => isSideNavOpen = false}></SideNavLink>
		<SideNavLink href="/oracle" text="Oracle" on:click={() => isSideNavOpen = false}></SideNavLink>
		<SideNavLink href="/qr_pin" text="QR PIN" on:click={() => isSideNavOpen = false}></SideNavLink>
		<SideNavLink href="/settings" text="Settings" on:click={() => isSideNavOpen = false}></SideNavLink>
	</SideNavItems>
</SideNav>

{#if finishedCheck}
<Content class="main">
	{@render children()}
</Content>
{/if}

<!-- Footer -->
	<footer>
		<Grid narrow>
			<Row>
				<Column>
					<a href="https://raw.githubusercontent.com/hlappano/SimpleJadePinServer/refs/heads/main/LICENSE" title="Apache 2.0" target="_blank" rel="noopener noreferrer">License</a>
				</Column>
				<Column>
					&bull;
				</Column>
				<Column>
					<a href="https://hlappano.github.io/" target="_blank" rel="noopener noreferrer">Author</a>
				</Column>
				<Column>
					&bull;
				</Column>
				<Column>
					<a href="https://github.com/hlappano/SimpleJadePinServer/issues" target="_blank" rel="noopener noreferrer">Issues</a>
				</Column>
			</Row>
		</Grid>
	</footer>

