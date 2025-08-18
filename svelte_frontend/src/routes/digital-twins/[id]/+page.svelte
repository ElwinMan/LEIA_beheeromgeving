<script lang="ts">
  import TabOmschrijving from '$lib/components/digitalTwinTabs/TabOmschrijving.svelte';
  import TabBasis from '$lib/components/digitalTwinTabs/TabBasis.svelte';
  import TabOndergrond from '$lib/components/digitalTwinTabs/TabOndergrond.svelte';
  import TabFeatureLagen from '$lib/components/digitalTwinTabs/TabFeatureLagen.svelte';
  import TabBookmarks from '$lib/components/digitalTwinTabs/TabBookmarks.svelte';
  import TabStories from '$lib/components/digitalTwinTabs/TabStories.svelte';
  import TabProjects from '$lib/components/digitalTwinTabs/TabProjects.svelte';
  import TabTerrainProvider from '$lib/components/digitalTwinTabs/TabTerrainProvider.svelte';

  import { digitalTwinExport } from '$lib/api';

  let { data } = $props();

  let tabs = [
    { label: 'Omschrijving', component: TabOmschrijving },
    { label: 'Basis', component: TabBasis },
    { label: 'Ondergrond', component: TabOndergrond },
    { label: 'FeatureLagen', component: TabFeatureLagen },
    { label: 'TerrainProviders', component: TabTerrainProvider },
    { label: 'Bookmarks', component: TabBookmarks },
    { label: 'Stories', component: TabStories },
    { label: 'Projects', component: TabProjects }
  ];

  let selectedIndex = $state(0);

  const SvelteComponent = $derived(tabs[selectedIndex].component);

  const downloadUrl = digitalTwinExport(data.id);
</script>

<svelte:head>
  <title>Digital Twin Configuratie - Digital Twins Manager</title>
</svelte:head>

<div class="space-y-6">
  <div class="flex items-center gap-4">
    <a href="/digital-twins" class="btn btn-ghost btn-sm">
      <img src="/icons/arrow-left.svg" alt="Ga terug" class="h-4 w-4" />
      Terug
    </a>
    <div>
      <h1 class="text-3xl font-bold">Digital Twin Configuratie</h1>
      <p class="text-base-content/70 mt-2">
        {data.digitalTwin?.title || `Digital twin ID: ${data.id}`}
      </p>
    </div>
    <a
      href={downloadUrl}
      class="btn btn-primary flex items-center gap-2"
      download
    >
      <img src="/icons/download.svg" alt="Download" class="w-5 h-5" />
      Download export
    </a>
  </div>

  <!-- Tab headers -->
  <div class="tabs tabs-border mb-4" role="tablist">
    {#each tabs as tab, i}
      <input
        type="radio"
        name="main_tabs"
        class="tab"
        aria-label={tab.label}
        checked={selectedIndex === i}
        onchange={() => selectedIndex = i}
      />
      <div class="tab-content border-base-300 bg-base-100 p-6 shadow-xl">
        <SvelteComponent digitalTwin={data.digitalTwin} digitalTwinId={data.id} />
      </div>
    {/each}
  </div>
</div>
