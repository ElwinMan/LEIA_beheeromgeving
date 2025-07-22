<script lang="ts">
  import { tick } from 'svelte';
  import { portal } from 'svelte-portal';

  let { digitalTwins = [] } = $props();

  let openIndex = $state<number | null>(null);
  let summaryRefs = $state<Array<HTMLElement | null>>([]);
  let dropdownLeft = $state(0);
  let dropdownTop = $state(0);

  // Sorting state
  let sortColumn = $state('name');
  let sortDirection = $state<'asc' | 'desc'>('asc');

  function setSort(column: string) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
  }

  function getSortedTwins() {
    return [...digitalTwins].sort((a, b) => {
      let aValue = a[sortColumn];
      let bValue = b[sortColumn];
      if (aValue == null) aValue = '';
      if (bValue == null) bValue = '';
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }
      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
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

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 sticky left-0 z-10 font-bold cursor-pointer" onclick={() => setSort('name')}>
              Digital Twin
              {#if sortColumn === 'name'}
                {#if sortDirection === 'asc'}
                  <img src="/icons/chevron-up.svg" alt="Sorteren oplopend" class="inline w-4 h-4" />
                {:else}
                  <img src="/icons/chevron-down.svg" alt="Sorteren aflopend" class="inline w-4 h-4" />
                {/if}
              {:else}
                <img src="/icons/chevrons-up-down.svg" alt="Niet gesorteerd" class="inline w-4 h-4 opacity-50" />
              {/if}
            </th>
            <th class="bg-base-200 font-bold cursor-pointer" onclick={() => setSort('subtitle')}>
              Subtitle
              {#if sortColumn === 'subtitle'}
                {#if sortDirection === 'asc'}
                  <img src="/icons/chevron-up.svg" alt="Sorteren oplopend" class="inline w-4 h-4" />
                {:else}
                  <img src="/icons/chevron-down.svg" alt="Sorteren aflopend" class="inline w-4 h-4" />
                {/if}
              {:else}
                <img src="/icons/chevrons-up-down.svg" alt="Niet gesorteerd" class="inline w-4 h-4 opacity-50" />
              {/if}
            </th>
            <th class="bg-base-200 font-bold cursor-pointer" onclick={() => setSort('owner')}>
              Eigenaar
              {#if sortColumn === 'owner'}
                {#if sortDirection === 'asc'}
                  <img src="/icons/chevron-up.svg" alt="Sorteren oplopend" class="inline w-4 h-4" />
                {:else}
                  <img src="/icons/chevron-down.svg" alt="Sorteren aflopend" class="inline w-4 h-4" />
                {/if}
              {:else}
                <img src="/icons/chevrons-up-down.svg" alt="Niet gesorteerd" class="inline w-4 h-4 opacity-50" />
              {/if}
            </th>
            <th class="bg-base-200 font-bold cursor-pointer" onclick={() => setSort('private')}>
              Lijstweergaven
              {#if sortColumn === 'private'}
                {#if sortDirection === 'asc'}
                  <img src="/icons/chevron-up.svg" alt="Sorteren oplopend" class="inline w-4 h-4" />
                {:else}
                  <img src="/icons/chevron-down.svg" alt="Sorteren aflopend" class="inline w-4 h-4" />
                {/if}
              {:else}
                <img src="/icons/chevrons-up-down.svg" alt="Niet gesorteerd" class="inline w-4 h-4 opacity-50" />
              {/if}
            </th>
            <th class="bg-base-200 font-bold cursor-pointer" onclick={() => setSort('last_updated')}>
              Gewijzigd
              {#if sortColumn === 'last_updated'}
                {#if sortDirection === 'asc'}
                  <img src="/icons/chevron-up.svg" alt="Sorteren oplopend" class="inline w-4 h-4" />
                {:else}
                  <img src="/icons/chevron-down.svg" alt="Sorteren aflopend" class="inline w-4 h-4" />
                {/if}
              {:else}
                <img src="/icons/chevrons-up-down.svg" alt="Niet gesorteerd" class="inline w-4 h-4 opacity-50" />
              {/if}
            </th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each getSortedTwins() as twin, idx}
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
                        <a
                          href={`https://virtueel.zeeland.nl/${twin.name}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          class="flex items-center gap-2"
                          onclick={() => openIndex = null}
                        >
                          <img src="/icons/external-link.svg" alt="Open" class="h-4 w-4" />
                          Bekijk kaart
                        </a>
                      </li>
                      <li>
                        <a
                          href={`/digital-twins/${twin.id}`}
                          class="flex items-center gap-2"
                          onclick={() => openIndex = null}
                        >
                          <img src="/icons/settings.svg" alt="Settings" class="h-4 w-4" />
                          Digital Twin Configuratie
                        </a>
                      </li>
                    </ul>
                  {/if}
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>

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
