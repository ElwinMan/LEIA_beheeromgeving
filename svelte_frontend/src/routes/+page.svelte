<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	
	onMount(() => {
		goto('/digital-twins', { replaceState: true });
	});
</script>

<svelte:head>
	<title>LEIA Beheeromgeving</title>
</svelte:head>

<!-- Fallback content in case JavaScript is disabled -->
<div class="flex items-center justify-center min-h-screen">
	<div class="text-center">
		<span class="loading loading-spinner loading-lg"></span>
		<p class="mt-4">Redirecting to Digital Twins...</p>
		<p class="mt-2 text-sm opacity-70">
			<a href="/digital-twins" class="link">Click here if you are not redirected automatically</a>
		</p>
	</div>
</div>
