<script lang="ts">
  let { digitalTwins = [] } = $props();
</script>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 sticky left-0 z-10 font-bold">Digital Twin</th>
            <th class="bg-base-200 font-bold">Subtitle</th>
            <th class="bg-base-200 font-bold">Eigenaar</th>
            <th class="bg-base-200 font-bold">Lijstweergaven</th>
            <th class="bg-base-200 font-bold">Gewijzigd</th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each digitalTwins as twin}
            <tr class="hover">
              <td class="sticky left-0 z-10">
                <div>
                  <div class="text-base font-bold">{twin.name}</div>
                  <div class="text-sm opacity-75">{twin.title}</div>
                </div>
              </td>
              <td class="text-sm">{twin.subtitle || '-'}</td>
              <td class="text-sm">{twin.owner || '-'}</td>
              <td class="text-sm">{twin.private || '-'}</td>
              <td class="text-sm">{twin.last_updated || '-'}</td>
              <td>
                <details class="dropdown dropdown-end">
                  <summary class="btn btn-sm btn-ghost">
                    Opties
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </summary>
                  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
                    <li>
                      <a
                        href={`https://virtueel.zeeland.nl/${twin.name}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        class="flex items-center gap-2"
                      >
                        <img src="/icons/external-link.svg" alt="Open" class="h-4 w-4" />
                        Bekijk kaart
                      </a>
                    </li>
                    <li>
                      <a href={`/digital-twins/${twin.id}`} class="flex items-center gap-2">
                        <img src="/icons/settings.svg" alt="Settings" class="h-4 w-4" />
                        Digital Twin Configuratie
                      </a>
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

      {#if digitalTwins.length === 0}
        <div class="py-12 text-center">
          <img src="/icons/database.svg" alt="Geen digital twins" class="mx-auto h-12 w-12 opacity-50" />
          <h3 class="mt-2 text-lg font-medium">Geen digital twins</h3>
          <p class="mt-1 opacity-70">Er zijn nog geen digital twins beschikbaar.</p>
        </div>
      {/if}
    </div>
  </div>
</div>
