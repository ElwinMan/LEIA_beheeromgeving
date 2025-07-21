<script lang="ts">
  import type { Tool } from '$lib/types/tool';
  import UpdateToolModal from '$lib/components/modals/UpdateToolModal.svelte';
  import { deleteTool } from '$lib/api';

  export let tools: Tool[] = [];

  let modalComponent: any;

  function handleOpenModal(tool: Tool) {
    modalComponent.showModal(tool);
  }

  async function handleDelete(toolId: number) {
    if (confirm('Weet je zeker dat je deze tool wilt verwijderen?')) {
      try {
        await deleteTool(String(toolId));
        tools = tools.filter(t => t.id !== toolId);
      } catch (err) {
        alert('Verwijderen mislukt. Controleer de server.');
        console.error(err);
      }
    }
  }

  function handleUpdated(event: CustomEvent<Tool>) {
    const updatedTool = event.detail;
    const idx = tools.findIndex(t => t.id === updatedTool.id);
    if (idx > -1) {
      tools[idx] = updatedTool;
      tools = [...tools];
    }
  }
</script>

<UpdateToolModal bind:this={modalComponent} on:updated={handleUpdated} />

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 sticky w-full font-bold">Name</th>
            <th class="bg-base-200 pr-10 text-right font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each tools as tool}
            <tr class="hover">
              <td class="w-full text-sm font-bold">{tool.name || '-'}</td>
              <td class="text-sm">
                <details class="dropdown dropdown-end text-right">
                  <summary class="btn btn-sm btn-ghost">
                    Opties
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </summary>
                  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
                    <li>
                      <button on:click={() => handleOpenModal(tool)} class="flex items-center gap-2">
                        <img src="/icons/settings.svg" alt="Settings" class="h-4 w-4" />
                        Bewerken
                      </button>
                    </li>
                    <li>
                      <button class="text-error" on:click={() => handleDelete(tool.id)}>
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
      <div class="h-32"></div>
      {#if tools.length === 0}
        <div class="py-12 text-center">
          <img src="/icons/database.svg" alt="No tools" class="mx-auto h-12 w-12 opacity-50" />
          <h3 class="mt-2 text-lg font-medium">Geen tools</h3>
          <p class="mt-1 opacity-70">Er zijn nog geen tools beschikbaar.</p>
        </div>
      {/if}
    </div>
  </div>
</div>
