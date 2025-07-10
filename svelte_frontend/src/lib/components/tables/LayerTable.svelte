<script lang="ts">
  import { Database } from 'lucide-svelte';
  import LayerModal from '$lib/components/LayerModal.svelte';
  import type { Layer } from '$lib/types/layer';
  import { deleteLayer } from '$lib/api';

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
      layers = layers.filter((layer) => layer.id !== updatedLayer.id);
      return;
    }

    // Otherwise, update the layer
    const idx = layers.findIndex((layer) => layer.id === updatedLayer.id);
    if (idx > -1) {
      layers[idx] = updatedLayer;
      layers = [...layers];
    } else {
      layers = [...layers, updatedLayer];
    }
  }

  async function handleDelete(layerId: number) {
    if (confirm('Weet je zeker dat je deze layer wilt verwijderen?')) {
      try {
        await deleteLayer(layerId);
        layers = layers.filter((layer) => layer.id !== layerId);
      } catch (err) {
        alert('Verwijderen mislukt. Controleer de server.');
        console.error(err);
      }
    }
  }
</script>

<LayerModal bind:this={modalComponent} on:updated={handleUpdated} />

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
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
              <td class="relative">
                <details class="dropdown dropdown-end">
                  <summary class="btn btn-sm btn-ghost">
                    Opties
                    <svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19 9l-7 7-7-7"
                      ></path>
                    </svg>
                  </summary>
                  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
                    <li>
                      <button on:click={() => handleOpenModal(layer)} class="flex items-center gap-2">
                        Bewerken
                      </button>
                    </li>
                    <li>
                      <button on:click={() => handleDelete(layer.id)} class="flex items-center gap-2 text-error">
                        Verwijderen
                      </button>
                    </li>
                  </ul>
                </details>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>

      <!-- Add padding at the bottom for dropdown space -->
      <!-- Temp fix till dropdown fix for absolute position -->
      <div class="h-32"></div>

      {#if layers.length === 0}
        <div class="py-12 text-center">
          <Database class="mx-auto h-12 w-12 opacity-50" />
          <h3 class="mt-2 text-lg font-medium">Geen layers</h3>
          <p class="mt-1 opacity-70">Er zijn nog geen layers beschikbaar.</p>
        </div>
      {/if}
    </div>
  </div>
</div>
