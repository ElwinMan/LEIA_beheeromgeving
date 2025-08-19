<script lang="ts">
  import LayerModal from '$lib/components/modals/UpdateLayerModal.svelte';
  import type { Layer } from '$lib/types/layer';
  import { deleteLayer, fetchLayersPaginated, fetchDigitalTwinsForLayer } from '$lib/api';
  import { createEventDispatcher } from 'svelte';
  import { portal } from 'svelte-portal';
  import { tick } from 'svelte';
  import ShowLayerUsageModal from '../modals/ShowLayerUsageModal.svelte';
  import TableControls from './TableControls.svelte';
  import SortableTableHeader from "$lib/components/tables/SortableTableHeader.svelte";

  const dispatch = createEventDispatcher();

  // Props from parent
  const { isBackgroundPage } = $props();

  let modalComponent: any;
  let digitalTwinsModal: any;

  // State for search and debounce
  let search = $state('');
  let debouncedSearch = $state('');
  let searchTimeout: ReturnType<typeof setTimeout> | null = null;

  // Pagination state
  let page = $state(1);
  let pageSize = $state(10);
  let total = $state(0);

  // Sorting state
  let sortColumn = $state('title');
  let sortDirection = $state<'asc' | 'desc'>('asc');

  let layers: Layer[] = $state([]);
  let openIndex = $state<number | null>(null);
  let summaryRefs = $state<Array<HTMLElement | null>>([]);
  let dropdownLeft = $state(0);
  let dropdownTop = $state(0);
  let digitalTwinsForLayer = $state<Array<{ id: number; name: string; title: string }>>([]);
  let selectedLayerTitle = $state('');

  function setSort(column: string) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
    page = 1;
  }

  function onSearchChange(newValue: string) {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      debouncedSearch = newValue;
      page = 1;
    }, 1000);
  }

  async function loadLayers() {
    try {
      const data = await fetchLayersPaginated(
        debouncedSearch,
        page,
        pageSize,
        sortColumn,
        sortDirection,
        isBackgroundPage
      );
      layers = data.results;
      total = data.total;
    } catch (err) {
      layers = [];
      total = 0;
    }
  }

  $effect(() => {
    loadLayers();
  });

  function gotoPage(p: number) {
    if (p < 1 || p > totalPages()) return;
    page = p;
  }

  function totalPages() {
    return Math.max(1, Math.ceil(total / pageSize));
  }

  function handleOpenModal(layer: Layer) {
    modalComponent.showModal(layer);
  }

  function truncate(str: string, length = 30) {
    return str.length > length ? str.slice(0, length) + '…' : str;
  }


  function handleUpdated(event: CustomEvent<Layer>) {
    loadLayers();
  }

  async function handleDelete(layerId: number) {
    if (confirm('Weet je zeker dat je deze layer wilt verwijderen?')) {
      try {
        await deleteLayer(layerId);
        await loadLayers();
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

  async function showLayerUsageModal(layerId: number) {
    selectedLayerTitle = layers.find((l) => l.id === layerId)?.title || '';
    digitalTwinsForLayer = await fetchDigitalTwinsForLayer(layerId);
    digitalTwinsModal.showModal();
  }
</script>

<LayerModal bind:this={modalComponent} on:updated={handleUpdated} />
<ShowLayerUsageModal
  bind:this={digitalTwinsModal}
  {digitalTwinsForLayer}
  {selectedLayerTitle}
/>

<TableControls
  {search}
  onSearch={onSearchChange}
  {page}
  totalPages={totalPages()}
  {pageSize}
  onPageChange={gotoPage}
  onPageSizeChange={(size) => { pageSize = size; page = 1; }}
/>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <SortableTableHeader
              column="title"
              label="Titel"
              {sortColumn}
              {sortDirection}
              {setSort}
            />
            <SortableTableHeader
              column="type"
              label="Type"
              {sortColumn}
              {sortDirection}
              {setSort}
            />
            <SortableTableHeader
              column="url"
              label="Url"
              {sortColumn}
              {sortDirection}
              {setSort}
            />
            <SortableTableHeader
              column="featureName"
              label="Feature Name"
              {sortColumn}
              {sortDirection}
              {setSort}
            />
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
                          <img src="/icons/settings.svg" alt="Settings" class="h-4 w-4" />
                          Bewerken
                        </button>
                      </li>
                      <li>
                        <button onclick={() => showLayerUsageModal(layer.id)} class="flex items-center gap-2">
                          <img src="/icons/link.svg" alt="Digital Twins" class="h-4 w-4" />
                          Gebruikt door Digital Twins
                        </button>
                      </li>
                      <li>
                        <button onclick={() => { handleDelete(layer.id); openIndex = null; }} class="flex items-center gap-2 text-error">
                          <img src="/icons/trash-2.svg" alt="Settings" class="h-4 w-4" />
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
