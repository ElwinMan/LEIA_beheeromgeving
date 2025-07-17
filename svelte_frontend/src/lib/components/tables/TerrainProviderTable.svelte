<script lang="ts">
  import type { TerrainProvider } from "$lib/types/tool";
  import UpdateTerrainProviderModal from "$lib/components/modals/UpdateTerrainProviderModal.svelte";
  import { deleteTerrainProvider } from "$lib/api";

  export let terrain_providers: TerrainProvider[] = [];

  let modalComponent: any;

  function handleOpenModal(tp: TerrainProvider) {
    modalComponent.showModal(tp);
  }

  async function handleDelete(tpId: number) {
    if (confirm('Weet je zeker dat je deze terrain provider wilt verwijderen?')) {
      try {
        await deleteTerrainProvider(String(tpId));
        terrain_providers = terrain_providers.filter(tp => tp.id !== tpId);
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
          {#each terrain_providers as terrain_provider}
            <tr>
              <td>{terrain_provider.title}</td>
              <td>{terrain_provider.url}</td>
              <td>{terrain_provider.vertexNormals ? 'Ja' : 'Nee'}</td>
              <td class="relative">
                <details class="dropdown dropdown-end">
                  <summary class="btn btn-sm btn-ghost">
                    Opties
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </summary>
                  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-40 p-2 shadow">
                    <li>
                      <button on:click={() => handleOpenModal(terrain_provider)} class="flex items-center gap-2">
                        Bewerken
                      </button>
                    </li>
                    <li>
                      <button class="text-error" on:click={() => handleDelete(terrain_provider.id)}>
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

      {#if terrain_providers.length === 0}
        <div class="py-12 text-center opacity-70">Geen terrain providers gevonden.</div>
      {/if}
    </div>
  </div>
</div>