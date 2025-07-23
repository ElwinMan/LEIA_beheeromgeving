<script lang="ts">
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import { tick } from 'svelte';
  import { portal } from 'svelte-portal';

  let { digitalTwins = [] }: { digitalTwins: DigitalTwin[] } = $props();

  let openIndex = $state<number | null>(null);
  let summaryRefs = $state<Array<HTMLElement | null>>([]);
  let dropdownLeft = $state(0);
  let dropdownTop = $state(0);

  // Sorting state
  let sortColumn = $state('last_updated');
  let sortDirection = $state<'asc' | 'desc'>('desc');

  // Pagination state
  let page = $state(1);
  let pageSize = $state(10);

  // Search state
  let search = $state('');
  let debouncedSearch = $state('');
  let searchTimeout: ReturnType<typeof setTimeout> | null = null;

  // Watch for changes to `search` using a manual function
  function onSearchChange(newValue: string) {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      debouncedSearch = newValue;
      page = 1;
    }, 1000);
  }

  type SortableTwinKey = 'name' | 'subtitle' | 'owner' | 'private' | 'last_updated';

  function setSort(column: string) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
  }

  function getSortedTwins() {
    let filtered = digitalTwins;
    if (debouncedSearch.trim() !== '') {
      const s = debouncedSearch.trim().toLowerCase();
      filtered = digitalTwins.filter(twin =>
        (twin.name && twin.name.toLowerCase().includes(s)) ||
        (twin.subtitle && twin.subtitle.toLowerCase().includes(s)) ||
        (twin.owner && twin.owner.toLowerCase().includes(s)) ||
        (twin.title && twin.title.toLowerCase().includes(s))
      );
    }
    return [...filtered].sort((a, b) => {
      const col = sortColumn as SortableTwinKey;
      let aValue = a[col];
      let bValue = b[col];
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

  const totalPages = $derived(() => Math.max(1, Math.ceil(getSortedTwins().length / pageSize)));
  const paginatedTwins = $derived(() =>
    getSortedTwins().slice((page - 1) * pageSize, page * pageSize)
  );

  function gotoPage(p: number) {
    if (p < 1 || p > totalPages()) return;
    page = p;
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
        dropdownLeft = rect.right - 208 + window.scrollX; // 208px for w-52
        dropdownTop = rect.bottom + window.scrollY;
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
      <div class="flex items-center gap-2 mb-0 p-4 bg-base-300 rounded">
        <input
          type="text"
          class="input input-bordered w-full max-w-xs"
          placeholder="Zoek digital twin..."
          bind:value={search}
          oninput={() => onSearchChange(search)}
        />
      </div>

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
          {#each paginatedTwins() as twin, idx}
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

      <!-- Pagination controls -->
      <div class="flex justify-between items-center mt-4 p-6 bg-base-200 shadow">
        <div>
          Pagina {page} van {totalPages()}
        </div>
        <div>
          <div class="join">
            <button class="join-item btn btn-md" onclick={() => gotoPage(page - 1)} disabled={page === 1}>«</button>
            {#if totalPages() <= 7}
              {#each Array(totalPages()) as _, i}
                <button
                  class="join-item btn btn-md {page === i + 1 ? 'btn-active btn-primary' : ''}"
                  onclick={() => gotoPage(i + 1)}
                >{i + 1}</button>
              {/each}
            {:else}
              <button
                class="join-item btn btn-md {page === 1 ? 'btn-active btn-primary' : ''}"
                onclick={() => gotoPage(1)}
              >1</button>
              {#if page > 4}
                <button class="join-item btn btn-md btn-disabled">...</button>
              {/if}
              {#each [page - 1, page, page + 1] as p (p)}
                {#if p > 1 && p < totalPages()}
                  <button
                    class="join-item btn btn-md {page === p ? 'btn-active btn-primary' : ''}"
                    onclick={() => gotoPage(p)}
                  >{p}</button>
                {/if}
              {/each}
              {#if page < totalPages() - 3}
                <button class="join-item btn btn-md btn-disabled">...</button>
              {/if}
              <button
                class="join-item btn btn-md {page === totalPages() ? 'btn-active btn-primary' : ''}"
                onclick={() => gotoPage(totalPages())}
              >{totalPages()}</button>
            {/if}
            <button class="join-item btn btn-md" onclick={() => gotoPage(page + 1)} disabled={page === totalPages()}>»</button>
          </div>
        </div>
        <div>
          <select class="select select-mg" bind:value={pageSize} onchange={() => { page = 1; }}>
            <option value={10}>10 per pagina</option>
            <option value={20}>20 per pagina</option>
            <option value={50}>50 per pagina</option>
          </select>
        </div>
      </div>

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
