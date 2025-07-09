<script lang="ts">
  import { Settings, Database } from 'lucide-svelte';

  let { tools = [] } = $props();
</script>

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
              <td>
                <details class="dropdown dropdown-end text-right">
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
                      <a href={`/tools/${tool.id}`} class="flex items-center gap-2">
                        <Settings class="h-4 w-4" />
                        Configureer tool
                      </a>
                    </li>
                    <li>
                      <a href={`/tools/${tool.id}/count`}> Tool gebruik overzicht </a>
                    </li>
                  </ul>
                </details>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>

      <!-- Extra ruimte voor dropdowns -->
      <div class="h-32"></div>

      {#if tools.length === 0}
        <div class="py-12 text-center">
          <Database class="mx-auto h-12 w-12 opacity-50" />
          <h3 class="mt-2 text-lg font-medium">Geen tools</h3>
          <p class="mt-1 opacity-70">Er zijn nog geen tools beschikbaar.</p>
        </div>
      {/if}
    </div>
  </div>
</div>
