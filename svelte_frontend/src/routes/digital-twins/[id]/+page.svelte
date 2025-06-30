<script lang="ts">
  import { ArrowLeft } from 'lucide-svelte';
  import TabOmschrijving from '$lib/components/digitalTwinTabs/TabOmschrijving.svelte';
  import TabBasis from '$lib/components/digitalTwinTabs/TabBasis.svelte';
  import TabOndergrond from '$lib/components/digitalTwinTabs/TabOndergrond.svelte';
  import TabFeatureLagen from '$lib/components/digitalTwinTabs/TabFeatureLagen.svelte';
  import TabBookmarks from '$lib/components/digitalTwinTabs/TabBookmarks.svelte';
  import TabStories from '$lib/components/digitalTwinTabs/TabStories.svelte';
  import TabProjects from '$lib/components/digitalTwinTabs/TabProjects.svelte';

  let { data } = $props();

  let tabs = [
    { label: 'Omschrijving', component: TabOmschrijving },
    { label: 'Basis', component: TabBasis },
    { label: 'Ondergrond', component: TabOndergrond },
    { label: 'FeatureLagen', component: TabFeatureLagen },
    { label: 'Bookmarks', component: TabBookmarks },
    { label: 'Stories', component: TabStories },
    { label: 'Projects', component: TabProjects }
  ];

  let selectedIndex = $state(0);

	const SvelteComponent = $derived(tabs[selectedIndex].component);
</script>

<svelte:head>
	<title>Digital Twin Configuratie - Digital Twins Manager</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center gap-4">
		<a href="/digital-twins" class="btn btn-ghost btn-sm">
			<ArrowLeft class="w-4 h-4" />
			Terug
		</a>
		<div>
			<h1 class="text-3xl font-bold">Digital Twin Configuratie</h1>
			<p class="text-base-content/70 mt-2">
				{data.digitalTwin?.title || `Digital twin ID: ${data.id}`}
			</p>
		</div>
	</div>

	<!-- Tab headers -->
	<div class="tabs tabs-lifted mb-4" role="tablist">
	  {#each tabs as tab, i}
	    <button
	      type="button"
	      class="tab tab-bordered {selectedIndex === i ? 'tab-active' : ''}"
	      role="tab"
	      tabindex={selectedIndex === i ? 0 : -1}
	      aria-selected={selectedIndex === i}
	      onclick={() => selectedIndex = i}
	      onkeydown={(e) => {
	        if (e.key === 'Enter' || e.key === ' ') selectedIndex = i;
	      }}
	    >
	      {tab.label}
	    </button>
	  {/each}
	</div>

	<!-- Tab content -->
	<div class="bg-base-100 rounded-lg shadow-xl p-6">
		<SvelteComponent digitalTwin={data.digitalTwin} digitalTwinId={data.id} />
	</div>
</div>