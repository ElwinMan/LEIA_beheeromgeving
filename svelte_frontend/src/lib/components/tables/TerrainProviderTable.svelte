<script lang="ts">
  import type { TerrainProvider } from "$lib/types/tool";
  import UpdateTerrainProviderModal from "$lib/components/modals/UpdateTerrainProviderModal.svelte";
  import { deleteTerrainProvider } from "$lib/api";
  import { portal } from 'svelte-portal';
  import { tick } from 'svelte';
  import { createEventDispatcher } from 'svelte';

  let { terrain_providers = [] } = $props();

  let modalComponent: any;

  let openIndex = $state<number | null>(null);
  let summaryRefs = $state<Array<HTMLElement | null>>([]);
  let dropdownLeft = $state(0);
  let dropdownTop = $state(0);

  const dispatch = createEventDispatcher<{ updated: void }>();

  function handleOpenModal(tp: TerrainProvider) {
    modalComponent.showModal(tp);
  }

  async function handleDelete(tpId: number) {
    if (confirm('Weet je zeker dat je deze terrain provider wilt verwijderen?')) {
      try {
        await deleteTerrainProvider(String(tpId));
        terrain_providers = terrain_providers.filter(tp => tp.id !== tpId);
        dispatch('updated');
      } catch (err) {
        alert('Verwijderen mislukt. Controleer de server.');
        console.error(err);
      }
    }
  }

  function handleUpdated(event: CustomEvent<TerrainProvider>) {
    const updatedTP = event.detail;
    const idx = terrain_providers.findIndex(tp => tp.id === updatedTP.id);
    if (idx > -1) {
      terrain_providers[idx] = updatedTP;
      terrain_providers = [...terrain_providers];
      dispatch('updated');
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
        dropdownLeft = rect.right - 160; // 160px for w-40
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

<UpdateTerrainProviderModal bind:this={modalComponent} on:updated={handleUpdated} />

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 font-bold">Title</th>
            <th class="bg-base-200 font-bold">URL</th>
            <th class="bg-base-200 font-bold">Vertex Normals</th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each terrain_providers as terrain_provider, idx}
            <tr>
              <td class="text-sm font-bold">{terrain_provider.title || '-'}</td>
              <td class="text-sm">{terrain_provider.url || '-'}</td>
              <td class="text-sm">{terrain_provider.vertexNormals ? 'Ja' : 'Nee'}</td>
              <td class="text-sm relative">
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
                      class="dropdown-content menu bg-base-100 rounded-box z-[1000] w-40 p-2 shadow"
                      style="position: absolute; left: {dropdownLeft}px; top: {dropdownTop}px;"
                    >
                      <li>
                        <button onclick={() => { handleOpenModal(terrain_provider); openIndex = null; }} class="flex items-center gap-2">
                          Bewerken
                        </button>
                      </li>
                      <li>
                        <button class="text-error" onclick={() => { handleDelete(terrain_provider.id); openIndex = null; }}>
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

      {#if terrain_providers.length === 0}
        <div class="py-12 text-center opacity-70">Geen terrain providers gevonden.</div>
      {/if}
    </div>
  </div>
</div>