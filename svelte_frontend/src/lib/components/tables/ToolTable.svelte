<script lang="ts">
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
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </summary>
                  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
                    <li>
                      <a href={`/tools/${tool.id}`} class="flex items-center gap-2">
                        <img src="/icons/settings.svg" alt="Settings" class="h-4 w-4" />
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

      <!-- Add padding at the bottom for dropdown space -->
      <!-- Temp fix till dropdown fix for absolute position -->
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
