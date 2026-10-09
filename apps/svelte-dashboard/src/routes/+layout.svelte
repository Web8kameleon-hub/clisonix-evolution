<script lang="ts">
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<title>ASI Terminal | Clisonix</title>
	<meta name="description" content="Clisonix ASI Terminal - Industrial Intelligence" />
</svelte:head>

<!-- BETA BANNER - Ruajtur për aktivitet masiv në të ardhmen
<div class="beta-banner">
	<strong>BETA</strong> — Platform under development. All features coming soon. Thank you for your patience.
</div>
-->

{@render children()}
