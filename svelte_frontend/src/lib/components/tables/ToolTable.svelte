<script lang="ts">
  import type { Tool } from '$lib/types/tool';
  import UpdateToolModal from '$lib/components/modals/UpdateToolModal.svelte';
  import { deleteTool } from '$lib/api';
  import { createEventDispatcher } from 'svelte';
  import { portal } from 'svelte-portal';
  import { tick } from 'svelte';

  const dispatch = createEventDispatcher<{ updated: void }>();

  let { tools = [] } = $props();

  let modalComponent: any;

  let openIndex = $state<number | null>(null);
  let summaryRefs = $state<Array<HTMLElement | null>>([]);
  let dropdownLeft = $state(0);
  let dropdownTop = $state(0);

  function handleOpenModal(tool: Tool) {
    modalComponent.showModal(tool);
  }

  async function handleDelete(toolId: number) {
    if (confirm('Weet je zeker dat je deze tool wilt verwijderen?')) {
      try {
        await deleteTool(String(toolId));
        tools = tools.filter(t => t.id !== toolId);
        dispatch('updated');
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
          {#each tools as tool, idx}
            <tr class="hover">
              <td class="w-full text-sm font-bold">{tool.name || '-'}</td>
              <td class="text-sm">
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
                        <button onclick={() => { handleOpenModal(tool); openIndex = null; }} class="flex items-center gap-2">
                          <img src="/icons/settings.svg" alt="Settings" class="h-4 w-4" />
                          Bewerken
                        </button>
                      </li>
                      <li>
                        <button class="text-error" onclick={() => { handleDelete(tool.id); openIndex = null; }}>
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
