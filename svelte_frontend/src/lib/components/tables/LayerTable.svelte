<script lang="ts">
	import { Database } from 'lucide-svelte';
	import LayerModal from '$lib/components/LayerModal.svelte';
	import type { Layer } from '$lib/types/layer';

	export let layers: Layer[] = [];
	export let isBackgroundPage: boolean = false;

	let modalComponent: any;

	function handleOpenModal(layer: Layer) {
		modalComponent.showModal(layer);
	}

	function truncate(str: string, length = 30) {
		return str.length > length ? str.slice(0, length) + '…' : str;
	}

	function handleUpdated(event: CustomEvent<Layer>) {
		const updatedLayer = event.detail;

		// Remove updated layer from table if it changed isBackground status
		if (updatedLayer.isBackground !== isBackgroundPage) {
			layers = layers.filter(layer => layer.id !== updatedLayer.id);
			return;
		}

		// Otherwise, update the layer
		const idx = layers.findIndex(layer => layer.id === updatedLayer.id);
		if (idx > -1) {
			layers[idx] = updatedLayer;
			layers = [...layers];
		} else {
			layers = [...layers, updatedLayer];
		}
	}
</script>


<LayerModal bind:this={modalComponent} on:updated={handleUpdated} />

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table table-xs table-pin-rows">
        <thead>
          <tr>
            <th class="bg-base-200 sticky font-bold">Titel</th>
            <th class="bg-base-200 font-bold">Type</th>
            <th class="bg-base-200 font-bold">Url</th>
            <th class="bg-base-200 font-bold">Feature Name</th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each layers as layer}
            <tr class="hover">
              <td class="text-sm font-bold">{layer.title || '-'}</td>
              <td class="text-sm">{layer.type || '-'}</td>
              <td class="text-sm">{truncate(layer.url, 30) || '-'}</td>
              <td class="text-sm">{layer.featureName || '-'}</td>
              <td>
                <button class="btn btn-sm" onclick={() => handleOpenModal(layer)}>
                  Opties
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
	</table>

      {#if layers.length === 0}
        <div class="text-center py-12">
          <Database class="mx-auto h-12 w-12 opacity-50" />
          <h3 class="mt-2 text-lg font-medium">Geen layers</h3>
          <p class="mt-1 opacity-70">Er zijn nog geen layers beschikbaar.</p>
        </div>
      {/if}
    </div>
  </div>
</div>
