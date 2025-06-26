<script lang="ts">
	import '../app.css';
	import Navigation from '$lib/components/Navigation.svelte';
	
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();
</script>

<Navigation>
	{@render children?.()}
</Navigation>
