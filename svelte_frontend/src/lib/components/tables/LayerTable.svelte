<script lang="ts">
  import LayerModal from '$lib/components/modals/UpdateLayerModal.svelte';
  import type { Layer } from '$lib/types/layer';
  import { deleteLayer } from '$lib/api';
  import CreateLayerModal from '$lib/components/modals/CreateLayerModal.svelte';
  import { createEventDispatcher } from 'svelte';
  import { portal } from 'svelte-portal';
  import { tick } from 'svelte';

  const dispatch = createEventDispatcher();

  let { layers = [], isBackgroundPage = false } = $props();

  let modalComponent: any;
  let createModal: any;

  let openIndex = $state<number | null>(null);
  let summaryRefs = $state<Array<HTMLElement | null>>([]);
  let dropdownLeft = $state(0);
  let dropdownTop = $state(0);

  function handleOpenModal(layer: Layer) {
    modalComponent.showModal(layer);
  }

  function truncate(str: string, length = 30) {
    return str.length > length ? str.slice(0, length) + '…' : str;
  }

  function handleCreated(event: CustomEvent<Layer>) {
    const created = event.detail;
    if (created.isBackground === isBackgroundPage) {
      layers = [...layers, created];
    }
  }

  function handleUpdated(event: CustomEvent<Layer>) {
    const updatedLayer = event.detail;
    const idx = layers.findIndex((layer) => layer.id === updatedLayer.id);
    let newLayers = [...layers];
    if (idx > -1) {
      newLayers[idx] = updatedLayer;
    }
    dispatch('updateLayers', newLayers);
  }

  async function handleDelete(layerId: number) {
    if (confirm('Weet je zeker dat je deze layer wilt verwijderen?')) {
      try {
        await deleteLayer(layerId);
        const newLayers = layers.filter((layer) => layer.id !== layerId);
        dispatch('updateLayers', newLayers);
      } catch (err) {
        alert('Verwijderen mislukt. Controleer de server.');
        console.error(err);
      }
    }
  }

  function handleSummaryClick(idx: number) {
    if (openIndex === idx) {
      openIndex = null;
      window.removeEventListener('mousedown', handleClickOutside);
      return;
    }
    openIndex = idx;
    tick().then(() => {
      const ref = summaryRefs[idx];
      if (ref) {
        const rect = ref.getBoundingClientRect();
        dropdownLeft = rect.right - 208; // 208px for w-52
        dropdownTop = rect.bottom;
        window.addEventListener('mousedown', handleClickOutside);
      }
    });
  }

  function handleClickOutside(event: MouseEvent) {
    if (!event.target || !(event.target as HTMLElement).closest('.dropdown-content')) {
      openIndex = null;
      window.removeEventListener('mousedown', handleClickOutside);
    }
  }
</script>

<CreateLayerModal bind:this={createModal} on:created={handleCreated} />
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
          {#each layers as layer, idx}
            <tr class="hover">
              <td class="text-sm font-bold">{layer.title || '-'}</td>
              <td class="text-sm">{layer.type || '-'}</td>
              <td class="text-sm">{truncate(layer.url, 30) || '-'}</td>
              <td class="text-sm">{layer.featureName || '-'}</td>
              <td>
                <div class="dropdown dropdown-end">
                  <button
                    bind:this={summaryRefs[idx]}
                    type="button"
                    class="btn btn-sm btn-ghost"
                    onclick={() => handleSummaryClick(idx)}
                  >
                    Opties
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </button>
                  {#if openIndex === idx}
                    <ul
                      use:portal={'body'}
                      class="dropdown-content menu bg-base-100 rounded-box z-[1000] w-52 p-2 shadow"
                      style="position: absolute; left: {dropdownLeft}px; top: {dropdownTop}px;"
                    >
                      <li>
                        <button onclick={() => { handleOpenModal(layer); openIndex = null; }} class="flex items-center gap-2">
                          Bewerken
                        </button>
                      </li>
                      <li>
                        <button onclick={() => { handleDelete(layer.id); openIndex = null; }} class="flex items-center gap-2 text-error">
                          Verwijderen
                        </button>
                      </li>
                    </ul>
                  {/if}
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>

      {#if layers.length === 0}
        <div class="py-12 text-center">
          <img src="/icons/database.svg" alt="Database" class="mx-auto h-12 w-12 opacity-50" />
          <h3 class="mt-2 text-lg font-medium">Geen layers</h3>
          <p class="mt-1 opacity-70">Er zijn nog geen layers beschikbaar.</p>
        </div>
      {/if}
    </div>
  </div>
</div>
